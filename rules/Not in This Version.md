---
up: "[[Playtest Packet]]"
prev: "[[Open Questions]]"
next: "[[Earlier Candidate Abilities]]"
---
# Not in This Version

These ideas are deliberately left out of the current rules. They're strong candidates to come back, so don't build around their absence.
- **Maximum HP Damage:** only part of an attack's damage could become HP loss; the rest would only cost stamina. Ranged attacks now have their own version of this, the aim limit (see [[Aim]]). A general rule stays out until melee shows it needs one.
- **Split attribute bonuses for ranged:** band width or Ranged Defense drawn from two attributes (for example, band width from Finesse 1 and 5 plus Cunning 3) instead of one.
- **Creature sizes,** with size scaling the range penalty per band: Tiny −8, Small −4, Medium −2, Large −1, bigger to be decided.
- **Damage reducing maximum stamina:** would let a character be worn out of the fight before reaching 0 HP.
- **A stamina cap ("hard flux"):** some of the stamina you spend defending wouldn't come back at your next recovery, so pressure would build up over several rounds.
  - **Why it came up:** in Starsector, damage your shields absorb stays on your flux bar while the shields are up, so even light pressure builds up, and clearing it means backing off. Here, recovery gives back everything a small attack costs to stop (about 3 stamina for a 1-step attack on the sample fighter, who recovers 4), so nothing sits between "it all comes back" and a wound. A cap would also make stamina spent attacking and stamina spent defending work differently, so that numbers slightly out of balance wouldn't tip fights into "whoever commits first wins" or into stalemates.
  - **What was tried,** under packet 0.10.1's rules, in an exact solver for duels in contact (no movement) and in engine fights:
    - *Perfect blocks lock,* and so does paying to avoid an opportunity attack; a round with neither clears the lock; grazing blocks are exempt, so armor keeps a niche. Between fighters who both play around it, duels end much as they do without it (6.9 → 6.1 rounds at Melee Defense 4), because recovery can come from stamina spent on other things. But a fighter who ignores it gives up 7 points of win chance at Melee Defense 4, and 35–42 at Melee Defense 5.
    - *Every block locks,* and only a round with no block clears it. This is a real clock: duels at Melee Defense 3, 4 and 5 last 2.6, 4.2 and 5.8 rounds, against 2.7, 6.9 and 15.7, so fight length stops hinging on getting defense exactly right. But it snowballs: a fighter 4 stamina behind wins 7% at Melee Defense 4, against 15%, and the first mover's edge grows (64% → 68%).
    - *Clearing only part of the lock, a slow drain, or never clearing it* each bought a shorter fight only with a bigger first-mover edge and a costlier deficit. *Stamina back for attacking,* the reverse idea, favored whoever struck first: 73% → 86.5% at Melee Defense 3.
    - *In the engine's group fights,* neither lock changed the results under the movement rules of the time: someone was usually down in the first round, before recovery mattered.
  - **Its merits:** light pressure would leave something behind; true stalemates would end; a pressed fighter would have a reason to back off and catch its breath, and a hold something to deny; and a visible cap would show who's under pressure.
  - **Why it's out:** it would be the busiest rule in the game: a second number for every creature, the GM's included, that changes on most blocks and is checked at every recovery. That's a new core mechanic on a system that already has enough of them. Its effect also grows with fight length: it's small in fights of the 3–5 rounds the game aims for, and the version strong enough to matter there snowballs. And pressure may now leave a mark in other ways: since 0.11.0, being made to dash makes your next attacks cost more, and since 0.11.1, a hold makes leaving cost more. Neither has been played yet.
  - **What would bring it back:** signs in play that pressure doesn't stick: nobody ever wants to step back and catch their breath; small attacks feel pointless, so players go all in or not at all; or both sides wait for the other to commit. Lighter fixes are candidates too: numbers in the existing rules, or a breather (extra recovery if you neither attacked nor were attacked since your last turn). If a cap comes back, it should make room for itself, either by simplifying something else or by changing shape, for example into a cap that turns the choice between perfect and grazing blocks into a real trade-off.
- **Lingering and permanent injuries.**
- **Extended contests** for grapples, holds and charms. These are control effects, not the hold in [[Holds]].
- **Spell schools and spell progression.**
- **NPC aggression profiles:** balance-tested defaults for how NPCs play.
- **A Strength requirement for shields,** like armor's. A candidate for pricing the shield's defense (Review F4), to be decided with the rest of the equipment numbers.
- **Initiative you have agency over,** rather than only a die roll. The leading idea is bidding: at the start of a fight, each creature may pay stamina from its starting pool to act earlier.
  - Acting first is worth a lot (about 35 points of win rate in equal level-1 duels in the engine), and a bid would put a stamina price on that edge directly.
  - It's one decision per fight, so it adds little load.
  - It shouldn't overlap the Rogue's core ability, which sells turn-order control during a fight; bids would set only the opening order.
  - Cunning could set the bidding order (higher Cunning bids after seeing the others).
  - Holds make close gang-ups lean harder on turn order. In a three-on-one starting 3 squares apart, with one attacker acting before the lone fighter, holds raise its chance of going down in the first round from 6% to 58% (exact, one round). If the lone fighter acts first, it's 0% either way.
  - For now, initiative is 2d12 + Cunning, with ties broken by Agility + Cunning and then a roll-off, as placeholders.
