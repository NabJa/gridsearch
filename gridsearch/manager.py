import sqlite3
from dataclasses import dataclass
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


def read_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_grid_values(min, max, num, dist):
    if dist == "linear":
        return np.linspace(min, max, num)
    if dist == "log":
        return np.logspace(np.log10(min), np.log10(max), num)
    raise ValueError(f"Unknown distribution: {dist}")


@dataclass
class GridParam:
    dist: str
    num: int
    min: int
    max: int

    @property
    def values(self):
        return get_grid_values(self.min, self.max, self.num, self.dist)


class Grid:
    def __init__(self, path):
        self.path = Path(path)
        self.params = self._load_params(path)
        self.grid = self._generate_grid()

    def _load_params(self, path):
        params = read_yaml(path)
        return {k: GridParam(**v) for k, v in params.items()}

    def _generate_grid(self) -> pd.DataFrame:
        grid = np.array(list(product(*[p.values for p in self.params.values()])))
        grid = pd.DataFrame(grid, columns=self.params.keys())
        grid["status"] = "pending"
        return grid

    def init(self, sql_path=None, if_exists="skip") -> Path:
        """_summary_
        Args:
            sql_path: Path to SQL database. If None, will use self.path.with_suffix(".db"). Defaults to None.
            if_exists: One of 'fail', 'replace', 'append' or 'skip'. Defaults to 'skip'.
        """
        if sql_path is None:
            sql_path = self.path.with_suffix(".db")

        if Path(sql_path).exists() and if_exists == "skip":
            print("Skipped db generation: File already exists")
            self.sql_path = Path(sql_path)
            return Path(sql_path)

        conn = sqlite3.connect(sql_path)
        self.grid.to_sql("grid", conn, if_exists=if_exists, index=False)
        conn.close()

        self.sql_path = Path(sql_path)
        return Path(sql_path)
