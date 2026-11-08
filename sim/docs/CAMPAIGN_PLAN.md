# Adventuring days: brainstorm and phased plan

*Status: proposal (2026-11-07). Not yet part of the milestone plan in `ENGINE_PLAN.md`. Paths below are relative to `sim/src/stamina_engine/` unless they start with `sim/`, `rules/` or `design/`.*

## Context

Every simulated fight today starts fresh: full HP, stamina at maximum, strain 0 (`model/state.py:98`, `model/derive.py:228`; Assumptions rows "Strain at a fight's start" and "Stamina and strain at the start of a fight", ENGINE_PLAN:487 and :510). Agents price an injury with a constant `w` (3) against stamina (`agents/blocking.py`), and the ability policies fire on in-fight heuristics only (`agents/ability_policy.py`). So the engine measures every fight as if it were the only one, and that hides the costs the packet puts between fights:

- **HP is the bridge.** Maximum stamina = 6 + *current* HP (Packet: Stamina), so a wound carries into the next fight as a smaller defense pool. HP comes back only by resting, 1 + odd-Strength per night, with no healing magic (Packet: Rest and Healing).
- **Strain is a day budget.** It recovers only overnight, and each point over maximum adds stamina to every strain ability (Packet: Going Over Your Maximum Strain). The cores suite already says its numbers are "best cases for a day of several fights" (`sim/reports/cores_suite_notes.md`).
- **Death and convalescence.** The review found a typical loser ends at −3 HP and needs 9–11 nights to be whole, and the winner is wounded 15–40% of the time (`design/Review_Playtest_Packet_v0.9.md:240`).

Several open questions can only be answered across fights:

- Open Questions: "Strength's nightly HP recovery: its value depends on how many fights fall between rests."
- Design Notes 3.5: "Balance must hold up across GM pacing, rest frequency and fight length", and a long-term resource should lose value under sparse pacing rather than become a trap.
- Design Notes open problem 7: per-night strain against 1 per 6 hours; per-rest parity between martials and casters.
- Running the Game (GM-1): an NPC that trades grazes "dies quickly, but the players are left carrying the injuries."
- Encounter guidelines are listed as missing GM material.

The design chat's proposal, six lopsided fights in a row with a 50% chance of a night's rest between each, is the right first step. The rest of this document generalises it.

## Refining the chat's idea

| Chat's version | Refinement | Why |
|---|---|---|
| 50% chance of a night between fights | A **pacing profile**: a distribution of fights per day (including days with none) and of downtime nights between days | A coin flip is memoryless (fights per day geometric, mean 2) and never gives travel days, which heal too. Named profiles let a result be reported "across pacing", which Design Notes 3.5 asks for |
| One profile | At least three: **sparse** (about one fight per day, frequent downtime), **standard** (the chat's), **dungeon** (four to six fights before any rest) | A result that changes rank between profiles is itself a finding |
| "Lopsided" fights | Encounters **tagged by their measured fresh-party cost**: easy, medium and hard, from the engine's own single-fight runs (mean HP lost, P(someone down)) | Makes "lopsided" reproducible, and the calibration table is a first draft of encounter guidelines |
| Regenerate HP | Apply the whole **Rest and Healing** rule: HP by Strength, strain by level, the 1-per-6-hours alternative as a switch | Strain is the other cross-fight resource; it matters for every class core |
| Six fights | Run until the campaign ends: a fixed number of fights, a number of days, or a party wipe; report by fight index | Survival curves show attrition where totals hide it |
| Fixed schedule | Phase 1 keeps the schedule exogenous (the GM's). Later phases let the party **choose** to rest or press on against a clock | A real party responds to injury. Then Strength's recovery buys time, not survival, and the report should say which |

## Brainstorm: what to measure

| # | Question | Measure | Packet or design source |
|---|---|---|---|
| 1 | What is an odd Strength value worth? | Paired campaigns, STR 2 vs STR 3 (and 0 vs 1), by pacing profile: deaths, fights lost, fights fought below full HP | Open Questions; Design Notes 3.4 |
| 2 | Do class cores hold up over a day? | Overage paid in stamina by fight index; win and down rates in fights 1, 2, 3+ of a day; the cores-vs-cores table re-run under each pacing | Going Over Your Maximum Strain; cores suite |
| 3 | Per-night strain against 1 per 6 hours | The same campaigns under both switch values | Strain (alternative); Design Notes open problem 7 |
| 4 | Is there a death spiral across fights? | Win rate by entry HP; the chance a wounded PC goes down next fight, against a fresh one | Stamina (max uses current HP); F7 |
| 5 | How long is convalescence? | Nights out of action per campaign; nights from 0 HP and from System Shock to full | Design Notes: "3–4 nights from incapacitated, about a week from the brink"; review line 240 |
| 6 | Does pacing reorder builds? | Rank correlation of builds (armor, shield, high-Agility duelist, Strength builds) between sparse and dungeon | Design Notes 3.5 |
| 7 | What does a grazing block really cost? | The stamina-per-HP exchange rate at which a campaign-aware agent does best (see Agents) | Blocking; Ledger on grazing as the attrition option |
| 8 | Do NPC profiles that flee spare the PCs? | PC HP lost per fight and deaths per campaign by NPC profile (berserker, disciplined, cautious) | Running the Game (GM-1); H-6 |
| 9 | How often do named characters die? | Deaths per 10 fights and per campaign, by pacing and difficulty mix | What This Game Is Trying To Do ("they do sometimes die, but they have to be pressured") |
| 10 | Encounter guidelines | For each encounter: fresh-party cost, and cost at entry HP 50% | GM material (Open Questions) |

## Engine design

### Where it lives

- **The campaign is an experiment layer above `Battle`**, like the runner and sweeps: `experiments/campaign.py`. It never runs a turn itself; each fight is an ordinary `Battle` built from an ordinary scenario.
- **What happens between fights is a rule, so it is a RuleSet component**, `rest` (cites "Packet: Rest and Healing", "Packet: HP", "Packet: Strain", "Packet: Dying and Death"). Its amounts come from the component, never from campaign code. Defaults reproduce the packet; every unstated reading is a named switch with an Assumptions row *pending designer*.
- **Carry-over state goes in and out through StateOps.** A new `CarryState` (per creature: HP, strain, Shock, stabilized, dead) is read from a finished `BattleState` and written into a new one by `StateOps` methods (`enter_with`, and rest operations such as `rest_night`, `rest_hours`), each emitting an event. `new_combatant` keeps its fresh default, so a fight with no carry-in is unchanged.
- **Fights without a campaign keep identical event logs.** A one-fight campaign from fresh must reproduce the standalone scenario's log hash; that is the parity test for the whole layer.

### Scenario format

```toml
[campaign]
name = "fighter-trio-standard"
trials = 1000
seed = 7
length = { fights = 12 }              # or { days = 10 }; always ends on a party wipe
pacing = "standard"                   # data/pacing/standard.toml
party = ["fighter_a", "fighter_b", "duelist"]
on_death = "end"                      # or "replace" (same build, fresh) or "continue"

[[combatant]]                         # party members persist across fights by id
id = "fighter_a"
build = "l1_sample_fighter"
agent = { kind = "tactical", campaign = "aware" }

[encounters]                          # drawn per fight; each names an ordinary scenario
easy   = { weight = 3, scenarios = ["enc/bandits_2.toml", "enc/wolves_3.toml"] }
medium = { weight = 2, scenarios = ["enc/orc_patrol.toml"] }
hard   = { weight = 1, scenarios = ["enc/ogre.toml"] }
```

```toml
# data/pacing/standard.toml — the chat's proposal
[pacing]
description = "After each fight, 50% chance the day ends."
day_ends_after_fight = "1/2"
downtime_nights = { 0 = 1 }           # nights between days beyond the first: none
breather = "full_stamina"             # between fights in one day
```

An encounter scenario fills its PC spawns from the party in order; its own NPCs are fresh every time. Pacing and encounter draws use their own seeded streams from `core/`, so two campaigns that differ only in a build see the same encounters and schedule (common random numbers, which makes STR 2 against STR 3 a paired comparison).

### Rest component switches (all need the designer)

| Switch | Default (packet reading) | Alternatives | Why it's a question |
|---|---|---|---|
| `rest.between_fights` | `full_stamina` | `carry` (waves with no breather), `recover_n` | Packet: "effectively full again after a short breather… There's no formal rule for this yet" |
| `rest.strain` | `per_night` (4 + round(L/10)) | `per_6_hours` (1 per 6 h, no level-5 bonus) | The packet's own alternative |
| `rest.from_negative` | Nightly HP recovery applies from negative HP as from positive | `stabilize_first` (no recovery until 0 HP), slower below 0 | The packet says how much per night, not from where |
| `rest.fit_to_fight` | HP ≥ 1 | Any HP once stabilized; a minimum fraction | "At 0 HP or below, you're incapacitated" covers a fight, not the next morning |
| `rest.after_fight_shock` | Keep rolling the dying roll each round until stabilized or dead | Allies stabilize with a Medicine roll (**TODO** in the packet) | Decides the death rate, and the packet leaves Medicine undefined |
| `rest.night_interrupted` | Never | A chance per night per pacing profile | Lets "no safe rest" be a pacing feature, not a rule change |

Leveling during a campaign is out of scope; a campaign runs at one level.

### Metrics

- **Campaign row:** fights fought and won, days and nights elapsed, deaths and who, nights spent below full HP, strain overage paid in stamina, how it ended (length reached, wipe).
- **Fight rows gain** campaign id, fight index, day index, fight-of-day index, and each PC's entry HP and strain. Everything the fight metrics already report then splits by entry state for free.
- **Reports:** win, down and death rates by fight index and by fight-of-day index (attrition curves); survival curve over the campaign; the paired build comparison per pacing profile with Wilson or paired intervals; all stamped with the RuleSet digest, the `rest` switches and the pacing profile's hash.

## Agents: teaching them that a fight isn't the last one

The engine can carry HP and strain correctly and still give the wrong answer if every agent plays each fight as if nothing follows. Today's agents are *myopic*: `w` = 3 for every fight, strain spent by in-fight heuristics. That's a useful baseline (and probably how many players play), but a finding about Strength recovery or a class core has to hold against agents that do care. Three levels, cheapest first:

1. **Shadow prices.** The campaign passes each agent a small `Outlook` in its observation: fights expected before the next rest (from the pacing profile, known to the party as a table would know it), nights to heal, strain recovery. The agent turns it into two prices:
   - an **HP price**, added to `w` in the block solver and the aim/commitment estimates: `w_total = w + λ_hp × (expected fights before rest)`, with a large term when a wound would leave the PC unfit to fight;
   - a **strain price** for each ability use: `λ_strain` per point, rising past maximum by the overage the next fights will pay.
   These are agent conventions, not rules, documented like the ability policies.
2. **Named spending styles,** as agent specs, so results show the spread: `nova` (every fight is the last; today's agents), `budgeted` (spend strain up to recovery ÷ expected fights per day, then only to avoid going down), `conservative` (no grazes that wound, abilities only to avoid incapacitation).
3. **Tuned prices (a best response).** Sweep `λ_hp` and `λ_strain` per build and pacing, and report the values that maximize campaign survival (with wins as the tie-breaker). The tuned λ is itself a design number: it is the exchange rate between stamina and lasting HP that a careful player faces, which is what question 7 asks. Every headline campaign result is then reported for `nova` and for the tuned agent, the same "at least two agent families" rule the Risks table already uses.

An optional fourth level, if the shadow prices look too crude: **backward induction over entry state.** The state between fights is tiny (HP, strain, fights left before rest). Simulate the last fight from every entry state, take its value table, then the fight before, and so on; the agent's HP and strain prices become exact differences in that table. It fits beside the M6 search auditor.

NPCs stay myopic: an encounter is their only fight. The NPC profiles' flee and surrender thresholds are the dial that question 8 sweeps.

Later, `se play --campaign` lets the designer play a party through a short campaign, with the outlook shown on screen, so the load report and the tuned prices can be compared with a human's choices.

## Telling design chats (and requests) about it

Some of the fix is documentation, because a chat reading single-fight numbers can't see what they leave out.

- **`USAGE_FOR_CHATS.md`, a new section "Fights don't happen alone":**
  - Every scenario result is a single fresh fight: full HP, strain 0, and an agent that prices HP at a constant `w`. It's a best case for strain abilities and ignores carried wounds.
  - Any claim about strain abilities, grazing, armor, Strength, retreat or surrender, or "who wins over a day", needs `se campaign` under at least two pacing profiles (sparse and dungeon), for the `nova` and tuned agents.
  - Report the pacing profile and the `rest` switch values with the digest.
  - Facts chats get wrong: there is no healing magic; stamina resets between fights only by the engine's `rest.between_fights` reading; strain does not reset between fights; HP lost lowers next fight's maximum stamina.
- **`CLAUDE.md`:** the new commands; one line under ground rules that cross-fight value is a campaign concern, so single-fight agents must not be tuned to fake it (no raising `w` in a scenario to "account for" later fights).
- **Report template:** a "Pacing" line beside the RuleSet digest and assumption switches in `sim/reports/`.
- **Phrasing for the designer's requests,** to get the cross-fight answer without spelling it out each time: *"Run X as a campaign across sparse, standard and dungeon pacing; compare nova and tuned agents; show attrition by fight of day."*

## Phases

- **C1: carry-over and fixed pacing (the chat's proposal, generalized).** `CarryState`, the `rest` component and its switches, `experiments/campaign.py`, pacing and encounter data, campaign and per-fight-index metrics, `se campaign <campaign.toml>`, the one-fight parity test. Myopic agents only. First report: questions 1, 2, 4 and 5 under the three profiles.
- **C2: calibration and encounter tags.** `se calibrate` runs each encounter scenario fresh and at reduced entry HP and writes its cost tags; encounter tables reference tags. Question 10.
- **C3: campaign-aware agents.** `Outlook` in observations, HP and strain prices in the block solver, estimates and ability policies; the three spending styles; the λ sweep and tuned-agent report. Questions 6 and 7.
- **C4: party choices.** A `RestOrPress` decision request after each fight, answered by a party agent (the engine never decides for a creature), with a clock in the pacing profile (each extra day raises the chance of an interrupted night, or ends the campaign at a deadline); fleeing and surrender now carry over, which ties into Objectives O1 (Escape) and O3 (morale). Questions 8 and 9.
- **C5 (optional):** backward-induction prices; `se play --campaign`.

C1 doesn't depend on the Objectives work and can run beside it. C4 is better after O1, because escaping a fight is the main way a party protects its HP.

**Done when (C1):** a one-fight fresh campaign reproduces each existing scenario's log hash; golden tests for a night's rest at every Strength 0–6, strain recovery under both switch values, and recovery from negative HP; determinism (same seed and campaign, same logs); the campaign suite reports attrition curves and the paired Strength comparison across three pacing profiles; earlier logs unchanged apart from the digest.

## Questions for the designer (Assumptions register, never silent defaults)

1. Between fights on the same day, is stamina simply full? What gap counts as a breather, and are there back-to-back fights with no breather?
2. Does nightly HP recovery work the same from negative HP? From −5 at STR 0 that's 11 nights.
3. When can a recovering character fight again: HP 1 or more, or something else?
4. What happens to a creature still in System Shock when the fight ends: keep rolling, or can an ally stabilize it (Medicine is TODO)?
5. Is rest always a night? The 1-per-6-hours strain alternative implies daytime rests could count.
6. When a PC dies, does a campaign end, continue a person short, or bring in a replacement? (Engine convention either way, but it changes the numbers.)
7. Should parties be able to choose to rest, and what does time cost them? (Agent and pacing convention, but it decides whether Strength's recovery buys survival or time.)

## Next step

If this direction is adopted: add "Proposed, not adopted: M8 Campaigns" to ENGINE_PLAN's milestone table beside M7, and write the detailed C1 plan in the style of `OBJECTIVES_O1_PLAN.md`.
