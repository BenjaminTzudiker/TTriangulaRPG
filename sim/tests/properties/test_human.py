"""The human agent and its session log (se play, se load --session): answers parsed from
typed lines, re-asked when invalid, timed, and logged."""

from itertools import count
from pathlib import Path

from stamina_engine.agents.human import HumanAgent, ScriptedIO
from stamina_engine.cli import invoke
from stamina_engine.experiments.load import load_report
from stamina_engine.experiments.runner import run_trial
from stamina_engine.experiments.scenario import load_scenario
from stamina_engine.experiments.session import play, read_session, write_session

SCENARIOS = Path(__file__).resolve().parents[2] / "src" / "stamina_engine" / "data" / "scenarios"
ANSWERS = {  # tried in order until one is accepted
    "turn> ": ["a", "e"],
    "steps> ": ["2", "1", "0"],
    "blocks> ": ["1"],
    "off-turn> ": ["p"],
    "ability> ": ["p"],
    "avoid> ": ["none"],
    "oa> ": ["0"],
    "aims> ": ["3", "2", "1", "0"],
    "move> ": ["p"],
}
REFUSED = "  That isn't one of the options"


class PromptIO:
    """Answers by prompt: one garbled line the first time each prompt comes up, then the
    listed answers in turn until one is accepted."""

    def __init__(self) -> None:
        self.shown: list[str] = []
        self.garbled: set[str] = set()
        self.tries: dict[str, int] = {}
        self.answers = ANSWERS

    def show(self, text: str) -> None:
        self.shown.append(text)
        if not text.startswith(REFUSED):
            self.tries.clear()

    def ask(self, prompt: str) -> str:
        if prompt not in self.garbled:
            self.garbled.add(prompt)
            return "nonsense 9 9"
        n = self.tries.get(prompt, 0)
        self.tries[prompt] = n + 1
        options = self.answers[prompt]
        if n >= len(options):
            raise AssertionError(f"every answer to {prompt!r} was refused")
        return options[n]


def clock() -> object:
    ticks = count()
    return lambda: 1.5 * next(ticks)


def test_a_person_plays_a_duel_and_every_decision_is_timed(tmp_path: Path) -> None:
    s = load_scenario(SCENARIOS / "l1_duel_open.toml")
    io = PromptIO()
    result, seed = play(s, "A", trial=0, io=io, clock=clock())  # type: ignore[arg-type]
    mine = [d for d in result.decisions if d.who == "A"]
    assert mine and all(d.seconds is not None and d.seconds > 0 for d in mine)
    assert all(d.seconds is None for d in result.decisions if d.who != "A")
    assert any("isn't one of the options" in t for t in io.shown)  # re-asked, not refused
    assert any("Your turn" in t for t in io.shown)
    # The other side and the dice are the trial's own: same seed as an engine run.
    engine = run_trial(s, 0)
    assert engine.log[0] == result.log[0]

    path = tmp_path / "session.jsonl"
    write_session(path, s, "A", 0, seed, result)
    back = read_session(path)
    assert back.header["played_by_human"] == "A" and back.result["rounds"] == result.rounds
    assert len(back.decisions) == len(result.decisions)
    report = load_report(
        [d for d in back.decisions if d["who"] == "A"], back.attacks, result.rounds, "x"
    )
    assert "Seconds (mean)" in report and "turn_command" in report

    out = invoke(["load", "--session", str(path)])
    assert out.exit_code == 0, out.output
    assert "people's decisions" in out.output


def test_moves_by_destination_or_exact_path() -> None:
    """Off the map and a broken path are refused; a destination alone takes the cheapest
    path there."""
    from stamina_engine.engine.events import Moved
    from stamina_engine.experiments.runner import battle_for, trial_seed

    s = load_scenario(SCENARIOS / "one_v_three_open.toml")
    io = PromptIO()
    io.answers = {
        **ANSWERS,
        "turn> ": ["m 99,99", "m 0,0 9,9", "m 4,7", "e"],
        "blocks> ": [str(n) for n in range(9, 0, -1)],  # the least injury listed
    }
    human = HumanAgent(s.rules, io, clock())  # type: ignore[arg-type]
    b = battle_for(s, trial_seed(s.seed, s.name, 0), check=True, agents={"D": human})
    result = b.run()
    moved = [e for e in result.log if isinstance(e, Moved) and e.who == "D"]
    assert moved and moved[0].to == (4, 7) and moved[0].how == "free"
    shown = "\n".join(io.shown)
    assert "m X,Y" in shown and shown.count("isn't one of the options") >= 3


def test_cli_play_logs_a_session(tmp_path: Path) -> None:
    path = tmp_path / "s.jsonl"
    keys = "\n".join(["a", "2", "1", "p", "e"] * 50) + "\n"
    out = invoke(["play", str(SCENARIOS / "l1_duel.toml"), "--as", "A", "--log", str(path)],
        stdin=keys,
    )
    assert out.exit_code in (0, 1), out.output
    if out.exit_code == 0:
        assert read_session(path).header["played_by_human"] == "A"


def test_scripted_io_runs_out() -> None:
    import pytest

    io = ScriptedIO(["a"])
    assert io.ask("turn> ") == "a"
    with pytest.raises(EOFError):
        io.ask("turn> ")
