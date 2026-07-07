from dataclasses import dataclass
from datetime import datetime


@dataclass
class Alarm:
    overtemperature: bool
    overpower: bool
    raw: int


@dataclass
class Measurement:
    temperature: float
    dc_power: float
    ac_power: float
    energy: float
    alarm: Alarm

    farm_id: str | None = None

    timestamp: datetime | None = None
    efficiency: float | None = None