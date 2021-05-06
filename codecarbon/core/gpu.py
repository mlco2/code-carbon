# -*- coding: utf-8 -*-

# Copyright (C) 2020 [COMET-ML]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
# OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
from logging import getLogger

import pynvml

logger = getLogger("codecarbon")


def to_utf8(str_or_bytes):
    if hasattr(str_or_bytes, "decode"):
        return str_or_bytes.decode("utf-8", errors="replace")

    return str_or_bytes


def get_gpu_name(handle):
    """Returns the name of the GPU device
    https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1ga5361803e044c6fdf3b08523fb6d1481
    """
    name = pynvml.nvmlDeviceGetName(handle)
    return to_utf8(name)


def get_uuid(handle):
    """Returns the globally unique GPU device UUID
    https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1g72710fb20f30f0c2725ce31579832654
    """
    uuid = pynvml.nvmlDeviceGetUUID(handle)
    return to_utf8(uuid)


def get_memory_info(handle):
    """Returns memory info in bytes
    https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1g2dfeb1db82aa1de91aa6edf941c85ca8
    """
    return pynvml.nvmlDeviceGetMemoryInfo(handle)


def get_temperature(handle):
    """Returns degrees in the Celsius scale
    https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1g92d1c5182a14dd4be7090e3c1480b121
    """
    return pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)


def get_power_usage(handle):
    """Returns power usage in milliwatts
    https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1g7ef7dff0ff14238d08a19ad7fb23fc87
    """
    return pynvml.nvmlDeviceGetPowerUsage(handle)


def get_power_limit(handle):
    """Returns max power usage in milliwatts
    https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1g263b5bf552d5ec7fcd29a088264d10ad
    """
    try:
        return pynvml.nvmlDeviceGetEnforcedPowerLimit(handle)
    except Exception:
        return None


def get_gpu_utilization(handle):
    """Returns the % of utilization of the kernels during the last sample
    https://docs.nvidia.com/deploy/nvml-api/structnvmlUtilization__t.html#structnvmlUtilization__t
    """
    return pynvml.nvmlDeviceGetUtilizationRates(handle).gpu


def get_compute_mode(handle):
    """Returns the compute mode of the GPU
    https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceEnumvs.html#group__nvmlDeviceEnumvs_1gbed1b88f2e3ba39070d31d1db4340233
    """
    return pynvml.nvmlDeviceGetComputeMode(handle)


def get_compute_processes(handle):
    """Returns the list of processes ids having a compute context on the
    device with the memory used
    https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1g46ceaea624d5c96e098e03c453419d68
    """
    processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)

    return [{"pid": p.pid, "used_memory": p.usedGpuMemory} for p in processes]


def get_graphics_processes(handle):
    """Returns the list of processes ids having a graphics context on the
    device with the memory used
    https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html#group__nvmlDeviceQueries_1g7eacf7fa7ba4f4485d166736bf31195e
    """
    processes = pynvml.nvmlDeviceGetGraphicsRunningProcesses(handle)

    return [{"pid": p.pid, "used_memory": p.usedGpuMemory} for p in processes]


def get_gpu_static_info():
    """Get all GPUs static information.
    >>> get_gpu_static_info()
    [
        {
            "name": "Tesla V100-SXM2-16GB",
            "uuid": "GPU-4e817856-1fb8-192a-7ab7-0e0e4476c184",
            "total_memory": 16945512448,
            "power_limit": 300000,
            "gpu_index": 0,
        }
    ]
    """
    try:
        pynvml.nvmlInit()
        deviceCount = pynvml.nvmlDeviceGetCount()
        devices = []
        for i in range(deviceCount):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)

            # Memory
            memory = get_memory_info(handle)

            device_details = {
                "name": get_gpu_name(handle),
                "uuid": get_uuid(handle),
                "total_memory": memory.total,
                "power_limit": get_power_limit(handle),
                "gpu_index": i,
            }
            devices.append(device_details)
        return devices

    except pynvml.NVMLError:
        logger.debug("Failed to retrieve gpu static info", exc_info=True)
        return []


def get_gpu_details():
    """Get all GPUs instantaneous metrics
    >>> get_gpu_details()
    [
        {
            "name": "Tesla V100-SXM2-16GB",
            "uuid": "GPU-4e817856-1fb8-192a-7ab7-0e0e4476c184",
            "free_memory": 16945381376,
            "total_memory": 16945512448,
            "used_memory": 131072,
            "temperature": 28,
            "power_usage": 42159,
            "power_limit": 300000,
            "gpu_utilization": 0,
            "compute_mode": 0,
            "compute_processes": [],
            "graphics_processes": [],
        }
    ]
    """
    try:
        pynvml.nvmlInit()
        deviceCount = pynvml.nvmlDeviceGetCount()
        devices = []
        for i in range(deviceCount):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)

            # Memory
            memory = get_memory_info(handle)

            device_details = {
                "name": get_gpu_name(handle),
                "uuid": get_uuid(handle),
                "free_memory": memory.free,
                "total_memory": memory.total,
                "used_memory": memory.used,
                "temperature": get_temperature(handle),
                "power_usage": get_power_usage(handle),
                "power_limit": get_power_limit(handle),
                "gpu_utilization": get_gpu_utilization(handle),
                "compute_mode": get_compute_mode(handle),
                "compute_processes": get_compute_processes(handle),
                "graphics_processes": get_graphics_processes(handle),
            }
            devices.append(device_details)
        return devices

    except pynvml.NVMLError:
        logger.debug("Failed to retrieve gpu information", exc_info=True)
        return []


def is_gpu_details_available():
    """Returns True if the GPU details are available."""
    try:
        pynvml.nvmlInit()
        return True

    except pynvml.NVMLError:
        return False
