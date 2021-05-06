"""
Encapsulates external dependencies to retrieve hardware metadata
"""

import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from codecarbon.core.cpu import IntelPowerGadget, IntelRAPL
from codecarbon.core.gpu import get_gpu_details
from codecarbon.core.units import Power

POWER_CONSTANT = 85
CONSUMPTION_PERCENTAGE_CONSTANT = 0.5

logger = logging.getLogger("codecarbon")


@dataclass
class BaseHardware(ABC):
    @abstractmethod
    def total_power(self) -> Power:
        pass


@dataclass
class GPU(BaseHardware):
    num_gpus: int
    gpu_ids: Optional[List]

    def __repr__(self) -> str:
        return super().__repr__() + " ({})".format(
            ", ".join([d["name"] for d in get_gpu_details()])
        )

    def _get_power_for_gpus(self, gpu_ids: Iterable[int]) -> Power:
        """
        Get total power consumed by specific GPUs identified by `gpu_ids`
        :param gpu_ids:
        :return: power in kW
        """
        all_gpu_details: List[Dict] = get_gpu_details()
        return Power.from_milli_watts(
            sum(
                [
                    gpu_details["power_usage"]
                    for idx, gpu_details in enumerate(all_gpu_details)
                    if idx in gpu_ids
                ]
            )
        )

    def total_power(self) -> Power:
        if self.gpu_ids is not None:
            gpu_ids = self.gpu_ids
            assert set(gpu_ids).issubset(
                set(range(self.num_gpus))
            ), f"CODECARBON Unknown GPU ids {gpu_ids}"
        else:
            gpu_ids = set(range(self.num_gpus))

        gpu_power = self._get_power_for_gpus(gpu_ids=gpu_ids)
        logger.info(f"CODECARBON GPU Power Consumption : {gpu_power}")
        return gpu_power

    @classmethod
    def from_utils(cls, gpu_ids: Optional[List] = None) -> "GPU":
        return cls(num_gpus=len(get_gpu_details()), gpu_ids=gpu_ids)


@dataclass
class CPU(BaseHardware):
    def __init__(self, output_dir: str, mode: str, tdp: int):
        self._output_dir = output_dir
        self._mode = mode
        self._tdp = tdp
        if self._mode == "intel_power_gadget":
            self._intel_interface = IntelPowerGadget(self._output_dir)
        elif self._mode == "intel_rapl":
            self._intel_interface = IntelRAPL()

    def _get_power_from_cpus(self) -> Power:
        """
        Get CPU power from Intel Power Gadget
        :return: power in kW
        """
        if self._mode == "constant":
            power = self._tdp * CONSUMPTION_PERCENTAGE_CONSTANT
            return Power.from_watts(power)

        all_cpu_details: Dict = self._intel_interface.get_cpu_details()

        power = 0
        for metric, value in all_cpu_details.items():
            if re.match(r"^Processor Power_\d+\(Watt\)$", metric):
                power += value
        return Power.from_watts(power)

    def total_power(self) -> Power:
        cpu_power = self._get_power_from_cpus()
        logger.info(f"CODECARBON CPU Power Consumption : {cpu_power}")
        return cpu_power

    @classmethod
    def from_utils(
        cls, output_dir: str, mode: str, tdp: Optional[int] = POWER_CONSTANT
    ) -> "CPU":
        return cls(output_dir=output_dir, mode=mode, tdp=tdp)
