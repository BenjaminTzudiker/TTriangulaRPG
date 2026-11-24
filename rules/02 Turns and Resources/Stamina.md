---
up: "[[Playtest Packet]]"
prev: "[[HP]]"
next: "[[Melee Attacks]]"
---
# Stamina

*Status: Numbers placeholder (maximum); Locked (recovery timing); Numbers placeholder (recovery amount)*

Stamina is the effort immediately available to you: footwork, weapon control, concentration, balance, and the energy to react under pressure.

At any moment, each point of stamina you have is in one of three states (plus stamina you've **spent**, which is gone until you recover it):
- **Ready stamina** is in your active pool and available to spend now. (When the rules say "stamina" without qualifying it, they mean ready stamina.)
- **Held stamina** is committed to an active hold on an enemy, your reach, or an effect (see [[Holds]]).
- **Locked stamina** is left over from a hold that ended without its stamina being spent. It is no longer attached to anything and can't be used, but it still returns at the end of your next turn (see [[Holds]]).

**Maximum Stamina = 6 + current HP + round(Level / 5)**

Levels run from 0 to 99 (see [[Character Advancement]]). Characters start at level 1, where both level bonuses in this note are 0.

Because it uses *current* HP, injuries lower your maximum stamina. Your **ready**, **held** and **locked** stamina together can never exceed your maximum. Whenever something would take that total over your maximum, such as a wound that lowers your maximum, your recovery, or an ability, you lose the excess: you choose where it comes from (locked, held, or ready stamina, or some of each). Otherwise a wound doesn't change your ready stamina.

**At the end of your own turn,** after held and locked stamina return and you set any new holds (so you can't hold what you're about to recover; see [[Holds]]), **recover** **4 + round(Level / 10)** stamina into your ready stamina, up to your maximum.
- Round halves up, so the bonus becomes +1 at level 5.
- No attribute affects recovery.

Why the end of your turn?
- It's a safety net: you can't spend yourself to zero and then face a whole round defenseless.
- You'll want to spend some stamina right away, or your first recovery is wasted. That discourages passive standoffs.
- It rewards going early.

Stamina recovers every turn, so it's effectively full again after a short breather between fights. There's no formal rule for this yet.
