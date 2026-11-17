# r07b: r07 with order A, Y, X: the ally acts between the holder and the held target.
# next to a healthy A, 5 squares from the west exit; plus Y (blue, fresh) 4 squares east of A.
# Order A, Y, X: Y can hit A before X decides.
SCEN = dict(
    rules="exp-holds", seed=5, round_cap=4,
    map="\n".join(["############", ">..........#", ">..........#", ">..........#", "############"]),
    roster=[("A", "red", "l1_sample", "", (6, 2)),
            ("X", "blue", "l1_sample", "", (5, 2)),
            ("Y", "blue", "l1_sample", "", (10, 2))],
    hp={"X": 7},
    order=["A", "Y", "X"],
)
