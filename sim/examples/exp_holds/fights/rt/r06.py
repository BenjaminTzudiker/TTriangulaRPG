# r06: two holders on one target (suspicion 2). A and B (red sample fighters) flank X (blue sample
# fighter, fresh). Order A, B, X. Each red attacks X with 2 steps, then holds X with what it thinks
# it can spare. Question: can X leave? Is attacking a holder (low ready) a real answer?
SCEN = dict(
    rules="exp-holds", seed=21, round_cap=4,
    map="\n".join([">###########", ">..........#", ">..........#", ">..........#", "############"]),
    roster=[("A", "red", "l1_sample", "", (4, 2)),
            ("B", "red", "l1_sample", "", (6, 2)),
            ("X", "blue", "l1_sample", "", (5, 2))],
    order=["A", "B", "X"],
)
