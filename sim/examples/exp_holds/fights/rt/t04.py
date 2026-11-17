# S7 reach-2 spear hold. Z = Finesse-0 spearman (reach 2, cap 1), X = sample fighter (reach 1).
# They start 2 squares apart: Z can hit X, X cannot hit Z without stepping in. Z acts first.
# t04 = exp-holds, t04n = same under exp-0.11.0.
SCEN = dict(
    rules="exp-holds", seed=7, round_cap=5,
    map="\n".join(["##############", "#............#", "#............#", "#............#", "##############"]),
    roster=[("Z", "red", "l1_spear_fin0", "", (5, 2)),
            ("X", "blue", "l1_sample", "", (7, 2))],
    order=["Z", "X"],
)
