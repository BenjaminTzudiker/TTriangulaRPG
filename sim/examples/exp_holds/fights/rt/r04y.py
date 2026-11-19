# r04y: the reach-2 pin with an ally for the pinned side. Z (red spear, reach 2) pins X (blue,
# 2 squares away) with a big hold; Y (blue sample fighter) starts 5 squares from Z and acts after X.
# Question: does Z's big hold leave it open to Y?  Order Z, X, Y.
SCEN = dict(
    rules="exp-holds", seed=8, round_cap=4,
    map="\n".join(["##############", "#............#", "#............#", "#............#", "#............#", "#............#", "##############"]),
    roster=[("Z", "red", "l1_spear_fin0", "", (5, 2)),
            ("X", "blue", "l1_sample", "", (7, 2)),
            ("Y", "blue", "l1_sample", "", (5, 5))],
    order=["Z", "X", "Y"],
)
