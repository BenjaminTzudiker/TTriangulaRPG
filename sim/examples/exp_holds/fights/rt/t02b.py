# S5 retreat / the single-holder lock. X (wounded, 7 HP, max stamina 13) stands next to a
# healthy A, five squares from the exit on the west edge. A acts first, then X.
# BLUE (X) wants to get off the map; RED (A) wants to down it.
SCEN = dict(
    rules="exp-holds", seed=5, round_cap=4,
    map="\n".join(["############", ">..........#", ">..........#", ">..........#", "############"]),
    roster=[("A", "red", "l1_sample", "", (6, 2)),
            ("X", "blue", "l1_sample", "", (5, 2))],
    hp={"X": 7},
    order=["A", "X"],
)
