# Same as t02 under exp-0.11.0 (no holds).
# healthy A, five squares from the exit on the west edge. A acts first, then X.
# BLUE (X) wants to get off the map; RED (A) wants to down it.
SCEN = dict(
    rules="exp-0.11.0", seed=5, round_cap=4,
    map="\n".join(["############", ">..........#", ">..........#", ">..........#", "############"]),
    roster=[("A", "red", "l1_sample", "", (6, 2)),
            ("X", "blue", "l1_sample", "", (5, 2))],
    hp={"X": 7},
    order=["A", "X"],
)
