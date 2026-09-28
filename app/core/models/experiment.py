from dataclasses import dataclass
from datetime import date

from .protocol import DAG, Step


@dataclass
class ScheduleEntry:
    step: Step
    date: date
    day_number: int


@dataclass
class Experiment:
    id: int | None
    name: str
    protocol_id: str
    start_date: date
    dag: DAG