"""Provenance: results name the rules, the code and the plugins that produced them."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from stamina_engine.provenance import PACKAGE_DIR, collect, git_info, tree_sha256
from stamina_engine.rules.ruleset import review_sim, v0_9


def test_tree_hash_sees_every_change(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "t.toml").write_text("v = 2\n")
    first = tree_sha256(tmp_path)
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "a.cpython-313.pyc").write_bytes(b"cache")
    assert tree_sha256(tmp_path) == first  # caches don't count
    (tmp_path / "data" / "t.toml").write_text("v = 3\n")
    assert tree_sha256(tmp_path) != first  # data tables count
    (tmp_path / "data" / "t.toml").write_text("v = 2\n")
    assert tree_sha256(tmp_path) == first
    (tmp_path / "b.py").write_text("")
    assert tree_sha256(tmp_path) != first  # new files count


def test_source_hash_stable_across_processes() -> None:
    code = "from stamina_engine.provenance import collect; from stamina_engine.rules.ruleset "
    code += "import v0_9; print(collect(v0_9()).source_sha256)"
    other = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert other.stdout.strip() == collect(v0_9()).source_sha256


@pytest.mark.skipif(shutil.which("git") is None, reason="needs git")
def test_git_details_in_a_checkout() -> None:
    info = git_info()
    assert info is not None  # tests run from an editable install in the repo
    head = subprocess.run(
        ["git", "-C", str(PACKAGE_DIR), "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    assert info.commit == head


def test_stamp_contents() -> None:
    p = collect(review_sim())
    lines = p.lines()
    assert lines[0] == f"RuleSet review-sim {review_sim().digest()[:12]}"
    assert p.source_sha256[:12] in lines[1]
    assert p.as_dict()["ruleset_digest"] == review_sim().digest()
    assert p.as_dict()["plugins"] is None


def test_not_a_checkout(tmp_path: Path) -> None:
    assert git_info(tmp_path) is None
