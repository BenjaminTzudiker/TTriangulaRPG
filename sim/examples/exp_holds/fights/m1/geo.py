#!/usr/bin/env python3
"""Geometry helper (my own; reads the engine and the scenario map, changes nothing).

  python3 geo.py cover SX,SY TX,TY [OX,OY ...]   cover of a target at T from a shooter at S,
                                                 with other creatures at the O squares
  python3 geo.py covermap SX,SY [OX,OY ...]      cover level of every square from S (0 none, 1 half,
                                                 2 three-quarters, 3 total), and distance band penalty
"""
import importlib.util
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "src"))  # sim/src
from stamina_engine.grid.battlefield import parse_map  # noqa: E402
from stamina_engine.grid.los import cover  # noqa: E402
from stamina_engine.rules.ruleset import preset  # noqa: E402

spec = importlib.util.spec_from_file_location("fight", "sc_holds.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
FIELD = parse_map(mod.SCEN["map"])
RULES = preset("exp-holds")


def cell(t):
    x, y = t.split(",")
    return (int(x), int(y))


def main():
    kind = sys.argv[1]
    s = cell(sys.argv[2])
    if kind == "cover":
        t = cell(sys.argv[3])
        others = [cell(a) for a in sys.argv[4:]]
        d = max(abs(s[0] - t[0]), abs(s[1] - t[1]))
        pen = 2 * (max(1, -(-d // 4)) - 1)
        print(f"shooter {s} -> target {t}: cover {int(cover(FIELD, RULES.grid, s, t, others))}, distance {d}, penalty {pen}")
    else:
        others = [cell(a) for a in sys.argv[3:]]
        print("    " + "".join(str(x % 10) for x in range(FIELD.width)))
        for y, row in enumerate(FIELD.rows):
            line = ""
            for x, ch in enumerate(row):
                if ch in "#o=":
                    line += ch
                elif (x, y) == s:
                    line += "S"
                elif (x, y) in others:
                    line += "c"
                else:
                    line += str(int(cover(FIELD, RULES.grid, s, (x, y), others)))
            print(f"{y:>3} {line}")


main()
