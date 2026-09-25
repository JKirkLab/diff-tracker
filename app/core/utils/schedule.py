import json
from datetime import date, timedelta
from pathlib import Path


def load_protocol(path: Path | str) -> dict:
    with open(path) as f:
        return json.load(f)


def compute_schedule(protocol: dict, start_date: date) -> list[dict]:
    """Walk the edge graph and return [{step, date, day_number}, ...] in order."""
    steps = {s["id"]: s for s in protocol["steps"]}
    edges = {e["from"]: e for e in protocol["edges"]}

    schedule = []
    current_id = "start"
    current_date = start_date

    while current_id:
        schedule.append(
            {
                "step": steps[current_id],
                "date": current_date,
                "day_number": (current_date - start_date).days,
            }
        )
        if current_id in edges:
            edge = edges[current_id]
            current_date = current_date + timedelta(days=edge["days"])
            current_id = edge["to"]
        else:
            break

    return schedule