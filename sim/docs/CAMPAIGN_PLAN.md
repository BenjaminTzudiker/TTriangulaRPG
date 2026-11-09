# Adventuring days: brainstorm and phased plan

*Status: proposal (2026-11-07). The designer's rulings of 2026-11-08 and the design chat's Party Day Study (2026-11-08) are folded in. Not yet part of the milestone plan in `ENGINE_PLAN.md`. Paths below are relative to `sim/src/stamina_engine/` unless they start with `sim/`, `rules/`, `design/` or `claude/` (the claude.ai project's files).*

## Context

Every simulated fight today starts fresh: full HP, stamina at maximum, strain 0 (`model/state.py:98`, `model/derive.py:228`; Assumptions rows "Strain at a fight's start" and "Stamina and strain at the start of a fight", ENGINE_PLAN:487 and :510). Agents price an injury with a constant `w` (3) against stamina (`agents/blocking.py`), and the ability policies fire on in-fight heuristics only (`agents/ability_policy.py`). So the engine measures every fight as if it were the only one, and that hides the costs the packet puts between fights:

- **HP is the bridge.** Maximum stamina = 6 + *current* HP (Packet: Stamina), so a wound carries into the next fight as a smaller defense pool. HP comes back only by resting, 1 + odd-Strength per night, with no healing magic (Packet: Rest and Healing).
- **Strain is a day budget.** It recovers only overnight, and each point over maximum adds stamina to every strain ability (Packet: Going Over Your Maximum Strain). The cores suite already says its numbers are "best cases for a day of several fights" (`sim/reports/cores_suite_notes.md`).
- **Death and convalescence.** The review found a typical loser ends at −3 HP and needs 9–11 nights to be whole, and the winner is wounded 15–40% of the time (`design/Review_Playtest_Packet_v0.9.md:240`).

Several open questions can only be answered across fights:

- Open Questions: "Strength's nightly HP recovery: its value depends on how many fights fall between rests."
- Design Notes 3.5: "Balance must hold up across GM pacing, rest frequency and fight length", and a long-term resource should lose value under sparse pacing rather than become a trap.
- Design Notes open problem 7: per-rest parity between martials and casters.
- Running the Game (GM-1): an NPC that trades grazes "dies quickly, but the players are left carrying the injuries."
- Encounter guidelines are listed as missing GM material.

## Prior work: the Party Day Study

A design chat already ran adventuring days by hand (`claude/Party_Day_Study.md`, following `claude/Fight_Series_Study.md`). Its setup:
- a party of three: sample fighter, greatsword, unarmored duelist;
- up to six random encounters on an open map: four mooks, two bandits, a level-30 brute, a skirmish;
- HP carried over between fights, with a 50% chance of a night (+2 HP each) between them;
- the day ends at the first drop.

It ran under candidate RuleSets built from plugins. What it found changes this plan:

1. **Drops come from spikes, not attrition.** The party beats two bandits 93–99% of the time, yet someone drops in about 60% of fresh fights, because the foes focus fire on the softest PC (MD 2–3). Days end at fight 1 or 2 "long before HP attrition matters": only 2–5% of six-encounter days finish without a drop, and the party clears 1.1–1.7 fights per day. Until defense values change, a campaign layer would mostly measure first-fight spikes.
2. **The study proposes a target:** in a fresh medium fight, someone drops at most about 15–20% of the time. No encounter it ran with real foes meets that target with this party, except mooks.
3. **The myopic agent's HP price is already close to right.** The study's exact duel series puts the best price over a series near 1 HP = 3 stamina, and one fixed price fits 88–91% of the best decisions. Pricing HP for later fights is worth less than this plan first assumed. Strain pricing is untested.
4. **Agents don't protect soft allies:** no formation, no body-blocking. The study's open question, whether this lethality is tactics a party can answer or punishment, needs an agent that holds a line.
5. **Big hitters kill when they drop someone** ("dead ≈ dropped"). Deaths against focus fire are fewer than drops (24% against about 60% at base 8).
6. **It built exact tools the engine lacks:** `series.py` (the best play over a series of duels) and `calc_unanswerable.py` (the share of a fresh PC's defenses a monster's all-in beats). They're in `claude/block_study/day_study_bundle.txt`, not in this repo.

So the order changes. First the engine has to run the current packet. Then encounters get calibrated, and a party gets an agent that can protect its members. Only then do carry-over results mean much.

## What the simulation is not

It measures how the rules spend and restore HP and strain over a run of fights. It doesn't simulate a campaign:

- **Pacing is given, not chosen.** The schedule of fights and nights comes from a pacing profile, as a GM would set it. The party never decides to rest or press on, because that choice means little without time pressure, and time pressure is the GM's to set (ruled 2026-11-08).
- **A dead character stays dead and the party carries on a person short** (ruled 2026-11-08). Real tables bring in a new character, change plans, or end the campaign. So the death *rate* is a fair measure of danger, but what a death does to the rest of a campaign can't be read from these numbers.
- **One level throughout.** No experience, no levelling, no loot.

Every campaign report repeats these three points.

## Refining the chats' ideas

| Chats' version | Refinement | Why |
|---|---|---|
| 50% chance of a night between fights | A **pacing profile**: a distribution of fights per day (including days with none) and of downtime nights between days | A coin flip is memoryless (fights per day geometric, mean 2) and never gives travel days, which heal too. Named profiles let a result be reported "across pacing", which Design Notes 3.5 asks for |
| One profile | At least three: **sparse** (about one fight per day, frequent downtime), **standard** (the chat's), **dungeon** (four to six fights before any rest) | A result that changes rank between profiles is itself a finding |
| The day ends at the first drop (the study) | A pacing-profile option, `day_ends_on_drop`, off by default | A party with someone down plausibly stops for the day, and it reproduces the study. It's still given pacing, not a party choice |
| "Lopsided" fights | Encounters **tagged by their measured fresh-party cost**, against the study's target: in a fresh "medium" fight someone drops at most about 15–20% of the time | Makes "lopsided" reproducible, and the calibration table is a first draft of encounter guidelines |
| +2 HP a night for everyone | The whole **Rest and Healing** rule: HP by Strength, strain by level | Strength's odd values are what question 1 asks about; strain matters for every class core |
| Six fights | Run until the campaign ends: a fixed number of fights or days, or the party losing a fight; report by fight index | Survival curves show attrition where totals hide it |

## Brainstorm: what to measure

| # | Question | Measure | Packet or design source |
|---|---|---|---|
| 0 | **Does attrition matter yet?** | Drops split by entry state: PCs who drop from full HP, against PCs who carried a wound in. Fights until the first drop | Party Day Study finding 1 |
| 1 | What is an odd Strength value worth? | Paired campaigns, STR 2 vs STR 3 (and 0 vs 1), by pacing profile: fights lost, characters down, fights fought below full HP, nights out of action | Open Questions; Design Notes 3.4 |
| 2 | Do class cores hold up over a day? | Overage paid in stamina by fight index; win and down rates in fights 1, 2, 3+ of a day; the cores-vs-cores table re-run under each pacing | Going Over Your Maximum Strain; cores suite |
| 3 | Is there a death spiral across fights? | Win rate by entry HP; the chance a wounded PC goes down next fight, against a fresh one; and how often the wounded PC is the one foes target. With `lowest_stamina` or `focus` targeting, a carried wound (a smaller maximum stamina) makes a PC the next target | Stamina (max uses current HP); F7; the study's focus-fire finding |
| 4 | How long is convalescence? | Nights out of action per campaign; nights from 0 HP and from System Shock to full | Design Notes: "3–4 nights from incapacitated, about a week from the brink"; review line 240 |
| 5 | Does pacing reorder builds? | Rank correlation of builds (armor, shield, high-Agility duelist, Strength builds) between sparse and dungeon | Design Notes 3.5 |
| 6 | What does a grazing block really cost? | The exact series price (the study: about 3 stamina per HP, fitting 88–91% of decisions), checked against what does best in campaigns | Blocking; Ledger on grazing as the attrition option |
| 7 | Do NPC profiles that flee spare the PCs? | PC HP lost per fight and characters down per campaign by NPC profile (berserker, disciplined, cautious) | Running the Game (GM-1); H-6 |
| 8 | How often do named characters die? | Deaths per 10 fights, by pacing and difficulty mix; how many downed PCs the after-fight stabilization saves (expected against focus fire, hardly at all against big hitters, which kill outright) | What This Game Is Trying To Do ("they do sometimes die, but they have to be pressured") |
| 9 | Encounter guidelines | For each encounter: fresh-party drop and death rates against the 15–20% target, and the same at entry HP 50%; who drops, by build | GM material (Open Questions); the study's §2 table |
| 10 | **Can a party protect its soft members?** | The study's encounters on a map with a defensible gap, a line-holding party against today's agents: drop rates of the soft PC | Party Day Study finding 4; P2 (danger you can see and answer) |

## Engine design

### First: a preset for the current packet

The engine still runs v0.9 rules where a campaign needs current ones (Packet v0.9.1–v0.9.3, all marked *Engine: not implemented* in the changelog):

| Rule | Engine today | Packet now |
|---|---|---|
| Maximum HP | 6 + Strength (`V09Resources.hp_max`) | 8 + 2 per even Strength value |
| Nightly HP recovery | None (no rest) | 1 + 1 per odd Strength value, also below 0 HP |
| Dying roll | 2d12 + Strength (`rules/components/dying.py`) | 2d12 + Will |
| Critical hits | Double after armor (`crit/double_once`); `crit/per_die_bonus` adds its bonus even when nothing gets through | +1 per critical die, only if anything gets past blocks and armor |
| Opportunity attacks | Capped (1 + odd Finesse) | No cap |
| Extra on-turn movement | 1 + odd Agility squares per purchase (`movement.extra_squares = "one"` exists, not in the preset) | 1 square |
| Initiative | 2d12 + odd Agility + odd Cunning | 2d12 + Cunning |

Each becomes a new component kind or value, never a changed default (CLAUDE.md: released defaults never change), under a new preset named for the packet version (`v0.9.3`). That's a rule-component change, so it goes on a branch with a pull request. It helps every suite, not only campaigns. The study's plugins (`exp_block_study.py`, the `cand-crit1-hp8` RuleSet) are the reference for matching its numbers.

### Where it lives

- **The campaign is an experiment layer above `Battle`**, like the runner and sweeps: `experiments/campaign.py`. It never runs a turn itself; each fight is an ordinary `Battle` built from an ordinary scenario.
- **What happens between fights is a rule, so it is a RuleSet component**, `rest` (cites "Packet: Rest and Healing", "Packet: HP", "Packet: Strain", "Packet: Dying and Death"). Its amounts come from the component, never from campaign code. A variant with a flat amount per night (`rest.night_hp`) exists only to reproduce the study's +2.
- **Carry-over state goes in and out through StateOps.** A new `CarryState` (per creature: HP, strain, Shock, stabilized, dead) is read from a finished `BattleState` and written into a new one by `StateOps` methods (`enter_with`, `rest_night`, the stabilization steps below), each emitting an event. `new_combatant` keeps its fresh default, so a fight with no carry-in is unchanged.
- **Fights without a campaign keep identical event logs.** A one-fight campaign from fresh must reproduce the standalone scenario's log hash; that is the parity test for the whole layer.

### Between fights (ruled 2026-11-08)

| Reading | Ruling | Assumptions row |
|---|---|---|
| Stamina between fights | Back to maximum before every fight, given the HP the creature carries in. Stamina recovers in well under a minute | ruled 2026-11-08 |
| Rest | A rest is one night. Each night: HP and strain recover by Packet: Rest and Healing | ruled 2026-11-08 |
| Recovery from negative HP | The same nightly amount, from wherever HP is. From −5 at STR 0 (8 HP since v0.9.2, 1 a night), that's 13 nights to full | ruled 2026-11-08; Packet: HP (v0.9.3) |
| Fit to fight | HP 1 or more. At 0 HP or below a creature is incapacitated: stamina 0, no actions, no movement. It sits out every fight until it heals | ruled 2026-11-08; Packet: Dying and Death (v0.9.3) |
| A death | The party continues a person short | ruled 2026-11-08 |
| Strain's 1-per-6-hours alternative | Not built until rests have a length in hours; with "a rest is a night", it needs a night's length | pending designer |

Two future ideas from the rulings belong elsewhere. **Fights that continue with new creatures**, whether they join at once or arrive from far enough away that they have to run in, are Objectives catalogue item 9 (reinforcement waves), not a campaign feature. **Crawling at 0 HP** would be a change to Dying and Death.

### After a fight: stabilization (ruled 2026-11-08)

Packet v0.9.3 says that when a fight ends, turns continue in initiative order until no one is in System Shock, and that allies can help in a way still marked TODO. The help below is the engine's stand-in for that TODO, an Assumptions row ruled 2026-11-08 for the simulation only:

1. **Rounds continue** until no party member is in System Shock (each one is stabilized or dead). No one else acts and nothing else happens.
2. **Each dying creature still makes its normal dying roll** at the start of its turn (Packet: Dying and Death): it can get better or worse.
3. **Each active party member** (HP 1 or more) **can help one dying ally per round.** Each helper gives that ally one extra roll. The extra roll can only help: on 15 + Shock or more, Shock drops by 1; anything else changes nothing. Two helpers on one ally make three rolls: one normal roll and two assists.
4. **Engine conventions** (Assumptions rows, *engine convention*):
   - The dying creature makes every roll, with its own Will, as in the packet's dying roll.
   - The normal roll comes first, then the assists. Each roll compares against the Shock as it stands after the roll before it.
   - Death at 10 Shock is checked after the normal roll. Reaching 0 Shock ends System Shock, and unused assists that round are lost.
   - Position doesn't matter after the fight.
   - If the party lost the fight, no one is left to help, and the campaign ends (a convention: what happens to a beaten party is the GM's).
   - This is after-fight only. Helping during a fight waits for the packet's Medicine rule.
5. **Choosing whom to help is a decision.** A new `Stabilize` request goes to each helper every round: which dying ally to help, or none. It goes through the broker like every other request, and every agent family answers it. The default policy helps the ally with the highest Shock (the closest to dying), ties to the lowest HP. It matters only when there are fewer helpers than dying allies. A later policy could choose exactly: the dying track is a small Markov chain, so the engine can compute which assignment saves the most expected lives.

Golden tests: the packet's System Shock example continued after a fight with zero, one and two helpers; one helper and two dying allies; a death on the normal roll before any assist.

### Surrender (ruled 2026-11-08)

Surrender is already in the engine (Assumptions row "Surrender (M4)"). Any active creature on a map may surrender on its own turn, and is then out of the fight. The tactical agent surrenders when engaged with HP at or below its `surrender_below` fraction, which is 0 (never) unless a profile sets it; only the `cautious` NPC profile does.

- **PCs fight to the death by default.** Their agents never surrender. `surrender_below` for PCs is a sweep axis, not a default.
- **A surrender counts only when the whole party is out.** The party loses a fight when every PC has surrendered, is down or is dead. If anyone surrendered, the campaign ends marked **surrendered** rather than **wiped**: an ending with an asterisk, reported apart from wipes. What happens to a surrendered party afterwards is the GM's business, so the campaign stops there.
- **A PC who surrendered while the rest of the party won** rejoins with the HP they had (engine convention).
- **Warning turns.** Surrender happens on your own turn, so it only helps a PC who survives to their turn *and* can see the danger. That's worth measuring in its own right, because the packet wants named characters to "have to be pressured before they take a fatal hit" and threats to be telegraphed.
  - For each PC who goes down, the engine records whether they had a **warning turn**: a turn of their own in that fight, before going down, at which their chance of going down before their next turn was already high.
  - That chance comes from the exact strike calculator, against the enemies able to reach them. The threshold is a report parameter.
  - The report gives the share of PCs who go down with no warning turn, and the turns of warning the rest had. The study's spike drops suggest this share is high today.
  - It's a fight metric, so single-fight suites can report it too.

### Scenario format

```toml
[campaign]
name = "fighter-trio-standard"
trials = 1000
seed = 7
length = { fights = 12 }              # or { days = 10 }; ends early if the party loses a fight
pacing = "standard"                   # data/pacing/standard.toml
party = ["fighter_a", "fighter_b", "duelist"]

[[combatant]]                         # party members persist across fights by id
id = "fighter_a"
build = "l1_sample_fighter"
agent = { kind = "tactical", campaign = "aware" }

[encounters]                          # drawn per fight; each names an ordinary scenario
easy   = { weight = 3, scenarios = ["enc/mooks_4.toml"] }
medium = { weight = 2, scenarios = ["enc/bandits_2.toml", "enc/skirmish.toml"] }
hard   = { weight = 1, scenarios = ["enc/brute_l30.toml"] }
```

```toml
# data/pacing/standard.toml: the chat's proposal
[pacing]
description = "After each fight, 50% chance the day ends."
day_ends_after_fight = "1/2"
day_ends_on_drop = false              # true reproduces the Party Day Study
downtime_nights = { 0 = 1 }           # nights between days beyond the first: none
```

An encounter scenario fills its PC spawns from the party's fit members in order; its own NPCs are fresh every time. The tiers above are placeholders until calibration sets them. Pacing and encounter draws use their own seeded streams from `core/`, so two campaigns that differ only in a build see the same encounters and schedule (common random numbers, which makes STR 2 against STR 3 a paired comparison).

### Metrics

- **Campaign row:** fights fought and won, days and nights elapsed, fights until the first drop, days cleared without a drop, deaths and who, nights each PC spent unfit or below full HP, strain overage paid in stamina, how it ended (length reached, wiped, surrendered).
- **Fight rows gain** campaign id, fight index, day index, fight-of-day index, party size, each PC's entry HP and strain, who dropped and whether they entered at full HP, and after-fight stabilization (rolls, assists, saved, died). Everything the fight metrics already report then splits by entry state for free.
- **Reports:** win, down and death rates by fight index and by fight-of-day index (attrition curves); survival curve over the campaign; the paired build comparison per pacing profile with Wilson or paired intervals. Each is stamped with the RuleSet digest, the `rest` readings and the pacing profile's hash, and carries the "What the simulation is not" caveats.
- **The attrition gate.** Every campaign report opens with question 0: the share of drops from PCs who entered at full HP. When most drops come from full HP, the report says that attrition isn't measurable under these rules and encounters. Its attrition curves and Strength comparisons are then context, not findings. Results split by party size, so a death isn't read as attrition.

### Exact tools to bring in

The study's two calculators belong in `analysis/`, beside the strike and ranged calculators, with tests:
- **`series.py`:** the best play over a series of duels. It gives an exact HP price for checking any agent's, and replaces the backward-induction step this plan first listed as optional.
- **`calc_unanswerable.py`:** the share of a fresh PC's defenses a monster's maximum all-in beats. The study recommends it as the boss check for GM guidance, and calibration reports it per encounter.

Both are in `claude/block_study/day_study_bundle.txt` and need copying into the repo, with the study's scenarios (`day/`, `day2/`), before this step.

## Agents

### Protecting the party comes first

The study's spike drops come from focus fire on soft PCs, and today's agents don't defend each other. Before carried-over HP is worth pricing, a party needs agents that can look after its members:

- **A line-holding party policy:** armored PCs hold a gap or a front, and soft or wounded PCs stay behind it, stepping in only to attack. It overlaps the screening policy the Objectives plan proposes, so it should be built once for both.
- **A bodyguard rule:** a PC moves to engage whoever threatens a soft or wounded ally, and the price of leaving reach counts.
- **NPC targeting as a sweep axis:** `lowest_stamina`, `focus`, `nearest`. Focus fire is how a carried wound turns into a drop next fight, so question 3 has to be read per targeting mode.

This also answers the study's open question (question 10). If line-holding brings the soft PC's drop rate down on a map with a defensible gap, the lethality is tactical content. If it doesn't, it's punishment, and a finding for defense values.

### Teaching them that a fight isn't the last one

Today's agents are *myopic*: `w` = 3 for every fight, and strain is spent by in-fight heuristics. The study suggests the HP part of that is already close to right, so this work is mostly about strain:

1. **An `Outlook` in the observation:** fights expected before the next rest (from the pacing profile, as a table would roughly know it), nights to heal, strain recovery.
2. **A strain price** for each ability use: `λ_strain` per point, rising past maximum by the overage the next fights will pay. An **HP price** above `w` is added only if `series.py` shows `w` = 3 falling short for some build or pacing.
3. **Named spending styles,** as agent specs, so results show the spread: `nova` (every fight is the last; today's agents), `budgeted` (spend strain up to recovery ÷ expected fights per day, then only to avoid going down), `conservative` (no grazes that wound, abilities only to avoid incapacitation).
4. **Tuned prices (a best response):** sweep `λ_strain` (and `λ_hp` if needed) per build and pacing, and report the values that maximize fights won without anyone going down. Headline campaign results are reported for `nova` and the tuned agent, as the Risks table's "at least two agent families" rule asks.

These are agent conventions, not rules, documented like the ability policies.

NPCs stay myopic: an encounter is their only fight. The NPC profiles' flee and surrender thresholds are the dial that question 7 sweeps.

## Telling design chats about it

Single-fight numbers don't show what they leave out, so part of the fix is documentation. This section is the draft for `USAGE_FOR_CHATS.md`. It ships with carry-over (C3), because describing commands that don't exist yet would mislead chats.

### Draft for `USAGE_FOR_CHATS.md`: "Fights don't happen alone"

**What a single fight leaves out.** Every `se run`, `se suite` and `se trace` result is one fight from fresh: full HP, strain 0, and agents that price HP at a constant `w`. That's a best case for anything that costs strain, and it can't see a wound carried into the next fight (current HP sets maximum stamina) or the nights it takes to heal. HP comes back only by resting (1 + odd Strength per night); there is no healing magic. Stamina is back to full before every fight; strain isn't.

**Run a campaign (`se campaign`) when the question involves anything that lasts past the fight:**
- HP lost or healed: Strength (both odd and even values), armor and shields, grazing blocks, anything that changes how often or how badly people are wounded;
- strain: class cores, candidate abilities, spells, overage;
- how NPCs fight, when the question is what they cost the PCs (flee and surrender thresholds, aggression, targeting);
- encounter difficulty, or "how many fights can a party take";
- any balance claim meant to hold for a session rather than a fight ("X is stronger than Y", "this is worth its cost").

**A single fight is enough when** the question is about one exchange (use the exact calculators), or a mechanic's in-fight behavior (movement, opportunity attacks, cover, initiative) where both variants leave people about equally hurt. If a variant changes how much HP is lost, or how much strain is spent, follow it with a campaign before calling it a result.

**The standard analyses.** Pick the ones the question needs; name them in the report.

| Analysis | Use it for | Run | Report |
|---|---|---|---|
| Attrition gate | Every campaign result, first | Any campaign | The share of drops from PCs who entered at full HP. If it's most of them, say attrition isn't measurable yet and treat the rest as context |
| Pacing check | Any single-fight finding about a lasting resource | The same comparison as a campaign under `sparse`, `standard` and `dungeon` | Whether the sign and ranking hold in every profile. One that flips is a finding: Design Notes 3.5 says balance must hold across pacing |
| Paired build comparison | Two builds that differ in one choice (STR 2 vs 3, armor vs none, a core vs none) | Both in the same campaign file and seed, so they meet the same encounters and schedule | Paired differences per profile: fights won, characters down, nights unfit, deaths per 10 fights |
| Day budget | Anything that costs strain | A campaign with the ability on and off | Win and down rates by fight of the day, overage paid; whether the ability still pays in fight 3 |
| Attrition | Death spirals and wounds carried over | Any campaign; split fight rows by entry HP and NPC targeting mode | Outcome by entry HP; chance a wounded PC goes down next, against a fresh one |
| Encounter cost | Encounter difficulty and guidelines | `se calibrate` | Each encounter's fresh drop and death rates against the 15–20% target, the same at half HP, who drops, and the all-in check |
| Protection check | Whether a drop rate is tactics or punishment | The same encounter with the line-holding party and with today's agents, on a map with a defensible gap | The soft PC's drop rate both ways |
| Agent spread | Any headline campaign result | The same campaign with `nova` and tuned agents | Both. A conclusion that holds only for one is itself the finding (for example, "only a careful player gains from this") |

**Reading the results.**
- Death rates measure danger. They don't say what a death does to a campaign: the party simply continues a person short.
- Pacing is given. The party never chooses to rest, so nothing here says how players would pace themselves.
- Everyone stays at one level.
- New creatures joining a fight in progress aren't modeled here (see the Objectives plan's reinforcement waves).

**Report** the pacing profiles, agent styles and NPC targeting beside the RuleSet digest and switches, and quote the reading caveats.

**Phrasing for the designer's requests.** To get the cross-fight answer without spelling it out each time: *"Run X with the pacing check and the day budget, for nova and tuned agents."*

### Elsewhere

- **`CLAUDE.md`:** the new commands, and one line under ground rules that cross-fight value is a campaign concern, so single-fight scenarios must not fake it (no raising `w` in a scenario to "account for" later fights).
- **Report template:** a "Pacing" line beside the RuleSet digest and assumption switches in `sim/reports/`.
- **Until carry-over lands,** one sentence in `USAGE_FOR_CHATS.md` can already say that every result is a fresh fight at strain 0 and so a best case for strain abilities.

## Phases

- **C0: the current packet as a preset.** The components and `v0.9.3` preset above, on a branch with a pull request. Done when the packet's worked examples for the changed rules pass, and earlier presets' logs are unchanged.
- **C1: encounter calibration.** `se calibrate`, the drop-source and warning-turn metrics (they're fight metrics, so they don't need carry-over), and `analysis/` ports of the study's two calculators. The study's encounters become engine scenarios. Done when the study's fresh-encounter table is reproduced within its intervals under its RuleSets, and the same table is reported under `v0.9.3`. Questions 0 (fresh part) and 9.
- **C2: a party that protects itself.** The line-holding and bodyguard policies (shared with Objectives screening), NPC targeting as a sweep axis, and the protection check on a defensible-gap map. Question 10. This is also the study's own next test, so it's useful before any campaign exists.
- **C3: carry-over, fixed pacing and after-fight stabilization.** `CarryState`, the `rest` component, after-fight stabilization and the `Stabilize` request, surrender endings, `experiments/campaign.py`, pacing (with `day_ends_on_drop`) and encounter data, campaign and per-fight-index metrics with the attrition gate, `se campaign <campaign.toml>`, the one-fight parity test, and the chats' guide above. First report: questions 0, 1, 3, 4 and 8 under the three profiles, with the study's day numbers reproduced as a cross-check. The code can be built beside C1 and C2, but its results wait for them: before calibration and protection, the attrition gate will mostly fail.
- **C4: spending across a day.** `Outlook`, the strain price, the spending styles and the tuned-agent report; an HP price only if `series.py` shows `w` falling short. Questions 2, 5 and 6.
- **C5: retreat and morale across fights.** PCs fleeing a fight they're losing, and keeping their HP for the next one; NPC morale swept for what it costs the PCs. Better after Objectives O1 (Escape) and O3 (morale). Question 7.
- **C6 (optional):** an exact stabilization policy; `se play --campaign` so the designer can play a party through a short campaign.

C0–C3 don't depend on the Objectives work, though C2 shares a policy with it.

**Not planned:** the party choosing when to rest. It needs time pressure, and setting that is the GM's job (ruled 2026-11-08).

**Done when (C3):**
- a one-fight fresh campaign reproduces each existing scenario's log hash;
- golden tests for a night's rest at every Strength 0–6, strain recovery, recovery from negative HP, and the stabilization cases above;
- determinism: same seed and campaign, same logs;
- the broker never rejects an engine agent's `Stabilize` answer;
- with the study's pacing (`day_ends_on_drop`, `rest.night_hp = 2`) and RuleSets, its day numbers are reproduced within their intervals: days cleared without a drop, fights cleared per day;
- the campaign suite reports the attrition gate, attrition curves and the paired Strength comparison across three pacing profiles under `v0.9.3`;
- `USAGE_FOR_CHATS.md` has the "Fights don't happen alone" section;
- earlier logs unchanged apart from the digest.

## Rulings and open questions

Ruled 2026-11-08, for the simulation:
1. Stamina is full before every fight.
2. Negative HP recovers at the same nightly rate.
3. A character can fight again at 1 HP; at 0 or below they are incapacitated.
4. After a fight, active allies help dying ones stabilize, as described above.
5. A rest is a night.
6. A dead character's party continues a person short.
7. Pacing is given; parties don't choose to rest.
8. PCs fight to the death by default. A surrender ends the campaign only when the whole party has surrendered or is down or dead, and is reported apart from a wipe.

Rulings 2 and 3, and the turns that continue after a fight for System Shock, are in packet v0.9.3. The after-fight help in ruling 4 is a simulation stand-in; the packet marks how allies help as TODO.

Still open:
- Is the study's target, "in a fresh medium fight, someone drops at most about 15–20% of the time", the definition of a medium encounter for calibration?
- Should any standard pacing profile end the day at the first drop, or only the profile that reproduces the study?
- The study's code bundle and scenarios (`claude/block_study/day_study_bundle.txt`, `day/`, `day2/`) need to be in the repo before C1.
- Strain's 1-per-6-hours alternative needs a night's length in hours before it can be compared.

## Next step

If this direction is adopted: add "Proposed, not adopted: M8 Campaigns" to ENGINE_PLAN's milestone table beside M7, and write the detailed plan for C0 and C1 in the style of `OBJECTIVES_O1_PLAN.md`.
