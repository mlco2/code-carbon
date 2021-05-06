"""
Contains implementations of the Public facing API: EmissionsTracker,
OfflineEmissionsTracker and @track_emissions
"""

import logging
import os
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from typing import Callable, List, Optional, Union

from apscheduler.schedulers.background import BackgroundScheduler

from codecarbon.core import cpu, gpu
from codecarbon.core.config import get_hierarchical_config, parse_gpu_ids
from codecarbon.core.emissions import Emissions
from codecarbon.core.units import Energy, Time
from codecarbon.core.util import suppress, set_log_level
from codecarbon.external.geography import CloudMetadata, GeoMetadata
from codecarbon.external.hardware import CPU, GPU
from codecarbon.input import DataSource
from codecarbon.output import BaseOutput, EmissionsData, FileOutput, HTTPOutput

logging.getLogger("codecarbon").setLevel(
    level=os.environ.get("CODECARBON_LOGLEVEL", "WARN")
)
logger = logging.getLogger("codecarbon")

# /!\ Warning: current implementation prevents the user from setting any value to None
# from the script call
# Imagine:
#   1/ emissions_endpoint=localhost:8000 in ~/.codecarbon.config
#   2/ Inside the script, the user cannot disable emissions_endpoint with
#   EmissionsTracker(emissions_endpoint=None) since the config logic will use the one in
#   the config file.
#
# Alternative: EmissionsTracker(emissions_endpoint=False) would work
# TODO: document this
#
# To fix this, a complex move would be to have default values set to the sentinel:
# _sentinel = object()
# see: https://stackoverflow.com/questions/67202314/
#      python-distinguish-default-argument-and-argument-provided-with-default-value


class BaseEmissionsTracker(ABC):
    """
    Primary abstraction with Emissions Tracking functionality.
    Has two abstract methods, `_get_geo_metadata` and `_get_cloud_metadata`
    that are implemented by two concrete classes `OfflineCarbonTracker`
    and `CarbonTracker.`
    """

    def __init__(
        self,
        project_name: Optional[str] = None,
        measure_power_secs: Optional[int] = None,
        output_dir: Optional[str] = None,
        save_to_file: Optional[bool] = None,
        gpu_ids: Optional[List] = None,
        emissions_endpoint: Optional[str] = None,
        co2_signal_api_token: Optional[str] = None,
        log_level: Optional[Union[int, str]] = None,
    ):
        """
        :param project_name: Project name for current experiment run, default name
                             as "codecarbon"
        :param measure_power_secs: Interval (in seconds) to measure hardware power
                                   usage, defaults to 15
        :param output_dir: Directory path to which the experiment details are logged
                           in a CSV file called `emissions.csv`, defaults to current
                           directory
        :param save_to_file: Indicates if the emission artifacts should be logged to a
                             file, defaults to True
        :param gpu_ids: User-specified known gpu ids to track, defaults to None
        :param emissions_endpoint: Optional URL of http endpoint for sending emissions
                                   data
        :param co2_signal_api_token: API token for co2signal.com (requires sign-up for
                                     free beta)
        :param log_level: Global codecarbon log level. Accepts one of:
                            {"debug", "info", "warning", "error", "critical"}.
                          Defaults to "info".
        """
        conf = get_hierarchical_config()

        self._log_level = (
            log_level if log_level is not None else conf.get("log_level", "info")
        )
        set_log_level(self._log_level)

        self._project_name: str = (
            project_name
            if project_name is not None
            else conf.get("project_name", "codecarbon")
        )

        self._measure_power_secs: int = (
            measure_power_secs
            if measure_power_secs is not None
            else conf.getint("measure_power_secs", 15)
        )

        self._output_dir: str = (
            output_dir if output_dir is not None else conf.get("output_dir", ".")
        )

        self._emissions_endpoint = (
            emissions_endpoint
            if emissions_endpoint is not None
            else conf.get("emissions_endpoint", None)
        )

        self._co2_signal_api_token = (
            co2_signal_api_token
            if co2_signal_api_token is not None
            else conf.get("co2_signal_api_token", None)
        )

        self._save_to_file = (
            save_to_file
            if save_to_file is not None
            else conf.getboolean("save_to_file", True)
        )

        self._start_time: Optional[float] = None
        self._last_measured_time: float = time.time()
        self._total_energy: Energy = Energy.from_energy(kwh=0)
        self._scheduler = BackgroundScheduler()
        self._hardware = list()

        if self._save_to_file == "False":
            self._save_to_file = False

        self._gpu_ids = gpu_ids if gpu_ids is not None else conf.get("gpu_ids", None)
        if isinstance(self._gpu_ids, str):
            self._gpu_ids = parse_gpu_ids(self._gpu_ids)

        # Hardware detection
        if gpu.is_gpu_details_available():
            logger.info("CODECARBON : Tracking Nvidia GPU via pynvml")
            self._hardware.append(GPU.from_utils(self._gpu_ids))
        if cpu.is_powergadget_available():
            logger.info("CODECARBON : Tracking Intel CPU via Power Gadget")
            self._hardware.append(
                CPU.from_utils(self._output_dir, "intel_power_gadget")
            )
        elif cpu.is_rapl_available():
            logger.info("CODECARBON : Tracking Intel CPU via RAPL interface")
            self._hardware.append(CPU.from_utils(self._output_dir, "intel_rapl"))
        else:
            logger.warning(
                "CODECARBON : No CPU tracking mode found. "
                + "Falling back on CPU constant mode."
            )
            logger.info("CODECARBON : Tracking using constant")
            tdp = cpu.TDP().tdp
            if tdp:
                self._hardware.append(CPU.from_utils(self._output_dir, "constant", tdp))
            else:
                logger.warning(
                    "CODECARBON : Failed to match CPU TDP constant. "
                    + "Falling back on a global constant."
                )
                self._hardware.append(CPU.from_utils(self._output_dir, "constant"))

        # Run `self._measure_power` every `measure_power_secs` seconds in a
        # background thread
        self._scheduler.add_job(
            self._measure_power, "interval", seconds=self._measure_power_secs
        )

        self._data_source = DataSource()
        self._emissions: Emissions = Emissions(
            self._data_source, self._co2_signal_api_token
        )
        self.persistence_objs: List[BaseOutput] = list()

        if self._save_to_file:
            self.persistence_objs.append(
                FileOutput(os.path.join(self._output_dir, "emissions.csv"))
            )

        if self._emissions_endpoint:
            self.persistence_objs.append(HTTPOutput(emissions_endpoint))

    @suppress(Exception)
    def start(self) -> None:
        """
        Starts tracking the experiment.
        Currently, Nvidia GPUs are supported.
        :return: None
        """

        if self._start_time is not None:
            logger.warning("CODECARBON : Already started tracking")
            return

        self._last_measured_time = self._start_time = time.time()
        self._scheduler.start()

    @suppress(Exception)
    def stop(self) -> Optional[float]:
        """
        Stops tracking the experiment
        :return: CO2 emissions in kgs
        """
        if self._start_time is None:
            logger.error("CODECARBON : Need to first start the tracker")
            return None

        self._scheduler.shutdown()

        # Run to calculate the power used from last
        # scheduled measurement to shutdown
        self._measure_power()

        emissions_data = self._prepare_emissions_data()

        for persistence in self.persistence_objs:
            persistence.out(emissions_data)

        return emissions_data.emissions

    def _prepare_emissions_data(self) -> EmissionsData:
        cloud: CloudMetadata = self._get_cloud_metadata()
        duration: Time = Time.from_seconds(time.time() - self._start_time)

        if cloud.is_on_private_infra:
            geo: GeoMetadata = self._get_geo_metadata()
            emissions = self._emissions.get_private_infra_emissions(
                self._total_energy, geo
            )
            country_name = geo.country_name
            country_iso_code = geo.country_iso_code
            region = geo.region
            on_cloud = "N"
            cloud_provider = ""
            cloud_region = ""
        else:
            emissions = self._emissions.get_cloud_emissions(self._total_energy, cloud)
            country_name = self._emissions.get_cloud_country_name(cloud)
            country_iso_code = self._emissions.get_cloud_country_iso_code(cloud)
            region = self._emissions.get_cloud_geo_region(cloud)
            on_cloud = "Y"
            cloud_provider = cloud.provider
            cloud_region = cloud.region

        return EmissionsData(
            timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            experiment_id=str(uuid.uuid4()),
            project_name=self._project_name,
            duration=duration.seconds,
            emissions=emissions,
            energy_consumed=self._total_energy.kwh,
            country_name=country_name,
            country_iso_code=country_iso_code,
            region=region,
            on_cloud=on_cloud,
            cloud_provider=cloud_provider,
            cloud_region=cloud_region,
        )

    @abstractmethod
    def _get_geo_metadata(self) -> GeoMetadata:
        """
        :return: Metadata containing geographical info
        """
        pass

    @abstractmethod
    def _get_cloud_metadata(self) -> CloudMetadata:
        """
        :return: Metadata containing cloud info
        """
        pass

    def _measure_power(self) -> None:
        """
        A function that is periodically run by the `BackgroundScheduler`
        every `self._measure_power` seconds.
        :return: None
        """
        last_duration = time.time() - self._last_measured_time

        warning_duration = self._measure_power_secs * 3
        if last_duration > warning_duration:
            warn_msg = (
                "CODECARBON : Background scheduler didn't run for a long period"
                + " (%ds), results might be inaccurate"
            )
            logger.warning(warn_msg, last_duration)

        for hardware in self._hardware:
            self._total_energy += Energy.from_power_and_time(
                power=hardware.total_power(), time=Time.from_seconds(last_duration)
            )
            logger.info(
                "CODECARBON : Energy consumed "
                + f"{hardware.__class__.__name__} : {self._total_energy}"
            )
        self._last_measured_time = time.time()


class OfflineEmissionsTracker(BaseEmissionsTracker):
    """
    Offline implementation of the `EmissionsTracker`
    In addition to the standard arguments, the following are required.
    """

    @suppress(Exception)
    def __init__(
        self,
        *args,
        country_iso_code: Optional[str] = None,
        region: Optional[str] = None,
        cloud_provider: Optional[str] = None,
        cloud_region: Optional[str] = None,
        country_2letter_iso_code: Optional[str] = None,
        **kwargs,
    ):
        """
        :param country_iso_code: 3 letter ISO Code of the country where the
                                 experiment is being run
        :param region: The provincial region, for example, California in the US.
                       Currently, this only affects calculations for the United States
                       and Canada
        :param cloud_provider: The cloud provider specified for estimating emissions
                               intensity, defaults to None.
                               See https://github.com/mlco2/codecarbon/
                                        blob/master/codecarbon/data/cloud/impact.csv
                               for a list of cloud providers
        :param cloud_region: The region of the cloud data center, defaults to None.
                             See https://github.com/mlco2/codecarbon/
                                        blob/master/codecarbon/data/cloud/impact.csv
                             for a list of cloud regions.
        :param country_2letter_iso_code: For use with the CO2Signal emissions API.
                                         See http://api.electricitymap.org/v3/zones for
                                         a list of codes and their corresponding
                                         locations.
        """
        conf = get_hierarchical_config()
        self._cloud_provider: Optional[str] = (
            cloud_provider
            if cloud_provider is not None
            else conf.get("cloud_provider", None)
        )
        self._country_iso_code: Optional[str] = (
            country_iso_code
            if country_iso_code is not None
            else conf.get("country_iso_code", None)
        )
        self._cloud_region: Optional[str] = (
            cloud_region if cloud_region is not None else conf.get("cloud_region", None)
        )
        self._region: Optional[str] = (
            region if region is not None else conf.get("cloud_region", None)
        )
        if self._region is not None:
            assert isinstance(self._region, str)
            self._region = self._region.lower()

        if self._cloud_provider:
            if self._cloud_region is None:
                logger.error(
                    "CODECARBON : Cloud Region must be provided "
                    + " if cloud provider is set"
                )

            df = DataSource().get_cloud_emissions_data()
            if (
                len(
                    df.loc[
                        (df["provider"] == self._cloud_provider)
                        & (df["region"] == self._cloud_region)
                    ]
                )
                == 0
            ):
                logger.error(
                    "CODECARBON : Cloud Provider/Region "
                    f"{self._cloud_provider} {self._cloud_region} "
                    "not found in cloud emissions data."
                )
        if self._country_iso_code:
            try:
                self._country_name: str = DataSource().get_global_energy_mix_data()[
                    self._country_iso_code
                ]["countryName"]
            except KeyError as e:
                logger.error(
                    "CODECARBON : Does not support country"
                    + f" with ISO code {self._country_iso_code} "
                    f"Exception occurred {e}"
                )

        self.country_2letter_iso_code: Optional[str] = (
            country_2letter_iso_code
            if country_2letter_iso_code is not None
            else conf.get("country_2letter_iso_code", None)
        )
        if self.country_2letter_iso_code:
            assert isinstance(self.country_2letter_iso_code, str)
            self.country_2letter_iso_code = self.country_2letter_iso_code.upper()

        super().__init__(*args, **kwargs)

    def _get_geo_metadata(self) -> GeoMetadata:
        return GeoMetadata(
            country_iso_code=self._country_iso_code,
            country_name=self._country_name,
            region=self._region,
            country_2letter_iso_code=self.country_2letter_iso_code,
        )

    def _get_cloud_metadata(self) -> CloudMetadata:
        return CloudMetadata(provider=self._cloud_provider, region=self._cloud_region)


class EmissionsTracker(BaseEmissionsTracker):
    """
    An online emissions tracker that auto infers geographical location,
    using `geojs` API
    """

    def _get_geo_metadata(self) -> GeoMetadata:
        return GeoMetadata.from_geo_js(self._data_source.geo_js_url)

    def _get_cloud_metadata(self) -> CloudMetadata:
        return CloudMetadata.from_utils()


def track_emissions(
    fn: Callable = None,
    project_name: Optional[str] = None,
    measure_power_secs: Optional[int] = None,
    output_dir: Optional[str] = None,
    save_to_file: Optional[bool] = None,
    offline: Optional[bool] = None,
    country_iso_code: Optional[str] = None,
    region: Optional[str] = None,
    cloud_provider: Optional[str] = None,
    cloud_region: Optional[str] = None,
    gpu_ids: Optional[List] = None,
    log_level: Optional[Union[int, str]] = None,
):
    """
    Decorator that supports both `EmissionsTracker` and `OfflineEmissionsTracker`
    :param fn: Function to be decorated
    :param project_name: Project name for current experiment run,
                         default name as "codecarbon"
    :param measure_power_secs: Interval (in seconds) to measure hardware power usage,
                               defaults to 15
    :param output_dir: Directory path to which the experiment details are logged
                       in a CSV file called `emissions.csv`, defaults to current
                       directory
    :param save_to_file: Indicates if the emission artifacts should be logged to a file,
                         defaults to True
    :param offline: Indicates if the tracker should be run in offline mode
    :param country_iso_code: 3 letter ISO Code of the country where the experiment is
                             being run, required if `offline=True`
    :param region: The provincial region, for example, California in the US.
                   Currently, this only affects calculations for the United States
    :param cloud_provider: The cloud provider specified for estimating emissions
                           intensity, defaults to None.
                           See https://github.com/mlco2/codecarbon/
                                            blob/master/codecarbon/data/cloud/impact.csv
                           for a list of cloud providers
    :param cloud_region: The region of the cloud data center, defaults to None.
                         See https://github.com/mlco2/codecarbon/
                                            blob/master/codecarbon/data/cloud/impact.csv
                         for a list of cloud regions
    :param gpu_ids: User-specified known gpu ids to track, defaults to None
    :param log_level: Global codecarbon log level. Accepts one of:
                        {"debug", "info", "warning", "error", "critical"}.
                      Defaults to "info".

    :return: The decorated function
    """

    def _decorate(fn: Callable):
        @wraps(fn)
        def wrapped_fn(*args, **kwargs):
            if offline:
                if country_iso_code is None and cloud_provider is None:
                    raise Exception(
                        "CODECARBON : Needs ISO Code of the Country for Offline mode"
                    )
                tracker = OfflineEmissionsTracker(
                    project_name=project_name,
                    measure_power_secs=measure_power_secs,
                    output_dir=output_dir,
                    save_to_file=save_to_file,
                    country_iso_code=country_iso_code,
                    region=region,
                    cloud_provider=cloud_provider,
                    cloud_region=cloud_region,
                    gpu_ids=gpu_ids,
                    log_level=log_level
                )
                tracker.start()
                fn(*args, **kwargs)
                tracker.stop()
            else:
                tracker = EmissionsTracker(
                    project_name=project_name,
                    measure_power_secs=measure_power_secs,
                    output_dir=output_dir,
                    save_to_file=save_to_file,
                    gpu_ids=gpu_ids,
                    log_level=log_level
                )
                tracker.start()
                fn(*args, **kwargs)
                tracker.stop()

        return wrapped_fn

    if fn:
        return _decorate(fn)
    return _decorate
