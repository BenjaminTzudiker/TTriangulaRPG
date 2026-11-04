"""Write run results as Parquet: fights, attacks and decisions, plus a runs table holding the
provenance stamp, the RuleSet TOML and the scenario TOML. Every row carries the run id and
RuleSet digest, so rows from different runs can be stacked and still traced.

Written with pyarrow, imported only when results are written: Polars' default build needs
AVX, which some machines (x86 Python under Rosetta) lack. Read the files with Polars or
pandas as you like.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from stamina_engine.experiments.runner import RunResult

Rows = Sequence[dict[str, Any]]


def _columns(rows: Rows) -> dict[str, list[Any]]:
    keys: dict[str, None] = {}
    for r in rows:
        keys.update(dict.fromkeys(r))
    return {k: [r.get(k) for r in rows] for k in keys}


def _stamped(rows: Rows, run: RunResult) -> list[dict[str, Any]]:
    stamp = {
        "run_id": run.run_id,
        "cell": run.cell,
        "ruleset": run.scenario.rules.name,
        "ruleset_digest": run.scenario.rules.digest(),
    }
    return [{**stamp, **r} for r in rows]


def write_results(runs: Sequence[RunResult], out_dir: Path) -> list[Path]:
    import pyarrow as pa
    import pyarrow.parquet as pq

    out_dir.mkdir(parents=True, exist_ok=True)
    tables: dict[str, list[dict[str, Any]]] = {
        "runs": [
            {
                "run_id": run.run_id,
                "cell": run.cell,
                "scenario": run.scenario.name,
                "trials": len(run.fights),
                "scenario_toml": run.scenario.source,
                "ruleset_toml": run.scenario.rules.to_toml(),
                **run.provenance.as_dict(),
            }
            for run in runs
        ],
        "fights": [row for run in runs for row in _stamped(run.fights, run)],
        "attacks": [row for run in runs for row in _stamped(run.attacks, run)],
        "decisions": [row for run in runs for row in _stamped(run.decisions, run)],
    }
    paths = []
    for name, rows in tables.items():
        path = out_dir / f"{name}.parquet"
        pq.write_table(pa.table(_columns(rows)), path)
        paths.append(path)
    return paths
