import sqlite3
from app.core.models.experiment import Experiment
from app.data.database import get_db_path
def save_experiment(exp: Experiment):
    db_path = get_db_path()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO experiments ( name, protocol_id, start_date)
            VALUES (?, ?, ?)
            """,
            (
                exp.name,
                exp.protocol_id,
                exp.start_date.isoformat()
            )
        )
        experiment_id = cursor.lastrowid

    return experiment_id

def load_experiment():
    return