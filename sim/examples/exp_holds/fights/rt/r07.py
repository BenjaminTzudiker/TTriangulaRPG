# r07: the drained-target lock with an ally around (suspicions 2, 4, 5). As t02: X (blue, 7 HP)
# next to a healthy A, 5 squares from the west exit; plus Y (blue, fresh) 4 squares east of A.
# Order A, X, Y: A attacks X, then holds; X must decide before Y can act. Y can reach A this round.
SCEN = dict(
    rules="exp-holds", seed=5, round_cap=4,
    map="\n".join(["############", ">..........#", ">..........#", ">..........#", "############"]),
    roster=[("A", "red", "l1_sample", "", (6, 2)),
            ("X", "blue", "l1_sample", "", (5, 2)),
            ("Y", "blue", "l1_sample", "", (10, 2))],
    hp={"X": 7},
    order=["A", "X", "Y"],
)
