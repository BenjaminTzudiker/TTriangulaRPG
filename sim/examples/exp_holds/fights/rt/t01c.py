# Suspicion 1/3: duel, A attacks all-in then holds its recovered 4. A acts first.
SCEN = dict(
    rules="exp-holds", seed=5, round_cap=4,
    map="\n".join(["############", "#..........#", "#..........#", "#..........#", "############"]),
    roster=[("A", "red", "l1_sample", "", (4, 2)),
            ("X", "blue", "l1_sample", "", (5, 2))],
    order=["A", "X"],
)
