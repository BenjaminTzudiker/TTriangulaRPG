# r04w: the reach-2 pin when X waits a round instead of stepping in (seed 8): can Z re-pin?
# apart on open ground, Z acts first. Z pokes with 1 step, then holds X with everything (X can't
# reach Z, so Z needs no ready stamina). Question: what can X do? Step in (eat the OA), back off
# (also leaves a square in Z's reach), or wait (and be poked again)?
SCEN = dict(
    rules="exp-holds", seed=8, round_cap=5,
    map="\n".join(["##############", "#............#", "#............#", "#............#", "##############"]),
    roster=[("Z", "red", "l1_spear_fin0", "", (5, 2)),
            ("X", "blue", "l1_sample", "", (7, 2))],
    order=["Z", "X"],
)
