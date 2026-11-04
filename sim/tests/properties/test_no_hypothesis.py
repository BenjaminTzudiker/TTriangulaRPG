"""Without hypothesis installed (a chat that can't reach PyPI), conftest's stub skips only the
@given property tests; every other test in their modules still runs."""

import os
import re
import subprocess
import sys
from pathlib import Path

SIM = Path(__file__).resolve().parents[2]


def test_property_modules_run_without_hypothesis(tmp_path: Path) -> None:
    modules = sorted(
        p
        for p in (SIM / "tests").rglob("test_*.py")
        if "oracle" not in p.parts and p != Path(__file__) and "hypothesis" in p.read_text()
    )
    given = sum(len(re.findall(r"^@given", p.read_text(), re.M)) for p in modules)
    hidden = tmp_path / "hypothesis"
    hidden.mkdir()
    (hidden / "__init__.py").write_text(
        'raise ModuleNotFoundError("No module named hypothesis", name="hypothesis")\n'
    )
    env = {**os.environ, "PYTHONPATH": str(tmp_path)}
    done = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "no:hypothesispytest", "-p", "no:cacheprovider"]
        + ["-rs", *map(str, modules)],
        capture_output=True,
        text=True,
        env=env,
        cwd=SIM,
        timeout=300,
    )
    assert done.returncode == 0, done.stdout[-3000:]
    assert f"SKIPPED [{given}]" in done.stdout and "hypothesis is not installed" in done.stdout
    summary = done.stdout.strip().splitlines()[-1]
    assert f"{given} skipped" in summary and "passed" in summary, summary
