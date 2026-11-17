# S7 big weapons: can an enemy just walk past? B = greatsword fighter (base 3, cap 2) stands
# in the middle of a 3-wide corridor. X (sample fighter) walks past it through three squares
# of its reach: (5,1) (6,1) (7,1). X moves first, so B has had no chance to set a hold.
# t05 = exp-holds, t05n = exp-0.11.0, t05p = exp-holds-per-square.  t05s/t05sp: same walk
# past the Finesse-0 spearman (reach 2).
SCEN = dict(
    rules="exp-holds-per-square", seed=3, round_cap=3,
    map="\n".join(["##############", "#............#", "#............#", "#............#", "##############"]),
    roster=[("B", "red", "l1_spear_fin0", "", (6, 2)),
            ("X", "blue", "l1_sample", "", (2, 2))],
    order=["X", "B"],
)
