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

        for exp_id, exp_name, protocol_id, start_date_str, end_date_str in rows:
            steps = {}
            edges = []
            for step_id, step_name, desc in conn.execute("SELECT step_id, name, description FROM experiment_steps WHERE experiment_id = ?",
                (exp_id)):
                steps[step_id] = Step(id= step_id, name = step_name, description = desc)

            for source, target, days in conn.execute(
                "SELECT source_step_id, target_step_id, days FROM experiment_edges WHERE experiment_id = ?",
                (exp_id),
            ):
                edges.append(Edge(source = source, target = target, days = days))

            dag = DAG(steps=steps, edges=edges)

            start = date.fromisoformat(start_date_str)
            protocol = Protocol(id = protocol_id, name = exp_name, description = "", dag = dag)
            schedule = compute_schedule(protocol, start)
            diffs.append({
                "name": exp_name,
                "protocol": protocol,
                "schedule": schedule,
                "start_date": start,
            })

    return diffs
