# Rearguard. All six are level-1 sample fighters. Red starts hurt: B has 4 HP, C has 6 HP.
# RED's goal: get its creatures off the map by the west edge (move onto a > square, then
#   'flee' on that creature's turn), the wounded B and C above all.
# BLUE's goal: down as many Red creatures as it can before they get away.
# The fight starts engaged: X stands next to A. Stop at the round cap if it isn't over.
SCEN = dict(
    rules="exp-0.11.0", seed=31, round_cap=7,
    map="\n".join(['########################', '>......................#', '>......................#', '>.........o............#', '>......................#', '>......................#', '>.............o........#', '>......................#', '>......................#', '########################']),
    roster=[
        ("A", "red", "l1_sample", "", (17, 4)),
        ("B", "red", "l1_sample", "", (16, 2)),
        ("C", "red", "l1_sample", "", (16, 6)),
        ("X", "blue", "l1_sample", "", (18, 4)),
        ("Y", "blue", "l1_sample", "", (19, 2)),
        ("Z", "blue", "l1_sample", "", (19, 6)),
    ],
    hp={"B": 4, "C": 6},
    order=['X', 'A', 'Y', 'B', 'Z', 'C'],
)
