import argparse
import sqlite3
import subprocess
from typing import Optional

from gridsearch.manager import Grid


def get_next_pending_param(sql_path: str) -> Optional[dict]:
    """
    Safely retrieves a parameter combination with status 'pending'.
    Marks the combination as 'in_progress' to avoid being picked by other processes.

    Args:
        sql_path: Path to the SQLite database.

    Returns:
        A dictionary with the parameter combination (including 'rowid'), or None if no pending rows are available.
    """
    conn = sqlite3.connect(sql_path)
    conn.isolation_level = None  # Ensure transactions are explicit
    cursor = conn.cursor()

    try:
        # Start an immediate transaction to lock the database row
        cursor.execute("BEGIN IMMEDIATE")
        # Select the first pending row
        cursor.execute("SELECT rowid, * FROM grid WHERE status = 'pending' LIMIT 1")
        row = cursor.fetchone()
        if row is None:
            conn.rollback()  # No pending row found, rollback transaction
            return None

        # Unpack the row details
        row_id = row[0]  # First column is `rowid`
        params = dict(zip([col[0] for col in cursor.description], row))

        # Mark the row as in_progress
        cursor.execute(
            "UPDATE grid SET status = 'in_progress' WHERE rowid = ?", (row_id,)
        )
        conn.commit()
        return params
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()


def param_generator(sql_path):
    while True:
        params = get_next_pending_param(sql_path)
        if params is None:
            print("No pending parameters found. Exiting...")
            break

        yield params


class GridContextManager:
    def __init__(self, config, if_exists):
        self.config = config
        self.if_exists = if_exists
        self.sql_path = None
        self.conn = None
        self.row = None

    def __enter__(self):
        self.grid = Grid(self.config)
        self.sql_path = self.grid.init(if_exists=self.if_exists)
        self.conn = sqlite3.connect(self.sql_path)
        return self

    def run_command(self, script_path):
        param = next(param_generator(self.sql_path))
        self.row = param.pop("rowid")
        _ = param.pop("status")
        command = ["sbatch", script_path]
        for key, value in param.items():
            command.extend([f"--{key}", str(value)])
        subprocess.run(command)

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            if self.row is not None:
                self.conn.execute(
                    "UPDATE grid SET status = 'completed' WHERE rowid = ?",
                    (self.row,),
                )
                self.conn.commit()
            self.conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Grid search runner")
    parser.add_argument("config", type=str, help="Path to the config file")
    parser.add_argument("script_path", type=str, help="Path to the script to run")
    parser.add_argument(
        "--if_exists", type=str, default="skip", help="How to handle existing database."
    )
    args = parser.parse_args()

    with GridContextManager(args.config, args.if_exists) as manager:
        manager.run_command(args.script_path)
