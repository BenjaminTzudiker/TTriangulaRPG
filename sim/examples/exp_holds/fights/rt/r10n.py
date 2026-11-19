# r10n: r10 (rearguard) under exp-0.11.0: X pays 1 to leave B and chases A.
# blue X; the west exit is 8 squares from A, so A needs two turns to get out. Order B, A, X.
# B holds X so that chasing A costs X; A runs. Question: does X chase, or punish B?
SCEN = dict(
    rules="exp-0.11.0", seed=13, round_cap=4,
    map="\n".join(["#############", ">...........#", ">...........#", ">...........#", "#############"]),
    roster=[("A", "red", "l1_sample", "", (8, 2)),
            ("B", "red", "l1_sample", "", (9, 1)),
            ("X", "blue", "l1_sample", "", (9, 2))],
    hp={"A": 4},
    order=["B", "A", "X"],
)
