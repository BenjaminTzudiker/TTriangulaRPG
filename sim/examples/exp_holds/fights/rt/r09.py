# r09: a held creature is shot at (suspicion 6). A (red sample fighter) attacks X (blue sample
# fighter) and holds it; C (red archer, bow) 6 squares away then shoots X. Dodging = dashing out of
# its square, which is in A's reach. Order A, C, X. r09n: the same under exp-0.11.0.
SCEN = dict(
    rules="exp-holds", seed=17, round_cap=3,
    map="\n".join(["##############", "#............#", "#............#", "#............#", "##############"]),
    roster=[("A", "red", "l1_sample", "", (4, 2)),
            ("X", "blue", "l1_sample", "", (5, 2)),
            ("C", "red", "l1_archer", "bow", (11, 2))],
    order=["A", "C", "X"],
)
