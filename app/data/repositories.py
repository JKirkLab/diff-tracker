import sqlite3
from datetime import date

from app.core.utils.schedule import compute_schedule
from app.data.database import get_db_path
from app.core.models.protocol import Protocol, Step, Edge, DAG


def save_experiment(name: str, protocol: Protocol, start_date: date, end_date: date) -> int:
    with sqlite3.connect(get_db_path()) as conn:
        cursor = conn.execute(
            "INSERT INTO experiments (name, protocol_id, start_date, end_date) VALUES (?, ?, ?, ?)",
            (name, protocol.id, start_date.isoformat(), end_date.isoformat()),
        )
        

        step_rows = []

        for step_id, step in protocol.dag.steps.items():
            step_rows.append(
                (
                    cursor.lastrowid,
                    step_id,
                    step.name,
                    step.description,
                )

            )
        conn.executemany(
            """
            INSERT INTO experiment_steps
                (experiment_id, step_id, name, description)
            VALUES (?,?,?,?)
            """,
            step_rows
        )

        edge_list = []
        for edge in protocol.dag.edges:
            edge_list.append(
                (
                    cursor.lastrowid,
                    edge.source,
                    edge.target,
                    edge.days,
                    "",
                )
            )
        conn.executemany(
            """
            INSERT INTO experiment_edges
                (experiment_id, source_step_id, target_step_id, days, notes)
            VALUES (?,?,?,?,?)
            """,
            edge_list
        )

    return cursor.lastrowid



def load_experiments() -> list[dict]:
    """Return active experiments (end_date >= today) as UI-ready dicts."""
    today = date.today().isoformat()

    diffs = []

    with sqlite3.connect(get_db_path()) as conn:
        rows = conn.execute(
            "SELECT id, name, protocol_id, start_date FROM experiments WHERE end_date >= ?",
            (today,),
        ).fetchall()

        for exp_id, exp_name, protocol_id, start_date_str in rows:
            steps = {}
            edges = []
            for step_id, step_name, desc in conn.execute(
                "SELECT step_id, name, description FROM experiment_steps WHERE experiment_id = ?",
                (exp_id,)):
                steps[step_id] = Step(id= step_id, name = step_name, description = desc)

            for source, target, days in conn.execute(
                "SELECT source_step_id, target_step_id, days FROM experiment_edges WHERE experiment_id = ?",
                (exp_id,)
            ):
                edges.append(Edge(source = source, target = target, days = days))

            dag = DAG(steps=steps, edges=edges)

            start = date.fromisoformat(start_date_str)
            protocol = Protocol(id = protocol_id, name = exp_name, description = "", dag = dag)
            schedule = compute_schedule(protocol, start)
            diffs.append({
                "id": exp_id,
                "name": exp_name,
                "protocol": protocol,
                "schedule": schedule,
                "start_date": start,
            })

    return diffs


def save_plates(exp_id: int, plates: list[dict[str, str]]) -> None:
    """Replace all plates for an experiment with the given list."""
    with sqlite3.connect(get_db_path()) as conn:
        with conn:
            conn.execute("DELETE FROM plates WHERE experiment_id = ?", (exp_id,))
            for i, p in enumerate(plates, start=1):
                conn.execute(
                    """
                    INSERT INTO plates (experiment_id, plate_number, name, A1, A2, A3, B1, B2, B3)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        exp_id, i, p.get("name", ""),
                        p.get("A1", ""), p.get("A2", ""), p.get("A3", ""),
                        p.get("B1", ""), p.get("B2", ""), p.get("B3", ""),
                    ),
                )


def load_plates(exp_id: int) -> list[dict[str, str]]:
    """Returns [{"name": ..., well_id: note, ...}, ...] ordered by plate_number."""
    with sqlite3.connect(get_db_path()) as conn:
        rows = conn.execute(
            "SELECT name, A1, A2, A3, B1, B2, B3 FROM plates WHERE experiment_id = ? ORDER BY plate_number",
            (exp_id,),
        ).fetchall()
    return [
        {"name": r[0], "A1": r[1], "A2": r[2], "A3": r[3], "B1": r[4], "B2": r[5], "B3": r[6]}
        for r in rows
    ]


def update_experiment_edges(exp_id, updated_dates):

    step_id, delta = updated_dates
    note = f"Changed by {delta:+d} days on {date.today().isoformat()}"
    with sqlite3.connect(get_db_path()) as conn:
        conn.execute(
            """
            UPDATE experiment_edges
            SET days = days + ?,
            notes = ?
            WHERE experiment_id = ?
            AND target_step_id = ?
            """,
            (delta, note, exp_id, step_id )
        )
        conn.execute(
            "UPDATE experiments SET end_date = date(end_date, ? || ' days') WHERE id = ?",
            (str(delta), exp_id),
        )
