# r11: splitting tokens (suspicion 8). A (red sample fighter) stands between X and Y (blue sample
# fighters, both wounded to 6 HP). Order A, X, Y. A attacks X, then splits its hold between X and Y.
# Question: does a split hold lock both, and can the two targets together punish A?
SCEN = dict(
    rules="exp-holds", seed=29, round_cap=3,
    map="\n".join(["############", ">..........#", ">..........#", ">..........#", "############"]),
    roster=[("A", "red", "l1_sample", "", (5, 2)),
            ("X", "blue", "l1_sample", "", (4, 2)),
            ("Y", "blue", "l1_sample", "", (6, 2))],
    hp={"X": 6, "Y": 6},
    order=["A", "X", "Y"],
)
