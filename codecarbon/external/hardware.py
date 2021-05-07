"""
Encapsulates external dependencies to retrieve hardware metadata
"""

import logging
import re
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import psutil

from codecarbon.core.cpu import IntelPowerGadget, IntelRAPL
from codecarbon.core.gpu import get_gpu_details
from codecarbon.core.units import Power

# default W value for a CPU if no model is found in the ref csv
POWER_CONSTANT = 85

#  ratio of TDP estimated to be consumed on average
CONSUMPTION_PERCENTAGE_CONSTANT = 0.5

logger = logging.getLogger(__name__)


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


@dataclass
class RAM(BaseHardware):

    # 3 watts of power for every 8GB of DDR3 or DDR4 memory
    # https://www.crucial.com/support/articles-faq-memory/how-much-power-does-memory-use
    gb_consumption = 3 / 8  # W/GB

    def __init__(self, pid: int = psutil.Process().pid, children: bool = True):
        """
        Instantiate a RAM object from a reference pid. If none is provided, will use the
        current process's. The `pid` is used to find children processes if `children`
        is True.

        Args:
            pid (int, optional): Process id (with respect to which we'll look for
                                 children). Defaults to psutil.Process().pid.
            children (int, optional): Look for children of the process when computing
                                      total RAM used. Defaults to True.
        """
        self._pid = pid
        self._children = children

    def _get_children_memories(self):
        """
        Compute the used RAM by the process's children

        Returns:
            list(int): The list of RAM values
        """
        current_process = psutil.Process(self._pid)
        children = current_process.children(recursive=True)
        return [child.memory_info().rss for child in children]

    def _read_slurm_scontrol(self):
        try:
            return subprocess.check_output(
                ["scontrol show job $SLURM_JOBID"], shell=True
            ).decode()
        except subprocess.CalledProcessError:
            return None

    def _parse_scontrol_memory(self, mem):
        nb = int(mem[:-1])
        unit = mem[-1]
        if unit == "T":
            return nb * 1024
        if unit == "G":
            return nb
        if unit == "M":
            return nb / 1024
        if unit == "K":
            return nb / (1024 ** 2)

    def _parse_scontrol(self, scontrol_str):
        lines = scontrol_str.split("\n")
        memlines = [line for line in lines if "mem=" in line]
        if not memlines:
            return
        memline = memlines[0]
        mem = memline.split("mem=")[1].split(",")[0]
        return mem

    def _get_slurm_mem_gb(self):
        scontrol_str = self._read_slurm_scontrol()
        mem = self._parse_scontrol(scontrol_str)
        mem_gb = self._parse_scontrol_memory(mem)
        return mem_gb

    @property
    def total_memory(self):
        """
        Property to compute the process's total memory usage in bytes.

        Returns:
            float: RAM usage (bytes)
        """
        children_memories = self._get_children_memories() if self._children else []
        main_memory = psutil.Process(self._pid).memory_info().rss
        memories = children_memories + [main_memory]
        return sum([m for m in memories if m] + [0])

    def total_power(self) -> Power:
        """
        Compute the Power (kw) consumed by the current process (and its children if
        `children` was True in __init__)

        Returns:
            Power: kW of power consumption, using self.gb_consumption W/GB
        """
        try:
            memory_gb = self.total_memory / (1024 ** 3)
            ram_power = Power.from_watts(memory_gb * self.gb_consumption)
            logger.info(f"CODECARBON RAM Power Consumption : {ram_power}")
        except Exception as e:
            logger.warning(f"CODECARBON could not measure RAM Power ({str(e)})")
            ram_power = Power.from_watts(0)
        finally:
            return ram_power
