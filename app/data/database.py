from pathlib import Path
from platformdirs import user_data_dir
import sqlite3

def get_db_path():
    data_dir = Path(user_data_dir("DiffTracker"))
    data_dir.mkdir(parents=True, exist_ok=True)

    return data_dir / "diff_tracker.db"


def init_db():
    db_path = get_db_path()

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            conn.execute(
                "ALTER TABLE experiments ADD COLUMN end_date TEXT NOT NULL DEFAULT '9999-12-31'"
            )
        except Exception:
            pass  

        conn.executescript("""
            CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            protocol_id TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS experiment_steps (
            id INTEGER PRIMARY KEY,
            experiment_id INTEGER NOT NULL,
            step_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,

            FOREIGN KEY (experiment_id) REFERENCES experiments(id),
            UNIQUE (experiment_id, step_id)
        );

        CREATE TABLE IF NOT EXISTS experiment_edges (
            id INTEGER PRIMARY KEY,
            experiment_id INTEGER NOT NULL,
            source_step_id TEXT NOT NULL,
            target_step_id TEXT NOT NULL,
            days INTEGER NOT NULL,
            notes TEXT,

            FOREIGN KEY (experiment_id) REFERENCES experiments(id),
            FOREIGN KEY (experiment_id, source_step_id) REFERENCES experiment_steps(experiment_id, step_id),
            FOREIGN KEY (experiment_id, target_step_id) REFERENCES experiment_steps(experiment_id, step_id)
        );
        """)