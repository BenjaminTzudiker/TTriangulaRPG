"""Where a result came from: the rules, the code and any plugins. Printed with every result.

The RuleSet digest identifies the rule configuration (which variants, which parameters). It
doesn't cover code, so a variant whose code was edited keeps its digest. The source hash
covers that: it hashes every file in the installed package, including data tables, so it
identifies the implementation even in a throwaway clone or an unpacked snapshot. Git details
are added when the package runs from a git checkout.
"""

import hashlib
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path

from stamina_engine.rules.plugins import PluginInfo
from stamina_engine.rules.ruleset import RuleSet

PACKAGE_DIR = Path(__file__).resolve().parent


def tree_sha256(root: Path) -> str:
    """SHA-256 over every file under root (path and bytes, in path order), skipping caches."""
    h = hashlib.sha256()
    files = sorted(
        (p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts),
        key=lambda p: p.relative_to(root).as_posix(),
    )
    for path in files:
        if path.suffix == ".pyc":
            continue
        h.update(path.relative_to(root).as_posix().encode())
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


@dataclass(frozen=True)
class GitInfo:
    commit: str
    describe: str  # nearest tag and distance, or the short commit if there are no tags
    dirty: bool  # uncommitted changes to the engine's code or data


def _git(cwd: Path, *args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def git_info(package_dir: Path = PACKAGE_DIR) -> GitInfo | None:
    """Git details, only when the package itself is tracked (an editable install)."""
    if _git(package_dir, "ls-files", "--error-unmatch", "__init__.py") is None:
        return None
    commit = _git(package_dir, "rev-parse", "HEAD")
    describe = _git(package_dir, "describe", "--tags", "--always")
    status = _git(package_dir, "status", "--porcelain", "--", ".")
    if commit is None or describe is None or status is None:
        return None
    return GitInfo(commit=commit, describe=describe, dirty=bool(status))


def _engine_version() -> str:
    try:
        return metadata.version("stamina-engine")
    except metadata.PackageNotFoundError:
        return "unknown"


@dataclass(frozen=True)
class Provenance:
    ruleset: str
    ruleset_digest: str
    engine_version: str
    source_sha256: str
    git: GitInfo | None
    plugins: tuple[PluginInfo, ...]

    def lines(self) -> list[str]:
        if self.git is None:
            code = "not a git checkout"
        else:
            changes = "uncommitted changes" if self.git.dirty else "clean"
            code = f"git {self.git.describe} ({self.git.commit[:12]}, {changes})"
        out = [
            f"RuleSet {self.ruleset} {self.ruleset_digest[:12]}",
            f"Code {code}; source {self.source_sha256[:12]}; stamina-engine {self.engine_version}",
        ]
        for p in self.plugins:
            parts = ", ".join(f"{kind}/{variant}" for kind, variant in p.components)
            out.append(f"Plugin {p.name} {p.sha256[:12]}: {parts}")
        return out

    def text(self) -> str:
        return "\n".join(self.lines())

    def as_dict(self) -> dict[str, str | bool | None]:
        """Flat fields, for stamping result tables."""
        return {
            "ruleset": self.ruleset,
            "ruleset_digest": self.ruleset_digest,
            "engine_version": self.engine_version,
            "source_sha256": self.source_sha256,
            "git_commit": self.git.commit if self.git else None,
            "git_describe": self.git.describe if self.git else None,
            "git_dirty": self.git.dirty if self.git else None,
            "plugins": ";".join(f"{p.name}:{p.sha256}" for p in self.plugins) or None,
        }


def collect(rules: RuleSet, plugins: Sequence[PluginInfo] = ()) -> Provenance:
    return Provenance(
        ruleset=rules.name,
        ruleset_digest=rules.digest(),
        engine_version=_engine_version(),
        source_sha256=tree_sha256(PACKAGE_DIR),
        git=git_info(),
        plugins=tuple(plugins),
    )
