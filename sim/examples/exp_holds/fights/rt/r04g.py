# r04g: r04f with Z acting first.
# apart. r04f: X acts first (can it close for free and hold Z?). r04g: Z acts first (does Z
# close to 2 squares, poke and pin?).
SCEN = dict(
    rules="exp-holds", seed=8, round_cap=4,
    map="\n".join(["################", "#..............#", "#..............#", "#..............#", "################"]),
    roster=[("Z", "red", "l1_spear_fin0", "", (3, 2)),
            ("X", "blue", "l1_sample", "", (9, 2))],
    order=["Z", "X"],
)
