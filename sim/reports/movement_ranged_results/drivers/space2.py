# Run from sim/: python3 reports/movement_ranged_results/drivers/space2.py 300
# A2x: the same archer-vs-fighter sweep with an unshielded fighter (two-handed longsword, Ranged
# Defense 1), so the shot compels the close. Does the pricing rule decide how many shots the
# fighter eats on the way, and does that decide the fight?
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import space as sp
trials = int(sys.argv[1]) if len(sys.argv) > 1 else 300
sp.trials = trials
def archer(d, fighter_agent, build):
    return sp.archer(d, fighter_agent).replace('build = "l1_sample"', f'build = "{build}"')
print("## A2x. Archer vs unshielded two-hander at 16 / 20 / 24 squares")
for rule, ov in sp.RULES.items():
    for d in (16, 20, 24):
        sp.cell(f"{rule}, two-hander: {d} apart", archer(d, sp.TACT, "l1_twohand"), ov, "A2x")
print("space2 done")
