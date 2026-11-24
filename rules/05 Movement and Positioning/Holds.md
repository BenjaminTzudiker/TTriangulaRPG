---
up: "[[Playtest Packet]]"
prev: "[[Opportunity Attacks]]"
next: "[[Forced Movement]]"
---
# Holds

*Status: Mechanism open*

A hold commits some of your stamina to punishing one enemy if it gives you an opening. It's how the side that's ahead finishes the job: a spent enemy you hold can't walk away, while a fresh one can always pay to leave.
- **Small holds** press a small edge. Leaving costs the enemy more, and you gamble that you can get through a round on less stamina of your own.
- **Big holds** end a fight that's already decided, without rounds of doomed retreat. They aren't meant for every small advantage. Against an enemy that can still hurt you, a big hold is a gamble.

## Setting Holds

At the end of your turn, you hold from what you have left, and your recovery comes on top:
1. **Held and locked stamina return.** Any stamina you held (or that became locked when a hold ended) returns to your **ready stamina**. Stamina you **spent** on opportunity attacks or abilities is gone until you recover it.
2. **Set new holds** from your ready stamina. Place any amount of it on enemies, split among as many enemies as you like. That stamina is now **held stamina** attached to those holds. The enemies don't have to be within your reach.
3. **Recover** stamina into your ready stamina (see [[Stamina]]).

So everything you hold is stamina you didn't spend this turn: a hold always competes with your attack, and you can't spend everything and then hold the stamina you're about to recover. Held stamina counts toward your maximum, so at or near full stamina a hold also costs you some or all of that turn's recovery.

Setting holds is how you end your turn: say who you're holding and with how much stamina. If you say nothing, you're holding no one. Setting a hold isn't an action.

## While Your Stamina Is Held or Locked

- **Held stamina** stays attached to its hold until it is spent, the hold ends, or it returns at the end of your next turn. You can't spend it on blocks, normal actions, or anything else except what its hold allows (by default, opportunity attacks against that enemy; some abilities add other uses).
- **Locked stamina** is unspent stamina left over from a hold that **ended** (or from a creature that went down). It is no longer attached to any hold and can't be spent or used for anything, but it stays unavailable until it **returns** to your ready stamina at the end of your next turn.
- Both held and locked stamina count toward your maximum stamina (see [[Stamina]]).

## What a Hold Does

**Leaving.** When a creature you hold leaves a square in your reach, it pays **1 + the stamina you hold on it** to avoid your opportunity attack, instead of 1 (see [[Opportunity Attacks#Avoiding Opportunity Attacks|Avoiding Opportunity Attacks]]). The hold then ends (any unspent held stamina becomes locked), so any further squares it leaves in your reach cost the usual 1. Being moved by [[Forced Movement]] isn't leaving a square, so it doesn't trigger or end a hold.

**Opportunity attacks.** The stamina you hold on a creature adds to your cap for opportunity attacks against it, and is **spent** before your ready stamina (see [[Opportunity Attacks#Making Opportunity Attacks|Making Opportunity Attacks]]). That includes the opportunity attack a creature provokes by shooting while in your reach. Spending held stamina on that attack doesn't end the hold: the hold is just smaller by what you spent (if you spend all of it, the hold ends).

**Several holders.** Several creatures can hold the same enemy. It pays each of them.

## When a Hold Ends

A hold ends:
- **when the creature you hold leaves a square in your reach.** It ends whether the creature pays, takes your opportunity attack, or doesn't pay and you choose not to attack;
- **when you lose any HP.**

When a hold ends, any stamina still held on it isn't spent and doesn't return early: it becomes **locked** until it returns to your ready stamina at the end of your next turn. Stamina held on a creature that goes down becomes **locked** in the same way.

> [!example] Example: A Hold
> Your sample fighter ends its turn next to a wounded orc, with 6 ready stamina left. It holds the orc with 4 stamina and keeps 2, then recovers 4: 6 ready stamina, and 4 held.
> - **The orc has 3 stamina.** It can't pay 1 + 4 = 5 to step away. If it leaves anyway, your opportunity attack can spend your cap of 2 plus the 4 held: two longsword steps (2 + 3 = 5), paid by spending all 4 held stamina and 1 ready stamina.
> - **If it stays and hits you for even 1 HP,** the hold ends at once. Your 4 held stamina becomes **locked** until the end of your next turn.
> - **On your next turn** you have at most 6 ready stamina to attack with, not 10. At the end of that turn your held or locked stamina returns to your ready stamina, and you can hold again.

> [!question] Closing in on a reach weapon
> Stepping closer to an enemy with a reach weapon provokes (see [[Opportunity Attacks#Triggers|Triggers]]). So a creature held by an enemy with a reach weapon, such as a spear in two hands, pays 1 + the held stamina just to close in, or takes the opportunity attack, which it can still block as usual. That may be a plausible advantage for reach, or a problem. It's undecided, and there's no exception for now.

> [!question] Sizing a hold
> Sizing a hold well takes several things at once: the target's stamina, how much held stamina buys another step of your opportunity attack, whether the target can afford to hurt you, and what you need on your next turn. How often a table gets that right without odds tables is unknown.
