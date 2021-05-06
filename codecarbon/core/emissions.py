"""
Provides functionality to compute emissions for cloud & private infra based on impact & energy Usage package
https://github.com/mlco2/impact
https://github.com/responsibleproblemsolving/energy-usage
"""

import logging
from typing import Dict, Optional

import pandas as pd

from codecarbon.core import co2_signal
from codecarbon.core.units import EmissionsPerKwh, Energy
from codecarbon.external.geography import CloudMetadata, GeoMetadata
from codecarbon.input import DataSource, DataSourceException

logger = logging.getLogger("codecarbon")


class Emissions:
    def __init__(
        self, data_source: DataSource, co2_signal_api_token: Optional[str] = None
    ):
        self._data_source = data_source
        self._co2_signal_api_token = co2_signal_api_token

    def get_cloud_emissions(self, energy: Energy, cloud: CloudMetadata) -> float:
        """
        Computes emissions for cloud infra
        :param energy: Mean power consumption of the process (kWh)
        :param cloud: Region of compute
        :return: CO2 emissions in kg
        """

        df: pd.DataFrame = self._data_source.get_cloud_emissions_data()

        emissions_per_kwh: EmissionsPerKwh = EmissionsPerKwh.from_g_per_kwh(
            df.loc[(df["provider"] == cloud.provider) & (df["region"] == cloud.region)][
                "impact"
            ].item()
        )

        return emissions_per_kwh.kgs_per_kwh * energy.kwh  # kgs

    def get_cloud_country_name(self, cloud: CloudMetadata) -> str:
        """
        Returns the Country Name where the cloud region is located
        """
        df: pd.DataFrame = self._data_source.get_cloud_emissions_data()
        return df.loc[
            (df["provider"] == cloud.provider) & (df["region"] == cloud.region)
        ]["countryName"].item()

    def get_cloud_country_iso_code(self, cloud: CloudMetadata) -> str:
        """
        Returns the Country ISO Code where the cloud region is located
        """
        df: pd.DataFrame = self._data_source.get_cloud_emissions_data()
        return df.loc[
            (df["provider"] == cloud.provider) & (df["region"] == cloud.region)
        ]["countryIsoCode"].item()

    def get_cloud_geo_region(self, cloud: CloudMetadata) -> str:
        """
        Returns the State/City where the cloud region is located
        """
        df: pd.DataFrame = self._data_source.get_cloud_emissions_data()
        state = df.loc[
            (df["provider"] == cloud.provider) & (df["region"] == cloud.region)
        ]["state"].item()
        if state is not None:
            return state
        city = df.loc[
            (df["provider"] == cloud.provider) & (df["region"] == cloud.region)
        ]["city"].item()
        return city

    def get_private_infra_emissions(self, energy: Energy, geo: GeoMetadata) -> float:
        """
        Computes emissions for private infra
        :param energy: Mean power consumption of the process (kWh)
        :param geo: Country and region metadata
        :return: CO2 emissions in kg
        """
        if self._co2_signal_api_token:
            try:
                return co2_signal.get_emissions(energy, geo, self._co2_signal_api_token)
            except Exception as e:
                logger.error(e)

        compute_with_regional_data: bool = (geo.region is not None) and (
            geo.country_iso_code.upper() in ["USA", "CAN"]
        )

        if compute_with_regional_data:
            try:
                return self.get_region_emissions(energy, geo)
            except Exception as e:
                logger.error(e)
                logger.warning(
                    "CODECARBON : Regional emissions retrieval failed. Falling back on country emissions."
                )
        return self.get_country_emissions(energy, geo)

    def get_region_emissions(self, energy: Energy, geo: GeoMetadata) -> float:
        """
        Computes emissions for a region on private infra.
        Given an quantity of power consumed, use regional data
         on emissions per unit power consumed or the mix of energy sources.
        https://github.com/responsibleproblemsolving/energy-usage#calculating-co2-emissions
        :param energy: Mean power consumption of the process (kWh)
        :param geo: Country and region metadata.
        :return: CO2 emissions in kg
        """
        try:
            country_emissions_data = self._data_source.get_country_emissions_data(
                geo.country_iso_code.lower()
            )

            if geo.region not in country_emissions_data:
                # TODO: Deal with missing data, default to something
                raise ValueError(
                    f"Region: {geo.region} not found for Country with ISO CODE : {geo.country_iso_code}"
                )

            emissions_per_kwh: EmissionsPerKwh = EmissionsPerKwh.from_lbs_per_mwh(
                country_emissions_data[geo.region]["emissions"]
            )
        except DataSourceException:  # This country has regional data at the energy mix level, not the emissions level
            country_energy_mix_data = self._data_source.get_country_energy_mix_data(
                geo.country_iso_code.lower()
            )
            region_energy_mix_data = country_energy_mix_data[geo.region]
            emissions_per_kwh: EmissionsPerKwh = self._energy_mix_to_emissions_rate(
                region_energy_mix_data
            )

        return emissions_per_kwh.kgs_per_kwh * energy.kwh  # kgs

    def get_country_emissions(self, energy: Energy, geo: GeoMetadata) -> float:
        """
        Computes emissions for a country on private infra,
        given a quantity of power consumed by
        using data for the mix of energy sources of that country.
        :param energy: Mean power consumption of the process (kWh)
        :param geo: Country and region metadata
        :return: CO2 emissions in kg
        """
        energy_mix = self._data_source.get_global_energy_mix_data()

        if geo.country_iso_code not in energy_mix:
            # TODO: Deal with missing data, default to something
            raise Exception()

        country_energy_mix: Dict = energy_mix[geo.country_iso_code]
        emissions_per_kwh = self._energy_mix_to_emissions_rate(country_energy_mix)
        return emissions_per_kwh.kgs_per_kwh * energy.kwh  # kgs

    @staticmethod
    def _energy_mix_to_emissions_rate(energy_mix: Dict) -> EmissionsPerKwh:
        """
        Convert a mix of energy sources into emissions per kWh
        https://github.com/responsibleproblemsolving/energy-usage#calculating-co2-emissions
        :param energy_mix: A dictionary that breaks down the energy produced into sources, with a total value.
            Format will vary, but must have keys for "coal", "petroleum" and "naturalGas" and "total"
        :return: an EmissionsPerKwh object representing the average emissions rate
        """
        # source: https://github.com/responsibleproblemsolving/energy-usage#conversion-to-co2
        emissions_by_source: Dict[str, EmissionsPerKwh] = {
            "coal": EmissionsPerKwh.from_kgs_per_kwh(0.995725971),
            "petroleum": EmissionsPerKwh.from_kgs_per_kwh(0.8166885263),
            "naturalGas": EmissionsPerKwh.from_kgs_per_kwh(0.7438415916),
        }

        emissions_percentage: Dict[str, float] = {}
        for energy_type in energy_mix.keys():
            if energy_type not in ["total", "isoCode", "countryName"]:
                emissions_percentage[energy_type] = (
                    energy_mix[energy_type] / energy_mix["total"]
                )

        #  Weighted sum of emissions by % of contributions
        # `emissions_percentage`: coal: 0.5, petroleum: 0.25, naturalGas: 0.25
        # `emission_value`: coal: 0.995725971, petroleum: 0.8166885263, naturalGas: 0.7438415916
        # `emissions_per_kwh`: (0.5 * 0.995725971) + (0.25 * 0.8166885263) * (0.25 * 0.7438415916)
        #  >> 0.5358309 kg/kwh

        emissions_per_kwh = EmissionsPerKwh.from_kgs_per_kwh(
            sum(
                [
                    emissions_percentage[source]
                    * value.kgs_per_kwh  # % (0.x)  # kgs / kwh
                    for source, value in emissions_by_source.items()
                ]
            )
        )

        return emissions_per_kwh
