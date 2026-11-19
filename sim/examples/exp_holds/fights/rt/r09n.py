# r09n: r09 (held creature shot at) under exp-0.11.0.
# fighter) and holds it; C (red archer, bow) 6 squares away then shoots X. Dodging = dashing out of
# its square, which is in A's reach. Order A, C, X. r09n: the same under exp-0.11.0.
SCEN = dict(
    rules="exp-0.11.0", seed=17, round_cap=3,
    map="\n".join(["##############", "#............#", "#............#", "#............#", "##############"]),
    roster=[("A", "red", "l1_sample", "", (4, 2)),
            ("X", "blue", "l1_sample", "", (5, 2)),
            ("C", "red", "l1_archer", "bow", (11, 2))],
    order=["A", "C", "X"],
)
