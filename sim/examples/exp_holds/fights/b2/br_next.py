# Brawl. Each side: a sample fighter (longsword and shield), a greatsword fighter and a
# Finesse-0 spearman (reach 2). RED: A sample, B greatsword, C spear. BLUE: X sample,
# Y greatsword, Z spear. They start 9 squares apart.
# Under exp-holds the greatsword (base 3, cap 2) and the spear (base 2, cap 1) can make no
# opportunity attack without a hold on the mover.
# Both sides fight to win: the last side with a creature up wins. Stop at the round cap.
SCEN = dict(
    rules="exp-holds-next-turn", seed=86, round_cap=8,
    map="\n".join(['######################', '#....................#', '#....................#', '#.........o..........#', '#....................#', '#....................#', '#..........o.........#', '#....................#', '#....................#', '######################']),
    roster=[
        ("A", "red", "l1_sample", "", (5, 4)),
        ("B", "red", "l1_greatsword", "", (5, 2)),
        ("C", "red", "l1_spear_fin0", "", (5, 6)),
        ("X", "blue", "l1_sample", "", (15, 4)),
        ("Y", "blue", "l1_greatsword", "", (15, 6)),
        ("Z", "blue", "l1_spear_fin0", "", (15, 2)),
    ],
    order=["A", "X", "B", "Y", "C", "Z"],
)
