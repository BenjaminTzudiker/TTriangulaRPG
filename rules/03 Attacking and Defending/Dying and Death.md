---
up: "[[Playtest Packet]]"
prev: "[[Attack Procedure]]"
next: "[[Weapons]]"
---
# Dying and Death

*Status: Numbers placeholder; Exploratory (helping the dying)*

0 HP is meant to be deadly, dangerous and impactful: clearly worse than being knocked out.

**At 0 HP or below,** you're incapacitated, and you stay that way until rest brings you back to 1 HP or more (see [[Rest and Healing]]). At exactly 0 HP you're incapacitated but not in System Shock.

**Taking damage that puts you below 0 HP** puts you in **System Shock**.
- **Starting Shock:** equal to your negative HP. At −2 HP you have 2 Shock.
- **More damage:** taking damage while in System Shock lowers your HP as normal and raises your Shock by the same amount.
- **Dying roll:** at the start of each of your turns, roll **2d12 + Will**.

  | Roll | Result |
  |---|---|
  | Below 10 + Shock | +1 Shock (bleeding out). Your HP doesn't change. |
  | 10 + Shock to 14 + Shock | No change. |
  | 15 + Shock or more | −1 Shock (stabilizing). |

- **Death:** you die at **10 Shock** or at **−10 HP**.
- **Stabilized:** reaching 0 Shock, on your own or with help, ends System Shock.
  - Someone else can help you stabilize (see [[#Helping the Dying|Helping the Dying]]).
  - You stay at your negative HP and stay incapacitated, but you stop rolling.
- **Damaged while stabilized:** you re-enter System Shock, with Shock equal to the damage taken.
- **When the fight ends:** if anyone is still in System Shock, keep taking turns in initiative order until everyone is stabilized or dead, so the dying rolls continue. Allies who aren't incapacitated can help them stabilize (see [[#Helping the Dying|Helping the Dying]]).

> [!example] Example: System Shock
> 1. You're at 3 HP and take 5 damage. You're now at −2 HP with 2 Shock.
> 2. On your next turn you roll low: 3 Shock, still at −2 HP.
> 3. You take 3 more damage: −5 HP and 6 Shock.
> 4. Over the next few turns you're fully stabilized. You're at −5 HP, so still incapacitated, but no longer in System Shock and no longer rolling.
> 5. You take 1 damage: −6 HP and 1 Shock. You're rolling every turn again until you die or stabilize.
>
> To put the odds in context: at 9 Shock you need 24 or more to drop to 8. Below 19, you reach 10 and die.

## Helping the Dying

As an **action** with a base cost of **5**, you can tend a creature in System Shock within 1 square of you. It costs 5 + your escalation (see [[Actions and Escalation]]). Roll **2d12 + Intelligence**. If you roll at least **10 + its Shock**, its Shock drops by 1.

> [!example] Example: Helping the Dying
> Your ally is at 3 Shock, and you're next to it with Intelligence 1. You haven't taken an action this turn, so tending it costs 5. You roll 2d12 + 1 and need 13 or more (10 + 3). On a 15 it drops to 2 Shock. If you try again this turn, it costs 6.
