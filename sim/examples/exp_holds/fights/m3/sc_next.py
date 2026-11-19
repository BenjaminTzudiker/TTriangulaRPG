# Screen. RED: two sample fighters (A, B) in front of an archer (C, bow in hand).
# BLUE: three sample fighters (X, Y, Z) who start 13 squares from Red's fighters.
# Both sides fight to win: the last side with a creature up wins. Stop at the round cap.
SCEN = dict(
    rules="exp-holds-next-turn", seed=58, round_cap=8,
    map="\n".join(['#########################', '#.......................#', '#.....o.......=.........#', '#.......................#', '#..........o............#', '#.......................#', '#..........=............#', '#.......................#', '#.....o.......=.........#', '#.......................#', '#########################']),
    roster=[
        ("A", "red", "l1_sample", "", (7, 4)),
        ("B", "red", "l1_sample", "", (7, 6)),
        ("C", "red", "l1_archer", "bow", (3, 5)),
        ("X", "blue", "l1_sample", "", (20, 4)),
        ("Y", "blue", "l1_sample", "", (20, 5)),
        ("Z", "blue", "l1_sample", "", (20, 6)),
    ],
    order=["X", "A", "Y", "C", "Z", "B"],
)
