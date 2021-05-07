"""
Provides functionality for unit conversions
"""

from dataclasses import dataclass


@dataclass
class EmissionsPerKwh:
    """
    Measured in kg/kwh
    """

    LBS_MWH_TO_KG_KWH = 0.00045359237
    G_KWH_TO_KG_KWH = 0.001

    kgs_per_kwh: float

    @classmethod
    def from_lbs_per_mwh(cls, lbs_per_mwh: float) -> "EmissionsPerKwh":
        return cls(kgs_per_kwh=lbs_per_mwh * EmissionsPerKwh.LBS_MWH_TO_KG_KWH)

    @classmethod
    def from_g_per_kwh(cls, g_per_kwh: float) -> "EmissionsPerKwh":
        return cls(kgs_per_kwh=g_per_kwh * EmissionsPerKwh.G_KWH_TO_KG_KWH)

    @classmethod
    def from_kgs_per_kwh(cls, kgs_per_kwh: float) -> "EmissionsPerKwh":
        return cls(kgs_per_kwh=kgs_per_kwh)


@dataclass
class Energy:
    """
    Measured in kwh
    """

    UJOULES_TO_JOULES = 10 ** (-6)
    JOULES_TO_KWH = 0.000000277777778

    kwh: float

    @classmethod
    def from_power_and_time(cls, *, power: "Power", time: "Time") -> "Energy":
        return cls(kwh=power.kW * time.hours)

    @classmethod
    def from_ujoules(cls, energy: float) -> "Energy":
        return cls(kwh=energy * Energy.UJOULES_TO_JOULES * Energy.JOULES_TO_KWH)

    @classmethod
    def from_energy(cls, kwh: float) -> "Energy":
        return cls(kwh=kwh)

    def __sub__(self, other: "Energy") -> "Energy":
        return Energy(self.kwh - other.kwh)

    def __add__(self, other: "Energy") -> "Energy":
        return Energy(self.kwh + other.kwh)

    def __float__(self) -> float:
        return float(self.kwh)


@dataclass
class Power:
    """
    Measured in kw
    """

    MILLI_WATTS_TO_WATTS = 0.001
    WATTS_TO_KILO_WATTS = 0.001

    kW: float

    @classmethod
    def from_milli_watts(cls, milli_watts: float) -> "Power":
        return cls(
            kW=milli_watts * Power.MILLI_WATTS_TO_WATTS * Power.WATTS_TO_KILO_WATTS
        )

    @classmethod
    def from_watts(cls, watts: float) -> "Power":
        return cls(kW=watts * Power.WATTS_TO_KILO_WATTS)

    @property
    def W(self):
        if not isinstance(self.kW, float):
            return self.kW
        return self.kW * 1000


@dataclass
class Time:
    """
    Measured in seconds
    """

    SECONDS_TO_HOURS = 0.00027777778

    seconds: float

    @property
    def hours(self) -> float:
        return self.seconds * Time.SECONDS_TO_HOURS

    @classmethod
    def from_seconds(cls, seconds: float) -> "Time":
        return cls(seconds=seconds)
