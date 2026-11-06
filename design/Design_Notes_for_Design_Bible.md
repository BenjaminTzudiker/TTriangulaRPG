> **⚠ STATUS: WORKING NOTES — NOT A FINISHED DESIGN BIBLE.**
> This is raw source material for a future design bible. It was updated on 2026-11-01 for the designer's nine rounds of rulings on the reconciliation ledger. Entries citing [C:2026-11-05] were added from the attribute design chat of that date.
> - **What the rules currently are:** the ledger is authoritative. These notes record *why*.
> - **Pillars:** the wordings in §2 are draft condensations, not adopted text.
> - **UNCERTAIN:** unconfirmed.
> - **SHELVED:** the principle still stands, but the mechanism that served it is deliberately out of the current rules (ledger Part H).
> - **§8:** principles the designer did **not** endorse. Don't treat them as house rules.

# Design Notes: Source Material for the Design Bible

*Only things you stated or clearly endorsed. Each entry is tagged:*
- **STATED**: your own words.
- **ENDORSED**: a proposal you explicitly agreed to.
- **UNCERTAIN**: lean or paraphrase; confirm before canonizing.
- **SHELVED**: the principle stands, but its mechanism is parked in the ledger's Part H. It's a candidate solution, not a rule.

*Like "Locked" in the ledger, a STATED principle is a deliberate current position, not an untouchable one. A good enough reason can reopen it.*

*Citations:*
- *[p.N] is a transcript page, ±1.*
- *[R1:A3] is your ruling round 1, item A3. All rulings are dated 2026-11-01 and logged verbatim in the ledger's Part G. Round 2's unnumbered items are cited as [R2].*
- *[C:2026-11-05] is a design chat on that date (the attribute chat). Quotes are your messages in it.*
- *Where a principle evolved, the final form comes first and the history follows.*

---

## 0. How this is organized, and why

I looked at how game teams structure design documentation. Three conventions recur:

1. **Pillars are few and testable.**
   - Three or four short rules, each naming an *experience* rather than a feature.
   - Each is specific enough that a proposed mechanic could fail it.
   - New features are checked against them.
   - A pillar that could describe any game ("fun combat") is useless.
2. **Principles are written as rule + rationale.**
   - A bare slogan gets misapplied. Recording the *why* lets a future you, or another collaborator, tell when the rule actually applies.
3. **A decision log records rejected alternatives with their reasons.** This stops ideas being re-proposed, and lets you knowingly reopen one if circumstances change.

So:
- §1 is your experience goal in your own words.
- §2 condenses it into pillars, plus one constraint.
- §3 holds principles, each as **Rule / Why / Test (how to apply it) / Source**.
- §4 is the rejected-alternatives log, plus decisions your rulings reversed and ideas that are shelved rather than rejected.
- §5 holds the open tensions.
- §6 holds the inspirations.
- §7 is the gap check against the packet.
- §8 lists principles ChatGPT proposed that you *didn't* endorse, so they don't creep in.

The pillar wordings in §2 are my condensation of your statements. The quoted source material under each is yours. Confirm or rewrite the one-line versions.

---

## 1. Experience goal (your words)

The project brief:

> "Create a tactical fantasy TTRPG centered around a continually regenerating stamina system. This TTRPG should:
> * preserve danger and narrative plausibility without punishing the players just for getting into fights in ways that they have no agency over
> * create interesting tactical situations without overwhelming the players with decisions or arithmetic"

**STATED** (project description)

Your clearest articulation in the transcript:

> "I'm trying to aim for something with more real danger than a heroic fantasy feeling but without the emphasis on *random* risk that I associate with 'gritty' fantasy. I'm intentionally departing from realism and treating characters as, for example, more aware of their surroundings in combat and with more agency over their own deaths than is true in real battles… Think 'named characters in Game of Thrones'. They do sometimes die, but usually not to just getting randomly stabbed once while not paying attention like the mooks often die to. The named characters need to be pressured before they take a fatal hit while the mooks can just take fatal hits for no tangible reason." [p.1277]

**STATED**

The core idea, as you wanted it in the intro:

> "Stamina isn't a resource you spend to enhance your defense, it *is* your defense. The game is about managing the ebb and flow of stamina, because when you run out you can no longer do things and you might just straight up die." [p.1826]

**STATED** ("very important")

Earlier form of the same goal:

> "I want to make combat feel dangerous, but not super wildly swingy and deadly - it should feel like the players have tools to outplay their opponents and they won't just die to bad dice luck as long as they play smart." [p.90]

**STATED**

---

## 2. Pillars (condensed; confirm wording)

**P1. Stamina is the fight.**
- One regenerating pool pays for attacking, blocking, moving, reacting and casting. Your defense *is* your remaining stamina.
- Sources:
  - "a small amount of stamina… which is spent to do almost anything" [p.87].
  - Contrast with other systems where stamina is "a limited resource you can spend to do extra stuff rather than the core of combat" [p.722].
  - The intro quote above [p.1826].
- *Test:* does this mechanic run through stamina? If it's a separate economy, it needs a strong reason.

**P2. Danger you can see and answer.**
- Any hit can be decisive and HP is tiny. But a named character is only seriously wounded after being pressured or misjudging, never by luck alone.
- Sources:
  - "one good sword hit can kill or KO someone" [p.90].
  - "They should be able to hurt other people, but they should have counterplay" [p.188].
  - The Game of Thrones quote [p.1277].
- *Test:* can the victim see it coming and spend to prevent it? If not, it fails.

**P3. Plausible in the fiction.**
- Every rule should read as something that could actually happen in a fight. Where you depart from realism, it's deliberate, and in favor of player agency.
- Sources:
  - "I want the system to feel real/aid in simulating a real seeming world" [p.537].
  - "Simulationist" [p.639].
  - "in my system I want the combat mechanics to be understandable as actual plausible events happening in a fight" [p.1587].
  - "I want to have a plausible narrative rather than 'I dodge the arrow'" [p.1142].
- *Test:* can you narrate what this rule represents? Game-y recharge loops and arrows that only drain stamina have failed this before [p.186, p.537].

**P4. Build the character you imagine.**
- Never make players choose between being faithful to their concept and being effective.
- Sources:
  - "Mechanically disincentivizing making your character build match your idea of the character in your head is something I very much want to avoid." [p.298]
  - §3.4 below.
- *Test:* would a concept-faithful choice cost this player combat effectiveness?

**Constraint C1. Complexity budget.**
- Tactical depth must not come from arithmetic load or decision overload. Stated in the brief; recurring at [p.87], [p.987], [p.1059], [p.2036].
- *Test:* is this a new number that changes every attack? If so, it must create a real decision.

---

## 3. Principles

### 3.1 Combat economy

**Punish mistakes with lost tempo, not death.**
- *Rule:* Overspending should leave you unable to press the attack, not defenseless. Stamina recovers at the **end** of your turn.
- *Why:* A safety net (new players can't zero their own defense), arithmetic done off-turn, and "being on the back foot".
- *Source:* "I think I want decision making to lead to punishments, but in this case I think the punishment of not having stamina to attack with on your turn might be enough?" [p.129]. Rationale also at [p.127], [p.788], [p.1275].
- **STATED**

**Reward early commitment; don't reward passivity.**
- *Rule:* End-of-turn recovery is wasted if you don't spend, so the first actor is pushed to engage.
- *Why:* So fights don't stall while nobody wants to overextend. You raised that problem at [p.227].
- *Source:* "you're encouraged to spend some stamina immediately because otherwise your first turn regen will be wasted, which will hopefully help prevent passivity" [p.1275]. "it rewards higher initiative" [p.788].
- **STATED**

**Attacking should be more stamina-efficient than perfect blocking; cheap grazing is the counterweight.**
- *Rule:* Don't nerf attacks to make defense viable. Give defense a flat-cost option that trades a little injury for efficiency, plus armor.
- *Why:* Prevents turtling while letting defenders punish overcommitment.
- *Source:* "I do want attacking to be overall a more efficient use of stamina to prevent turtling" [p.726]. "If someone overcommits to the attack, you take a grazing hit to avoid dying while conserving stamina and then strike back" [p.799].
- **STATED**

**Escalate cost, don't also shrink the payoff.**
- *Rule:* Repeated purchases get pricier per step, but each step delivers the same amount. Never double-penalize.
- *Why:* The rising cost already creates diminishing returns, and double scaling adds math for no new decision.
- *Source:* "You're double penalizing - not only does it cost two stamina to get the second damage step, but you don't even get as much damage." [p.804]. "It's always 6+6+6+... or 4+4+4+..." [p.809]. Also [p.517]: "needlessly complicated to lower the return and increase the cost".
- **STATED**

**Rising marginal costs are the house tool against over-specialization.**
- *Rule:* Repeatable spends and build purchases (attack steps, blocks, attribute points, skill ranks, extra trees) cost more each time. Use that as a soft cap instead of hard limits.
- *Also applied to multiclassing:* each core tree ability you already own makes other core abilities cost +1 AP [R1:B12].
- *Source:* "I also want to be careful making overspecializing the correct choice - that's a big part of why I have many repeatable stamina expenditures (eg attacks/defenses) and character building costs (eg stat points) increase in marginal cost." [p.1041]. "No need to set a hard cap if your sixth history-specific bonus costs 6 skill points." [p.1439]
- **STATED**
- *Corollary:* break the triangle pattern when it can't produce the intended incentive. "it diverges from the triangular numbers so I avoided it, but it seems like that's necessary" [p.1439]. **STATED**

**Doing several things in a turn is possible but expensive.**
- *Source:* "I want to make it possible but expensive to do multiple things in one turn." [p.1226]. "Having that scaling stamina for attacks *and* extra attack like in 5e seems messy and unnecessary." [p.176]. "There should probably be some way to combine multiple actions per turn" [R1:A4].
- **STATED**
- *How it's applied now:*
  - Each melee attack step and each aim step is an "action".
  - Each action costs +1 per action already taken this turn.
  - Ranged shots pay a flat base cost [R1:A4].
  - The mechanism is open, and "action" is a provisional name (§3.6).

**Commit up front; misjudging should cost efficiency, not be forbidden.**
- *Rule:* You declare the whole attack. Follow-ups are allowed but are easier to block, because the defender's count resets.
- *Why:* Keeps play fast (no fine-tuning swing by swing) while allowing multi-target attacks and recovery from misjudgment.
- *Source:* "This encourages the attacker to not bog the game down by separately resolving each attack to precisely tune stamina usage, but also let them attack multiple targets or finish off an unusually tough target with reduced efficiency for misjudging the required attack commitment" [p.490].
- **STATED**

**Tax the decisions the system actually tracks.**
- *Rule:* Charge stamina for choices the rules model (which square you move to), not for unmodeled detail (each swing).
- *Source:* "'each swing/incantation' isn't taxed is because it isn't tracked. There's no decision for the player to make there in this system, whereas there *is* a decision on which square to move to" [p.1339].
- **STATED**
- *Evolution (OA avoidance):*
  1. Paid per decision [p.1355].
  2. Then once per enemy per turn [p.1361].
  3. Now 1 stamina per enemy **per square left** [R1:A3, R3:1].
  - *My reading:* each square is still a decision the system tracks, so the principle survives and only the granularity changed.

**Don't punish aggression with unrelated costs.**
- *Rule:* Advancing on your turn shouldn't make your later retreat more expensive; being further forward is risk enough. On-turn and off-turn costs use separate tracks, and blocking escalates only within one attack.
- *Source:* "there's no penalty to off-turn movement from your on-turn movement so there's no mechanical punishment for aggression" [p.1712]. "blocking is its own thing that only escalates within one attack" [p.1783].
- **STATED**
- *Corollary:* off-turn movement and opportunity attacks share one off-turn track, which resets at the start of your turn, "so off turn movement competes with opportunity attacks for stamina" [R1:B4, R1:A6]. **STATED**

**Opportunity attacks are limited and not free, but exposure should be punishable.**
- *Rule:*
  - Cap what you can spend on one OA: 1 stamina, +1 per odd Finesse. Finesse is the OA stat.
  - OAs count toward the attacker's off-turn track, so they cost the attacker future options.
  - An enemy that exposes itself for several squares should be punishable for more, even by someone who hasn't invested in Finesse. The mechanism for this is open.
- *Source:* "mechanic to limit opportunity attack power" [R1:A8]. "The enemies don't get to opportunity attack for free" [R2:1]. "the intent being that it's still sometimes possible to opportunity attack for more than 1 stamina even if you don't invest in finesse as long as the enemy exposes themself enough" [R2:1].
- **STATED** (intent locked, mechanism open)

**Using your fun abilities shouldn't cripple you afterwards.**
- *Rule:* Prefer soft limits that tax the present turn (strain overage adds stamina cost) over lasting debuffs (max-stamina costs) or "bug the party for a rest" lockouts.
- *Applied:* overexertion (lowering max stamina to gain stamina) is abandoned [R3:8].
- *Source:* "Should I really have players spend max stamina on normal abilities? That seems pretty punishing" [p.446]. "I don't want casters crippled outside of their leveled spell casting ability for using their abilities, and the tradeoff of 'you can keep casting... but each time you're making yourself more vulnerable the turn you do' sounds interesting." [p.474]. "I want to avoid people blowing all of their strain on one or two big flashy fun abilities only to then bug the party for a rest… (feels like maybe an unfun type of punishment for using fun abilities?)" [p.1041].
- **STATED**

**Don't mechanically encourage things that are unfun to do.**
- *Source:* "doing nothing on your turn kinda sucks and I don't want to mechanically encourage things that suck to do." [p.221]
- **STATED**

### 3.2 Danger, agency and information

**Lasting harm is acceptable because damage is avoidable.**
- *Rule:* Injuries can stick (lingering injuries, slow HP recovery) *because* players control whether they take hits. That's the opposite of 5e, where damage is unavoidable.
- *Source:* "Those always seemed unfun to me in 5e because you couldn't really avoid taking damage, but maybe it'd fit better in this system." [p.339]
- **STATED**
- *Current state:* the lingering and permanent injury rules are **SHELVED** (ledger H-3) [R2]. Today, lasting harm means slow HP recovery (1 HP per night) and no HP-restoring magic.

**Consequences should feel weighty but cost little in practice.**
- *Rule:* Prefer penalties that read as a real setback in the fiction but stay mechanically mild: once per fight rather than once per round, and never a death spiral.
- *Source:* "damage reducing max stamina was chosen because it *feels* like a real negative but isn't actually very *punishing* in practice." On max stamina tracking current HP: "the sort of meaningful but non-crippling (because it's a once-per-fight nerf rather than once-per-round or worse) that I'd want to have to make injury meaningful without death spirals." [C:2026-11-05]
- **STATED**
- *Calibration:* in an even level-1 duel, each missing HP costs about 5 points of win rate through the stamina it removes (extrapolated from `sim/reports/str_value.md`). You accepted that: "A duel against an equal opponent sounds like the worst case scenario for minor penalties, so it should usually be less impactful. I think I'm fine with it being moderately punishing in that case when moderately injured." [C:2026-11-05]

**No HP-restoring magic (for now).**
- *Rule:*
  - HP comes back only through rest.
  - No HP-recovery spells like 5e's *Healing Word* or *Cure Wounds* are planned.
  - Don't design, or assume, a healer role that refills HP.
- *Source:* "HP recovery spells like Healing Word or Cure Wounds from 5e aren't planned to be included, which might be important to communicate to Claude explicitly in some way." [R2]
- **STATED**
- *Why:* you didn't give a reason in the ruling. *My reading:* it follows from slow-healing HP and "lasting harm is acceptable because damage is avoidable".

**Going below 0 HP is deadly and impactful, but not instantly final.**
- *Rule:* 0 HP should be clearly worse than being knocked out. There should still be a window in which you can stabilize or be saved.
- *Source:* 0 HP should be "deadly, dangerous, and impactful" [p.339, p.342].
- **STATED**
- *How it's applied now:* **System Shock** [R2, R4–R6].
  - You enter it below 0 HP, starting at Shock equal to your negative HP.
  - Each turn you roll toward bleeding out or stabilizing.
  - Damage adds Shock.
  - 10 Shock or −10 HP kills.
  - Exactly 0 HP incapacitates you without Shock.
- *Still open:* an "out of the fight but alive" state above 0 HP. Damage reducing max stamina (H-2) is your candidate (§5).

**Injuries change what you can do, not just your numbers.**
- *Source:* "I agree with the preference against just subtracting numbers" [p.371]
- **STATED** (mechanism SHELVED, H-3)

**Agency-removing effects must be progressive and resistible.**
- *Rule:* Grapples, holds and charms advance along a track you can fight with stamina. No binary save-or-suck, and no instant paralysis.
- *Source:* "I'm not a fan of 5e's 'roll high on the d20 to have it do nothing, roll low to get completely fucked'." [p.152]. "anything that takes away agency should probably use some interactable progress mechanic that interfaces with existing mechanics like stamina." [p.1858]. "I don't want that to just *happen* immediately" [p.1277].
- **STATED** (mechanism SHELVED, H-4)
- *Current state:*
  - Control effects are TBD, and the extended-contest model is shelved [R2].
  - It's also open whether there will be universal conditions like "paralyzed", or whether each spell or ability explains what it does [R1:A16].

**Attribute-based control resistance must not reproduce 5e's saving-throw spread.**
- *Rule:* If an attribute helps resist control, it must not scale the way a defense value does. Repeated stamina spends multiply a defense value, so a high-attribute character would shrug everything off while a low one couldn't afford to resist. No single attribute should become the only answer to a whole category of control, the way the shield is to arrows today.
- *Source:* "I'm still a bit nervous about the 5e saving throw issue making stat-specific control mechanics really punishing because of how they'd scale if using something similar to melee defense… it's hard to not have repeated stamina expenditures multiply the numbers and make balance really unwieldy." And: "A bit nervous about having Will be 'the extended contest ability' - worried that'd make it like the mandatory shields of the current ranged attack implementation." [C:2026-11-05]
- **STATED** (the concern; the mechanism is open)

**Players need enough information to decide; telegraph lethal threats.**
- *Source:* "Games that have very tight mechanical systems like this seem like they only work if the players have enough information to make informed decisions… not being told… that an enemy is actually a badass capable of punching through their entire stamina bar in one hit sounds like it'd really suck." [p.231]. You later noted it's GM-dependent and "the numbers hide how deadly things are" [p.1286].
- **STATED** (principle). Mechanism unsolved.

**NPCs fight to survive.**
- *Rule:* Enemies that suicide into grazing hits make fights annoying for PCs, who carry injuries long-term.
- *Source:* "if a DM doesn't play NPCs with self preservation then each fight will be annoying because enemies will suicide into a grazing hit for a few damage and then die, but the players will be stuck with that injury for a while." [p.1286]
- **STATED**

**Positioning must stay live within a round.**
- *Rule:* Low HP plus coarse turns makes melee approach suicidal, so give reactive movement instead of shortening turns.
- *Source:* "how can people position aggressively with such large time increments for each turn? Making one turn represent less in-universe time than a 5e turn just seems like it'd just bog down combat." [p.762]
- **STATED**

### 3.3 Fiction and plausibility

**Skill, not luck, should decide decisive outcomes.**
- *Rule:* Crits come from expertise (Finesse widens the range) and from aiming. Hitting a vital spot is a skill.
- *Source:* "I didn't love that crits felt luck based when really a skilled rogue should be critting because of skill." [p.751]. "Crits aren't meant to just be random, they're meant to be hitting a vital spot." [p.1235]
- **STATED**

**…but aim must not be deterministic.**
- *Source:* "I don't want ranged aiming to be deterministic" [p.1142]. [p.1226]
- **STATED**

**Each tree's resources should key off a fitting stat; avoid narrative non-sequiturs.**
- *Source:* "why would a wizard recover from arcane strain with strength" [p.592]. Applied to recovery design. The final design moved to a single strain pool, but the principle stands.
- **STATED**

**Avoid gamey recharge loops that can't be narrated.**
- *Source:* "How do you feel about abilities that (re)charge by doing stuff? The idea makes sense mechanics-wise, but I find it hard to justify narratively." [p.537]
- **STATED**. You later reconsidered Draw Steel-style recharge [p.651], so it's a lean, not a ban.

**Grounded power scale: nothing on the attribute scale is superhuman.**
- *Rule:* Attributes describe real people.
  - 2 is an average person.
  - 9 is a world's-strongest-man contender.
  - 10, reachable only on skill checks, is the pinnacle of human ability, once in a generation.
  - No value represents heroic-fantasy or shounen feats.
  - A 0 is still an adventurer.
- *Source:*
  - "None of these are literally superhuman; maybe that's better as an overall explanation to say that none of these are like 'suplex 5000lbs' for a heroic fantasy/shounen themed game." [R7:AT-5]
  - "I'd like to stay away from magic/superhuman, especially by 6 or 7. A 9 should be the strongest man alive… think a 7ft tall Eddie Hall, not a comic book superhero." [p.743]
  - "Someone should still be able to be an adventurer with a 0 in a stat" [p.740].
- **STATED**
- *Evolution:* you originally put "strongest man alive" and "pinnacle" at 9 [p.743, p.1429]. With the +10 cap on skill checks, you toned 8 down, put that level at 9, and moved the pinnacle to 10 [R7:AT-5].

**A high attribute should feel like embodying it.**
- *Rule:* Grounded, but felt. A 5 or 6 should give a reward the player notices, not only a bigger number.
- *Source:* "This isn't a superhero game, but a 5 or 6 should *feel* like you're embodying that stat. Getting to recover 4 hp after a long hard day seems like it'd feel like a satisfying reward for playing the big guy." [C:2026-11-05]
- **STATED**

**Recovery is tuned to tone, not realism.**
- *Rule:* About 3–4 nights from incapacitated to full health, and about a week back from the brink of death, fits the game's tone. Healing speed can differ a lot between bodies.
- *Source:* "I can kinda see someone robust and healthy bouncing back from the same injurious event 4x faster than someone frail and unhealthy. I could even see it being more than 4x in the real world." On those recovery times: "it sounds like it'd probably be ok for the tone of this game? It's not meant to be *realistic* exactly." [C:2026-11-05]
- **UNCERTAIN** (a lean)

**Don't add a new spatial concept just to refine one rule.**
- *Source:* "I'm worried that tracking facing… won't be worth introducing a new concept just to refine the opportunity attack rules, since nowhere else does any concept of facing come up." [p.1349]
- **STATED**

### 3.4 Character building: arenas of play

**Don't make players choose between arenas of play, especially when the arenas are unequally represented in the mechanics.**

- *Rule:* When one build currency could buy either combat value or roleplay/exploration value, players will feel pushed toward combat, because combat is where the system's mechanics live. Keep separate currencies for separate arenas. Be wary of any ability, stat bonus or reward that crosses them.
- *Why:* The system is detailed in combat and deliberately thin elsewhere. A shared currency silently tells players "don't waste points on dancing". That breaks P4 and makes characters converge.
- *Test:*
  - Could a player spend this on a combat benefit *or* an out-of-combat or flavor benefit?
  - If yes, would the concept-faithful choice cost them combat effectiveness?
  - If both answers are yes, split the currency or move the option.
- *How it's applied now:*
  - **Expertise** (combat-relevant attributes) vs **Skill Points** (skill-check-only attribute bonus, skills, ribbons, extra spell/maneuver choices).
  - Caution against healing and party-buff passives competing with combat picks.
  - Caution against Intelligence granting Skill Points as a combat-stat reward.
- *Final form:* "I agree with the design bible section to include stuff like 'don't make players pick between things in different arenas of play, especially if those arenas are unequally represented in the mechanics'." [p.1493]. **STATED / ENDORSED**
- *Evolution:*
  1. [p.298] Origin as two point pools: "I'll call these 'skill points'… 'expertise points'". Plus the failure mode: "If you can spend less mechanically valuable 'roleplay' points… on getting your strength or agility up to 3 and doing so is a big advantage, then every character should do that, even ones who are supposed to be very small or very clumsy."
  2. [p.565] Generalized: "I don't want players to have to choose between spending character creation points/decisions on what's mechanically helpful… and what is an accurate representation of the character. If I have to spend skill points on dodging or on dancing and the system uses dodging a ton but never references dancing, the system is implicitly pushing players to not 'waste' resources on dancing."
  3. [p.1277] Extended to abilities: "to prevent the 'it's optimal to take the party buff ability but that's just a boring passive that doesn't enhance the experience of playing my character' issue when different arenas of play are impacted by abilities bought with the same character building resources". And to stat rewards: "I want to be careful treating the more roleplay-y arena of play skill points as a valid reward for spending mechanically heavy combat-y arena of play expertise points".
  4. [p.1409] Fictional justification: "A +3 int character from skill points is just as smart as a +3 int character from expertise points, but the latter knows how to apply that intelligence to stressful situations like combat".

**Crossing arenas, including time scales, is a red flag, not a ban.**
- *Rule:* An arena can be a kind of play (combat, exploration, social) or a time scale (one fight vs the campaign: rest, travel, downtime). A bonus bought in one arena that pays off in another needs a strong reason. Such crossings usually end with the value depending on something the player doesn't control: how often a situation comes up, or how the GM paces rests.
- *Source:* "There's nothing *inherently* wrong with crossing arenas of play, but it seems to usually lead to problems like this in some form, and I consider it a big red flag in a design. It's why I separated AP and EP from SP as early as I did in the design process (Starsector not doing this for in-combat and campaign map bonuses in its skill system is one of the few design qualms I have with it)." [C:2026-11-05]
- **STATED**
- *Applied:* Strength's odd values as +1 nightly HP recovery. HP is combat-relevant, but recovery's value depends on how many fights fall between rests.

**Related principles:**

**No auto-pick or mandatory attributes; don't hang core resources on one stat.**
- *Source:* "I don't want to have constitution be an auto-pick" [p.163]. "having Strength also give extra stamina might make it too important a stat for every build" [p.330]. "I don't think I want stamina regen tied to stats like strength since that's such a core stat it'd basically be mandatory." [p.783]. "it doesn't make sense to give such an important feature [stamina refresh] to any single one of them" [p.117].
- **STATED**
- *Note:* Max stamina ended up including STR via HP [p.1469, R3:11]. That's a deliberate small exception you accepted. You've since flagged STR's +1 HP as "suspect since this scales poorly at higher levels with the rest of the rules" [R1:A15].

**Overlapping sources must differ by when they work.**
- *Rule:* When two attributes feed the same thing, each needs a condition the other lacks. Otherwise the attribute with more bundled benefits wins.
- *Source:* "AGI also gives dodge and works when disarmed while FIN works fine when wearing armor. AGI gives movement alongside initiative while CUN will get some other undecided bonus to go alongside initiative." [C:2026-11-05]
- **STATED** (as the reasoning behind the current overlaps)

**Odd values give useful but optional bonuses; the most appealing bonuses go on even values.**
- *Rule:* A value-1 bonus costs 1 Expertise, so it must be worth having but never mandatory for anyone optimizing. Strong effects such as defense value go on even values.
- *Source:* "the odd values were given useful but not mandatory things - the really appealing options like defense number bonuses were intentionally put on even values. I'm not opposed to a lot of characters eventually buying level 1 in a range of stats, but it shouldn't be completely mandatory for anyone even thinking about optimizing at all." [C:2026-11-05]
- **STATED**

**Dumping should gain little, and being average should be cheap.**
- *Source:* "'dumping' intelligence should get them very little. If they want to play an average intelligence fighter, ideally it would be pretty cheap… so that it's very easy to not dump a stat unless you actively want to." [p.1434]
- **STATED**

**Many characters taking a point or two in most attributes is a healthy sign, not a failure.**
- *Rule:* It's what the principle above produces. The failure is skipping a point being crippling.
- *Source:* "is it really bad if most characters eventually want to take a point or two in most abilities? Not doing so shouldn't be crippling so we don't discourage oddball roleplaying too much, but if that's eventually good enough a good portion of the time, then that seems like it's maybe a sign of a well balanced and interesting array of choices?" [C:2026-11-05]
- **UNCERTAIN** (you asked it as a question)

**Don't force a roleplay identity on a build.**
- *Source:* "want to play a blaster? I guess you need to be book smart" (as a worry) [p.122]. Magic should be optional for anyone, and mental stats shouldn't be dump stats for non-casters [p.124].
- **STATED**

**One stat per skill, with clear boundaries.**
- *Rule:* Split a skill rather than let it float between stats.
- *Why:* Floating skills make players argue for their best stat, and GM-side adjustments are invisible to players.
- *Source:* "it'll just encourage players to always try to argue for their best stat" [p.39]. "it might feel bad to have the DM make ad hoc adjustments to the roll in ways the player can't interface with" [p.67]. GM exceptions are allowed "as an actual exception to the rules" [p.75].
- **STATED**

**Character building should have the same interplay as combat.**
- *Source:* "it feels like there's no interplay of mechanics present in character creation the way there is in the stamina-based combat… make character building more than just 'I pick the ability from the list'" [p.428]
- **STATED** (goal; method open)

**Purchases should feel like something happened.**
- *Rule:* Core features are strong and near-mandatory. Opening a new tree is worth more than going deeper in one.
- *Source:* "I worry it'll feel bad to spend an ability point and have nothing happen." [p.1687]. "I want to make them pretty good so they'd be nearly mandatory picks either way" [p.1673]. Ability-point purchases should be "an actual power boost rather than just being more versatile" [p.1054].
- **STATED**
- *How it's applied now:*
  - Tier-unlock abilities cost an AP and "will probably have minor benefits that fit the overall theme of the tree".
  - They also give a home to "fitting mechanics that people might not choose to unlock if given the choice to buy them normally" [R1:A14].
  - Unlocking a tree is just buying its first, core ability. There are no separate tier-tree unlocks [R1:B12, R2:8].

**Avoid "subclasses but more complicated" and GM-dependent builds.**
- *Source:* "If the packages are too clearly defined or don't have much ability overlap then I've just made subclasses but more complicated." [p.1605]. On the ranger problem, and on GMs' enemy choices skewing builds [p.1605].
- **STATED**

**Multiclassing shouldn't inflate resources, nor feel bad.**
- *Source:* Strain as "a shared resource pool… so you don't get more total ability usage by multiclassing" [p.998]. On a main-tree-only rule: "That'd make multiclassing kinda suck more than I want it to" [p.588].
- **STATED**

**Keep core-economy parameters uniform across characters.**
- *Rule:* Roles come from *efficiency*, not pool size.
- *Source:* "they'll each spend the same amount of stamina more or less efficiently at various tasks to define their roles" [p.334]. Class-varying regen "seems like a balance nightmare" [p.783].
- **STATED**

**Secondary stats should matter, unlike 5e's "one important stat".**
- *Source:* [p.1178]. "abilities will let each stat play a capable offensive and/or defensive role depending on character build, but the basic stat bonuses will lean in those directions" [p.1192].
- **STATED**

**Trees grant access; attributes set how much you get from each.**
- *Rule:* Attributes form a layer running on top of the class trees but not parallel to them. Your attribute spread decides how much you get out of each tree you open, and which parts of each tree are worth buying. A tree doesn't dictate one stat. Players mostly follow the parts of a tree they have the stats for, take the occasional off-stat ability that's especially strong or fitting, and plan their attributes to match.
- *Source:* "I really like attributes as a layer running on top of but not fully parallel to the trees - how you invest in attributes determines how much you can get out of each multi-tree and how valuable each part of the tree is. That kind of layering sounds like it's the sort of thing that adds depth to a character creation system." And from 5e: "Knowing which spells work well for multiclassing w/ lower casting stats and which are worse unless you invest in the stat was one thing I remember liking in 5e." [C:2026-11-05]
- **STATED**
- *Related:* rushing the main stat is the failure, not maxing it. "I'm not immediately bothered by an optimal wizard eventually wanting 6 INT, though if an optimal wizard always rushed 6 INT before going into other stats then that would be a problem." [C:2026-11-05]

**Spells and abilities: the core from the casting stat, riders from the ability's own stat.**
- *Rule:* A spell's core effect scales with the casting stat of the tree it's cast from. A secondary effect (the rider) is a fixed property of the spell and scales with the stat that fits its fiction. A spell shared between trees then suits some trees better than others with no special rule: a Cunning bard gets the most from a Cunning-rider enchantment without investing in another attribute. The core must stay worth taking at a low rider stat, and the rider must still make that stat worth having.
- *Source:* "Maybe an enchantment wizard spell gets to target extra people based off of your cunning and an abjuration ability gives a temp hp equivalent that increases with your will. If these are properties of the spell across trees then it could naturally make certain spells fit more easily into certain trees. A bard whose main stat is cunning wouldn't need to invest in another attribute to get the most out of the spell. This would require some attention to make the spell not useless for the enchantment wizard at a lower cunning while still making cunning useful." [C:2026-11-05] The core/rider split is Claude's framing of this.
- **ENDORSED**
- *Note:* some martial abilities may key only off mental stats. The pattern is a default, not a requirement.

**A stat's value from abilities counts only if anyone can reasonably take those abilities.**
- *Rule:* Builds may want some attributes more than others, but every attribute should give *some* benefit. "Used by abilities" counts as a core feature of an attribute only when those abilities are open to any build, not locked in one class tree.
- *Source:* "it's fine (maybe desirable) for some builds to want some stats more than others, but ideally there'd at least be *some* benefit to a stat. In order for me to feel comfortable counting 'used in abilities' as a proper core feature of a stat I'd want anyone to at least have the reasonable option of taking those abilities (even if many don't)." [C:2026-11-05]
- **STATED**

**Choices that aren't fun to make shouldn't be build choices.**
- *Rule:* Strain capacity is level-only. That's not because choosing it would be too strong; it's because the choice isn't fun.
- *Source:* "I think that strain will probably be solely level dependent. Not necessarily because it's too powerful to be given as a choice, but because that sort of choice is not very fun." [C:2026-11-05]
- **STATED**

### 3.5 Balance and GM

**Balance must hold up across GM pacing, rest frequency and fight length.**
- *Source:* "this DM's style of running a game is making my character randomly weaker or stronger, which isn't something I can really plan around… I do want the game balance to be resilient to a range of combat lengths" [p.1097]. The 5e adventuring-day problem [p.441]. Rest frequency skewing classes [p.472].
- **STATED**

**A long-term resource is acceptable when the player can cash it in within any one fight.**
- *Rule:* Prefer long-term resources whose worth falls to zero under sparse pacing rather than becoming a trap. The player can always spend them inside a single fight.
- *Contrast:* 5e's short-rest resources quietly become long-rest resources when there's one encounter a day. High HP recovery doesn't break that way: with one fight a day, the player spends it by accepting more wounds, knowing they'll heal tonight.
- *Limit:* This removes the trap, not the variance. With long gaps between fights everyone heals fully anyway, and the bonus is worth nothing.
- *Source:* "the player can to some extent still get value out of high recovery by taking more damage in a once-a-day fight at no penalty, while short rest resources just unavoidably become long rest resources if there's only one encounter per day." [C:2026-11-05]
- **STATED**

**No mechanic should push the group or GM to adjust pacing to keep one player on an equal footing.**
- *Rule:* If one character's rest or recovery needs set the party's downtime (the slowest healer decides when everyone moves on), the table feels pressure to change its pacing so as not to be "mean" to that player. Treat that as a design failure, whichever character it falls on.
- *Source:* "I don't like it when a mechanic kinda pushes a group or GM to adjust things like pacing to 'put everyone on a fair equal footing' because they don't want to be 'mean' to a player." [C:2026-11-05] It generalizes strain's intent that one class's rest needs shouldn't hold the party hostage [p.553, p.1041].
- **STATED**

**Imperfect, uneven scaling is fine, even good, if it means fewer special rules.**
- *Source:* "things not being 'perfectly balanced' and scaling unevenly can often make a system way more fun to interact with because there are interesting bumps to find that haven't been 'sanded off'… It also lets you make fewer very specific rules, which is a big plus." [p.1066]
- **STATED**

**Opt-in complexity is OK only if it isn't the optimal path.**
- *Source:* Over-specializing is "opt-in (as long as it's not the actual optimal choice, which I want to avoid)" [p.1059].
- **STATED**

**Don't add asymmetry until there's evidence for it.**
- *Source:* "probably fine to not do that unless I see an active reason to." [p.1697]
- **STATED**

**Express differences as tendencies, not special rules.**
- *Source:* "> Notice I never needed a rule saying: Divine spells cost less stamina. It's just that many divine spells happen to. — Yeah, that's exactly what I had in mind." [p.1097]
- **ENDORSED**

**Dice are the GM's tool.**
- *Rule:* Don't gate when rolls happen. Avoid mechanics tied to roll frequency or strict pass/fail.
- *Source:* "I want to preserve the dice as a tool for the DM to employ however they see fit, even if it's just to establish a vague vibe" [p.1452].
- **STATED**

**Give GMs balance-tested defaults they can override.**
- *Source:* NPC profiles: "This gives the DM a balance tested default that implies the best way to play the system, but still lets them override that" [p.1294].
- **STATED** (in a proposal). The NPC-profile mechanism is **SHELVED** (H-6) [R2].

**PCs and humanoid NPCs share mechanics.**
- *Source:* "It'd feel weird to not have them use the same mechanics, and having them function differently might make it hard to make abilities that interact with an opponent's stamina." [p.241]
- **STATED**

**High-level characters should dominate low-level ones.**
- *Source:* [p.1388]
- **STATED**

### 3.6 Complexity and presentation

**Limit numbers that change constantly; avoid non-integer math, percentages and per-weapon lookup tables.**
- *Source:* "I don't want players to need to keep track of too many changing numbers" [p.1059]. "even '50% more expensive' is more mentally taxing than '+2 stamina'" [p.1066]. "I'd prefer not to require more complicated multiplication of non-integer numbers." [p.598]. "So I'd need another table to track for each weapon die?" [p.517].
- **STATED**

**A recurring rule must earn its per-attack cost, or it'll be resented or forgotten.**
- *Source:* "I worry the rule will either end up adding a new annoying thing to calculate or wind up forgotten." [p.1720]
- **STATED**

**Mirror the existing attack engine rather than adding a second resolution system.**
- *Source:* "I'm a bit nervous adding another resolution system like this - 5e's separation of attack roll vs saving throw comes to mind" [p.1909]. "The contested 2d12 rolls feel like they're rolling two sets of dice just to give each person something to do" [p.1878].
- **STATED**

**Defenses should draw on several sources, not one stat.**
- *Source:* "vs normal attacks, where multiple stats contribute and archetypes with low raw defense numbers can wear armor or cast defensive spells" [p.1949]. [p.1979]
- **STATED**

**Resolve every offensive step before any defensive step.**
- *Rule:* The attacker does everything first: declare the target, declare stamina, roll, and add up the total. Only then do reactions such as diving for cover or declaring blocks happen.
- *Source:* "Keep all relevant offensive steps (declaring target, declaring stamina, rolling, adding up total) before defensive steps (reactions like diving for cover, declaring blocks, etc)." [R1:B11]
- **STATED**. No reason given. *My reading:* the defender always decides with full information, which fits "players need enough information to decide".

**Names shouldn't mislead or collide.**
- *Rule:* Avoid a term that means something different in D&D, or that overlaps an existing resource name. A term should also read naturally at the table.
- *Source:*
  - "Ideally don't call them actions since that'll be misleading" [R1:A4].
  - "Exertion might compete with strain and stamina in terms of overlapping meaning… it's a bit awkward to say 'I've done 4 exertions this turn'." [R2]
  - "Just call it an 'action' for now and make a note of the issues (misleading compared to D&D, implies multiple attack steps are treated as separate actions, etc)." [R7:CB-2]
- **STATED**. "Action" is a known compromise, not a choice.

**The core rules should be interesting on their own, without leaning on a big list of abilities.**
- *Rule:* The tactical interest should come from the shared core systems (stamina, commitment, blocking, movement), not mainly from a large catalogue of class abilities or spells.
- *Source:* "I'd like the core rules to be interesting without leaning on a big list of abilities" [R8].
- **STATED**
- *Related:* "It's possible I'll move the design in a direction without magic… but currently I'm guessing there'll be something like what you described." [R8] So magic's scope is open (§5).

**Keep the out-of-combat layer thin.**
- *Source:* "Is it weird to tack a thin 'roleplay arena of play' set of mechanics onto this detailed combat system?" [p.1402]. "mainly for out of combat (which will be rules light) purposes/roleplay" [p.132].
- **STATED** (framing; ChatGPT strongly agreed)

**Rules text: one home per rule, in your voice, with non-mechanical explanation where it helps understanding.**
- *Source:* [p.1474], [p.1546]
- **STATED**

---

## 4. Rejected alternatives (decision log)

| Rejected idea | Why | Replaced by | Ref |
|---|---|---|---|
| D&D-style 6 stats; Constitution; Charisma | Can't express nuanced concepts; Con would be an auto-pick; presence fits the mental stats | STR/AGI/FIN/INT/WIL/CUN | p.1, p.9, p.163 |
| Build as "size" | Wanted power, not bulk | Strength | p.9 |
| Stat as skill ceiling | Doesn't capture talent *and* training | Stat + skill added | p.39 |
| Stat substitution / approach-based skills | Players argue for best stat; invisible GM adjustments | One stat per skill, GM exceptions | p.39, p.67, p.75 |
| Dice pools | Too fiddly | Single roll + modifiers | p.39, p.87, p.774 |
| 5e Extra Attack alongside the stamina triangle | "messy and unnecessary" | Attack steps | p.176 |
| Separate to-hit roll | The damage roll *is* the attack; blocking is deterministic | No to-hit | p.783 |
| Diminishing damage/blocks per step on top of rising cost | Double penalty | Constant per-step amount | p.804, p.809 |
| Arrows only draining stamina | Can't be justified narratively | Arrows wound; cover, shields, blocking | p.186 |
| Regen as 1/3–1/4 of max | Breakpoint-sensitive | Half max, then flat 4 + round(level/10) | p.218, p.1469 |
| Stat-based or class-based regen | Makes STR mandatory; balance nightmare | Uniform regen | p.783 |
| Start-of-turn regen | Lets players zero their defense; wastes first regen; rewards going second | End of turn | p.127, p.788 |
| Full refresh / "do nothing" turn | Doing nothing sucks | Partial regen | p.221 |
| Four layers of max stamina; separate max-stamina damage track | Too much tracking | Max stamina = 6 + current HP + round(level/5). Damage reducing max stamina is shelved (H-2), not rejected | p.105, p.998, p.1277; R1; R3:11 |
| Max-stamina costs on ordinary abilities / as the casting limit | Cripples you after using abilities | Strain with stamina overage | p.446, p.474 |
| Overexertion (lower max stamina to gain stamina) | Superseded | Strain overage | p.334; R3:8 |
| Per-rest or per-fight uses for class cores | Rest-frequency imbalance; dislikes "X fights per rest" | Strain-cost cores | p.464, p.585 |
| Per-tree strain pools with stat-keyed recovery | Multiclass inflation; non-integer math | Single shared pool | p.588–598, p.998 |
| Fractional "commitment coefficient" for heavy weapons | Needs per-die tables; later steps cost more and give less | Base cost + stat multiples | p.517 |
| Stat applied once per attack (not per step) | Breaks multi-target attacks | Stat per step | p.522 |
| 5e double-damage crits; reroll-chain crits | Doesn't fit; infinite damage at high FIN | Armor ignore + HP doubling after cap | p.751, p.754 |
| Pure-luck crits | Crits should be skill | FIN crit range; aim | p.751, p.1235 |
| Deterministic aim (flat FIN per step) | "barely any uncertainty" | 1d6 + FIN | p.1226 |
| Growing aim die (d4→d12) | More aim would mean fewer crits | 1d6 + FIN | p.1226 |
| "Pressure" vs "Wound" as two tracked numbers / game terms | Not tracked separately; just a cap | "damage" (the Max HP Damage cap itself is shelved, H-1) | p.1200, p.1471; R1:A2 |
| Shorter in-world turns to fix dogpiling | Bogs down combat | Off-turn movement | p.762 |
| Paying stamina for normal on-turn movement; aim penalty for moving | Don't discourage movement | Free on-turn movement | p.1274 |
| Facing; "maneuver" keyword; free disengagement | Facing is a new concept used nowhere else | Pay stamina to deny OAs (now per enemy per square; see §4.1) | p.1349, p.1355, p.1361 |
| Main-hand shield rule | "not important enough to need a rule" | One shield, +2/+2 | p.1481 |
| Extra strain for buying school ranks early | Wrong resource | Stamina surcharge | p.1059 |
| Stamina-cost reductions on mastered spells | Growing pools cover it | Strain reductions only | p.1059 |
| Percentage surcharges | Mentally taxing | Flat surcharges | p.1066 |
| Stamina refund next turn for big spells/shots | Bookkeeping | (dropped "for now") | p.1072, p.1142 |
| Blanket spell discount for gishes | Too broad | Specific hybrid abilities | p.1090 |
| Hard rules for tradition differences | Unnecessary | Tendencies in spell lists | p.1097 |
| Skill permission gates; Daggerheart-style hope/fear; strict DCs | Restricts GM use of dice | GM-discretion rolls | p.1452 |
| +2 per skill rank; hard caps on specialization | Number inflation; soft caps suffice | +1 per triangular rank | p.1439 |
| Skill-point attribute bonus 0–3 at 2/4/6 | Dumping too cheap to avoid | 0–4 at 1/2/4/7 | p.1434–1439 |
| Stat-subtraction injuries | Unfun "just subtract numbers" | Injuries that change options (shelved, H-3) | p.368, p.371 |
| Quick-killing wounds in the top injury tier | That tier is for lasting harm | "Permanent" tier (shelved, H-3) | p.386 |
| Opposed 2d12 rolls for control effects | Dice just to give both sides something to do | Attack-like control (shelved, H-4) | p.1878 |
| Control damage-disruption at 1 per 5 damage | HP is ~6, so it's too weak | 1:1 (shelved, H-4) | p.1923 |
| Control defense = 1 + attribute | Too swingy; multiplies weak saves; GM-dependent | (open; shelved, H-4) | p.1949 |
| 5e save-or-suck | All-or-nothing | Progressive control | p.152, p.1858 |
| Separate tier-unlock currency / auto tiers every 10 levels (post-export, ChatGPT's); unlocking "tier trees" as separate things | You wanted no special point type | Tier-unlock abilities bought with AP; core abilities cost +1 AP per core owned | p.1649; R1:A14, R1:B12, R2:8 |
| Dash action / escalating extra on-turn movement (ChatGPT's) | Wrong chase dynamics | Flat 1 per extra square; +1 square per purchase per odd AGI | p.1706–1712; R3:6 |
| "Exertion" as the name for an on-turn step | Overlaps stamina and strain; awkward to say | "Action" (provisional; issues noted) | R2; R7:CB-2 |
| Flat −1 AGI/FIN/CUN armor penalty | (not stated) | −1 FIN and −1 AGI per STR below a threshold (placeholder) | R1:A15; R2:5 |
| ChatGPT's dying track (death at 3 Shock, +1 per round) | (not stated) | System Shock: start at negative HP, roll each turn, die at 10 Shock or −10 HP | p.608–612; R2, R4–R6 |

*ChatGPT's own suggestions that you simply never took up aren't listed here. They're not "rejected"; they just aren't canon. See §8.*

### 4.1 Decisions your rulings reversed

These are earlier settled positions that the rulings changed. Each is recorded so the old reasoning isn't mistaken for the current rule.

| Earlier position | Now | Ref |
|---|---|---|
| OA avoidance paid per decision [p.1355], then once per enemy per turn [p.1361] | 1 stamina per enemy per square left, flat | R1:A3; R3:1 |
| No Finesse requirement to OA with heavy weapons ("reach already widens the window") [p.1375] | An OA spending cap of 1 + odd FIN means bigger-weapon OAs effectively need Finesse or an ability | R1:A8; R2:1 |
| Packet: +1 stamina available for OAs each round | Cap on spending per OA, as above | R1:A8 |
| Packet: each ranged shot surcharged, aim steps exempt | Shots cost a flat base; aim steps are surcharged actions | R1:A4 |
| Packet: off-turn movement has its own progression | Off-turn movement and OAs share one off-turn track | R1:A6; R1:B4 |

### 4.2 Shelved, not rejected

These are deliberately out of the current rules, but they're candidate solutions to raise when their problem comes up. Details are in the ledger's Part H.
- **H-1 Max HP Damage:** caps how much of an attack can wound. It's your initial proposed fix for ranged aim lethality, and it differentiates STR, AGI and FIN [R1:A2, R2:11].
- **H-2 Damage reducing max stamina:** would allow "out of the fight" before 0 HP. Excluded for complexity, "but worth seriously considering" [R1].
- **H-3 Lingering and permanent injuries** [R2].
- **H-4 Control effects / extended contests** [R2].
- **H-5 Spellcasting:** overall ideas only [R2].
- **H-6 NPC aggression profiles** [R2].

---

## 5. Recurring tensions and open questions

These are the threads you kept returning to. Most are unresolved. Item 1 is the problem you said you want to tackle first.

1. **Ranged aim lethality.** Aim adds damage, and nothing currently stops that damage from wounding.
   - You called this an unsolved problem and "one of the first I have Claude try to help me solve".
   - Max HP Damage (H-1) is your initial proposed fix [R2:11, R1:A2].
2. **Arithmetic load of the core attack.** The tension at the heart of C1:
   - "Is this sort of stamina math going to be annoying?" [p.987].
   - "potentially a lot more than even Pathfinder or GURPS" [p.2036].
   - Reference tables were accepted; tokens are an option.
3. **Is each subsystem worth its complexity?**
   - Per-weapon triangles, strain and the max-stamina track [p.998].
   - Max HP Damage [p.1720]. Now shelved, partly for this reason.
   - Control [p.1967]. Now shelved.
   - Earlier: stats in everything [p.145].
   - Damage reducing max stamina was shelved for complexity [R1].
4. **Telegraphing lethality with numbers that hide it**, given GM variance and homebrew monsters [p.231, p.917–921, p.1276, p.1286]. Unsolved.
5. **Mental stats' combat role.** "These still don't feel solved to me" [p.853, p.1277, p.1909]. They're "just not fully defined"; Cunning's initiative bonus is a placeholder [R1:B10, R2:6].
6. **Expression vs optimization in builds:**
   - Agility as a universal stat [p.308].
   - Two kinds of the same attribute (Expertise vs Skill Points) [p.1409].
   - Skill value depends on how skills are split and how often they come up [p.1446].
7. **Rest and long-term resources:**
   - Should rests be tied to a night? [p.441, p.553]
   - Should long-term resources exist at all? [p.726, p.998]
   - Per-rest parity between martials and casters [p.472, p.1128].
   - Strain recovery: per night, or 1 per 6 hours of rest [R1:B14, R2:9].
8. **Breadth vs depth** for casters and trees:
   - Spell variety without slots [p.354, p.530]. Spellcasting as a whole is shelved for now (H-5).
   - Tier-unlock nodes, multiclass cost [p.1644–1697].
9. **One-round vulnerability vs multi-round hangover** after big spells or aimed shots [p.1090].
10. **Numbers scale:** keep ±1 meaningful vs give room for growth [p.1380–1388].
11. **Initiative fairness:** do higher-initiative characters suffer [p.249, p.255]? Standoffs at the start of combat [p.227].
12. **Whether there's a KO state before 0 HP** [p.112, p.339–343, p.603–611].
    - Below 0 HP is now settled: System Shock [R2, R4–R6].
    - Still open: an "out of the fight but alive" state above 0 HP. Your stated concern is characters only "going down" when they hit 0 HP [R1]. H-2 is the candidate.
13. **Control effects:** procedure and defense number [p.1858–1979].
    - Now TBD, with extended contests shelved (H-4) [R2].
    - Also open: universal conditions vs self-describing effects [R1:A16].
14. **Keeping Strength relevant at high levels without overpowering it early** [p.1156]. STR's +1 HP "scales poorly at higher levels" [R1:A15].
15. **Rogue vs Fighter as movement-punishers** (OA identity) [p.1369].
16. **Combat as sport vs war;** pre- and post-fight phases [p.1567].
17. **Ability selection that isn't obvious,** without abstract Slay the Spire-style mechanics [p.1587–1616].
18. **Naming the on-turn step.** "Action" is provisional: it's misleading next to D&D and implies each attack step is a separate action [R7:CB-2].
19. **Dodge's place in the system** is marked uncertain [R2:7].
20. **Magic's scope.** You may take the design in a direction without magic; for now you expect something like the shelved spellcasting ideas (H-5) [R8].

---

## 6. Inspirations and comparisons that shaped decisions

Only cases where you drew a conclusion. Pure research asks are omitted.

- **D&D 5e**, mostly as the thing to improve on:
  - **Rejected or avoided:**
    - the six-stat groupings [p.1];
    - save-or-suck [p.152];
    - Extra Attack [p.176];
    - rest/adventuring-day class imbalance [p.441, p.1041, p.1097];
    - unavoidable damage making lingering injuries unfun [p.339];
    - separating skill and tool proficiency [p.22];
    - attack roll vs saving throw split [p.1909];
    - weak-save swinginess [p.1949];
    - the ranger problem [p.1605];
    - the "one important stat" [p.1178];
    - HP-restoring spells like *Healing Word* and *Cure Wounds* [R2];
    - "action" as a fixed per-turn slot, which is why the name is only provisional here [R7:CB-2].
  - **Kept as reference points:**
    - turn length as the baseline [p.762];
    - cover values [p.1217];
    - initiative flow [p.1481];
    - conditions list [p.1277];
    - spell schools "for now" [p.1033];
    - hybrid classes as targets for multi-tree builds [p.410];
    - spell slots valued for encouraging variety [p.354, p.530];
    - class level ≈ tree tier; battlemaster dice ≈ Ability Point purchase [p.1054];
    - Sentinel as the model for OA-control feats [p.1375];
    - spell-level power buckets [p.1697].
- **Call of Cthulhu:** arbitrary skill granularity makes some concepts cheap and others expensive [p.22, p.1446].
- **Game of Thrones named characters vs mooks:** the combat-feel model [p.1277].
- **Eddie Hall:** calibration for Strength 9, a world's-strongest-man contender [p.743]. 10 is now the once-in-a-generation pinnacle [R7:AT-5].
- **Heroic fantasy and shounen:** the anti-reference for the power scale. Nothing like "suplex 5000lbs" [R7:AT-5].
- **Reddit r/RPGdesign comment on a stamina dice-pool system:** the closest precedent. You distinguished yours (no dice pools; more interesting than an action-point economy) [p.774].
- **Daggerheart hope/fear:** rejected as roll-frequency-dependent [p.1452].
- **Draw Steel class resources:** considered as activity-based recharge [p.651].
- **Slay the Spire:** cards interfacing with shared mechanics as a model for ability synergy, but your mechanics must stay plausible [p.1587].
- **Pathfinder 2e / GURPS:** benchmarks for attack-arithmetic complexity [p.2036].
- **Ars Magica, Dark Souls TTRPG, Savage Worlds, FFT, Ironsworn, Cairn, Numenera:** asked about, with no stated conclusion. Reference only.

---

## 7. Gap check: the packet's "What This Game Is Trying To Do"

**What the packet says:**
- tactical decisions over big HP pools or random defenses;
- survive by managing stamina, choosing when to commit, recognizing danger;
- most attacks are dangerous;
- deaths feel earned, not arbitrary;
- lighter out-of-combat rules with GM judgment.

**What matches:** all of it is consistent with your statements. Deterministic blocking is the "no random defenses" point. Commitment, earned deaths and the light roleplay layer all match.

**Gaps (stated goals the section omits):**

| Missing goal | Your source |
|---|---|
| Stamina *is* your defense; one pool pays for everything (P1) | p.87, p.722, p.1826 |
| "Named characters, not mooks": real danger without random risk, and an explicit, deliberate departure from realism in favor of awareness and agency (P2) | p.1277 |
| No punishment for fights players had no agency over; lasting injury is justified *because* damage is avoidable. Injury mechanics are now shelved; slow HP recovery and no HP-restoring magic remain | project brief; p.339; R2 |
| Mechanics read as plausible events in a fight; simulationist leaning (P3) | p.537, p.639, p.1587 |
| Positioning is live all round; aggression shouldn't be suicidal | p.91, p.762 |
| Build the character you imagine; arenas of play (P4) | p.298, p.565, p.1493 |
| Low arithmetic and decision load (C1) | project brief; p.87, p.2036 |
| Balance resilient to GM style, rest frequency and fight length | p.1097, p.441 |
| Agency-removing effects are progressive, never instant (mechanism now shelved) | p.1858, p.1277; R2 |
| Grounded power scale, never superhuman; high levels dominate low levels | p.743, p.1388; R7:AT-5 |
| Below 0 HP is deadly but survivable for a window (System Shock) | p.339, p.342; R2, R4–R6 |
| Players get enough information to make tactical calls (telegraphing). The packet has this only under "Running the Game" | p.231 |

**Nuances:**
- "Most attacks are dangerous": your framing is that most attack damage is *pressure* that costs stamina, with injury capped and rarer [p.1200]. Consider "most attacks are threats you must answer".
- "Characters stay alive by… recognizing danger before it becomes fatal": this leans on GM telegraphing, which you flagged as unsolved [p.1286].

---

## 8. ChatGPT-coined principles you never endorsed (keep out of the bible unless you adopt them)

These sound like house rules but are ChatGPT's. Some are worth a look.

- "Combat is a contest of commitment rather than chance… Wounds are rare but decisive" (the manifesto draft) [p.1285]. *Note:* at p.1284 this passage follows a "You said:" label. That label is ChatGPT quoting you inside its own reply, so the text is ChatGPT's, not yours.
- "Deadly, fair, tactical" tagline [p.1579].
- "Every subsystem should primarily create decisions, not merely constrain outcomes" [p.1748].
- "Don't create a second resolution system; create a second type of result" [p.1934].
- "Put precision where players interact, abstraction where the GM builds opposition" [p.2006].
- "Every recurring mechanic should justify its recurring cognitive cost" [p.2019]. Close to your own p.1720 worry.
- "Reactive movement improves your position but never fully invalidates a committed attack". A generalization of your 3/4-cover rules [p.1320]; you didn't respond.
- "Class determines what you can do; stats how well; weapons the kind of threat" [p.1375–1380].
- "Skills should represent methods, not subjects" [p.1455].
- "Keep frequently-subtracted numbers small" [p.1392].
- "Abilities should reference the player, allies, enemy *state* and the battlefield, not enemy type or saves" (ranger-problem fix) [p.1613].
- Stat-threshold hierarchy for abilities (natural scaling, then riders, then rare hard minimums) [p.1627].
- "Combat as Duel" framing [p.1566].

---

*Research basis for this format: design-pillar guidance (3–4 short, testable experience rules that can reject features) and design-decision logging (record the decision, the rationale, and the alternatives with why each was rejected).*
