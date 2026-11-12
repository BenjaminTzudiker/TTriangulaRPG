"""Step-by-step play (`se play --step`, simulator requirements R8): a fight played through
the answers file alone, the same answers always reaching the same request, bad answers
reported and not consumed, and the session log `se load` reads."""

import hashlib
import json
from pathlib import Path
from typing import Any

from stamina_engine.cli import invoke
from stamina_engine.experiments.scenario import load_scenario
from stamina_engine.experiments.session import read_session
from stamina_engine.experiments.step import AWAITING, INVALID, OVER, Answer, read_answers, step

SCENARIOS = Path(__file__).resolve().parents[2] / "src" / "stamina_engine" / "data" / "scenarios"
ARCHER = SCENARIOS / "archer_open.toml"


def first_answer(report: dict[str, Any]) -> str:
    """A simple legal answer to the waiting decision."""
    d = report["decision"]
    f = d["fields"]
    kind = d["kind"]
    if kind == "turn":
        return f"s {f['shots'][0]}" if f["shots"] else "e"
    return {
        "aim": "0",
        "steps": "1",
        "blocks": "1",
        "off_turn": "p",
        "react": "p",
        "avoid": "none",
        "take_oa": "0",
        "ability": "p",
    }[kind]


def play_through(answers: Path, who: str = "A", limit: int = 300) -> dict[str, Any]:
    for _ in range(limit):
        out = invoke(["play", str(ARCHER), "--as", who, "--step", "--answers", str(answers)])
        report = json.loads(out.output)
        if out.exit_code == OVER:
            return report
        assert out.exit_code == AWAITING, out.output
        out = invoke(
            [
                "play",
                str(ARCHER),
                "--as",
                who,
                "--step",
                "--answers",
                str(answers),
                "--answer",
                first_answer(report),
            ]
        )
        assert out.exit_code in (AWAITING, OVER), out.output
    raise AssertionError("the fight didn't end")


def test_a_fight_played_through_the_answers_file(tmp_path: Path) -> None:
    answers = tmp_path / "a.jsonl"
    report = play_through(answers)
    assert report["status"] == "over" and report["winner"] in ("archer", "fighter", None)
    lines = [json.loads(line) for line in answers.read_text().splitlines()]
    assert lines and all(line["who"] == "A" for line in lines)
    assert {line["kind"] for line in lines} >= {"turn", "aim"}
    # Replaying the finished file gives the same ending, every time.
    again = invoke(["play", str(ARCHER), "--as", "A", "--step", "--answers", str(answers)])
    assert again.exit_code == OVER and json.loads(again.output) == report


def test_the_same_answers_reach_the_same_request() -> None:
    s = load_scenario(ARCHER)
    answers = [Answer("p"), Answer("s F")]
    first = step(s, ("A",), 0, answers)
    second = step(s, ("A",), 0, answers)
    assert first.code == AWAITING and first.report["decision"]["kind"] == "aim"

    def digest(r: dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(r, sort_keys=True).encode()).hexdigest()

    assert digest(first.report) == digest(second.report)
    other = step(s, ("A",), 1, answers[:1])
    assert other.report["seed"] != first.report["seed"]


def test_a_bad_answer_is_reported_and_not_appended(tmp_path: Path) -> None:
    answers = tmp_path / "a.jsonl"
    args = ["play", str(ARCHER), "--as", "A", "--step", "--answers", str(answers)]
    out = invoke([*args, "--answer", "s nobody"])
    assert out.exit_code == INVALID
    report = json.loads(out.output)
    assert report["status"] == "invalid" and report["answer"] == "s nobody"
    assert not answers.exists() or answers.read_text() == ""
    assert invoke([*args, "--answer", "p"]).exit_code == AWAITING
    out = invoke([*args, "--answer", "s F"])
    assert out.exit_code == AWAITING
    out = invoke([*args, "--answer", "99"])  # more aims than it can afford
    assert (
        out.exit_code == INVALID and "isn't one of the options" in json.loads(out.output)["reason"]
    )
    assert len(answers.read_text().splitlines()) == 2


def test_a_bad_line_in_the_file_is_reported_by_number(tmp_path: Path) -> None:
    answers = tmp_path / "a.jsonl"
    answers.write_text('{"answer": "p"}\n"x"\n')
    out = invoke(["play", str(ARCHER), "--as", "A", "--step", "--answers", str(answers)])
    assert out.exit_code == INVALID
    report = json.loads(out.output)
    assert report["answers_file_line"] == 2 and report["answers_used"] == 1
    wrong = tmp_path / "b.jsonl"
    wrong.write_text('{"who": "F", "answer": "p"}\n')
    out = invoke(["play", str(ARCHER), "--as", "A", "--step", "--answers", str(wrong)])
    assert out.exit_code == INVALID and "A's, not F's" in json.loads(out.output)["reason"]


def test_both_sides_and_the_session_log(tmp_path: Path) -> None:
    """Two controlled combatants share one answers file; the session log at the end is the
    one `se load --session` reads."""
    answers = tmp_path / "a.jsonl"
    log = tmp_path / "s.jsonl"
    base = ["play", str(ARCHER), "--as", "A", "--as", "F", "--step", "--answers", str(answers)]
    for _ in range(400):
        out = invoke([*base, "--log", str(log)])
        if out.exit_code == OVER:
            break
        report = json.loads(out.output)
        d = report["decision"]
        text = first_answer(report)
        if d["kind"] == "turn" and d["who"] == "F":
            text = f"a {d['fields']['targets'][0]}" if d["fields"]["targets"] else "m 3,4"
        assert invoke([*base, "--answer", text]).exit_code in (AWAITING, OVER, INVALID)
        if json.loads(invoke(base).output)["answers_used"] == report["answers_used"]:
            assert invoke([*base, "--answer", first_answer(report)]).exit_code != INVALID
    else:
        raise AssertionError("the fight didn't end")
    sess = read_session(log)
    assert sess.header["played_by_human"] == "A,F"
    assert {d["who"] for d in sess.decisions} <= {"A", "F"}
    assert all(d["seconds"] is None for d in sess.decisions)
    load = invoke(["load", "--session", str(log)])
    assert load.exit_code == 0 and "Load: 1 session(s)" in load.output
    assert len(read_answers(answers)) == json.loads(out.output)["answers_used"]
