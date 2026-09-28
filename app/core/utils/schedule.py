from datetime import timedelta

from app.core.models.experiment import ScheduleEntry
from app.core.models.protocol import Protocol


def compute_schedule(protocol: Protocol, start_date) -> list[ScheduleEntry]:
    """Walk the protocol DAG and return one ScheduleEntry per step, in order."""
    edge_map = {e.source: e for e in protocol.dag.edges}

    entries: list[ScheduleEntry] = []
    current_id = "start"
    current_date = start_date

    while current_id:
        step = protocol.dag.steps[current_id]
        entries.append(
            ScheduleEntry(
                step=step,
                date=current_date,
                day_number=(current_date - start_date).days,
            )
        )
        if current_id in edge_map:
            edge = edge_map[current_id]
            current_date = current_date + timedelta(days=edge.days)
            current_id = edge.target
        else:
            break

    return entries