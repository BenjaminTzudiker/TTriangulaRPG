# S1 free hold in a plain duel (both fresh sample fighters, A first). A attacks with 2 steps,
# then holds everything it does not expect to need for blocking. t03 = with the hold,
# t03z = same orders with no hold. Compare A at the start of its next turn.
SCEN = dict(
    rules="exp-holds", seed=11, round_cap=4,
    map="\n".join(["############", "#..........#", "#..........#", "#..........#", "############"]),
    roster=[("A", "red", "l1_sample", "", (6, 2)),
            ("X", "blue", "l1_sample", "", (5, 2))],
    order=["A", "X"],
)
