# r08: a held archer (suspicion 6). X (blue sample fighter) starts next to C (red archer, bow in
# fighter) starts next to C (red archer, blade drawn, Melee Defense 3). Order X, C. X attacks, then holds
# or shoot point-blank, or draw the blade and fight. r08n: the same under exp-0.11.0.
SCEN = dict(
    rules="exp-holds", seed=4, round_cap=4,
    map="\n".join(["################", "#..............#", "#..............#", "#..............#", "################"]),
    roster=[("X", "blue", "l1_sample", "", (5, 2)),
            ("C", "red", "l1_archer", "blade", (6, 2))],
    order=["X", "C"],
)
