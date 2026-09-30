# Escape-magic research

Read /refs/CONTEXT.md, /refs/history.md, /refs/past_runs.md, and the existing
RESEARCH.md / EXPERIMENTS.md before choosing the change. History #1's proactive
minotaur wands scored 0.3722; #2's Castle arrival/crossing scored 0.3896. Neither
is repeated. Previous close-range darts, exact prayer thresholds, earlier dives,
and broader escape rewrites also have failures recorded; they are not adopted.

Parent: 30 games, both Tourist identities, seeds 0–14. Minotaurs account for six
deaths (seeds 2, 11, 14 for each identity), the most common exact cause. The deepest
milestone is Dlvl:29. Seeds 0, 1, 6, 12 die early. Both roles are Tourist, so the
same role wiki applies to both genders.

## Other-character leaders

Opened all 27 distinct other-character .diff files listed in /refs/top/README.md.
Many are truncated at 300,000 bytes, especially portfolio programs; inspected
source packages as well. The list records a concrete absent mechanism per program,
with an explicit exception where no new active mechanism exists. Shared mechanisms
are listed separately because multiple leaders contain the same implementation.

- `0716a5964bc4`: aa_dd/global_logic.py: cap inventory below the squeeze limit when a Mines staircase is reachable only through a diagonal gap.
- `0875c3519bed`: pf_v25/global_logic.py: the same staircase-directed inventory cap, instead of waiting for a completely boxed-in position.
- `1c17ee5b7216`: pf_v25/global_logic.py: leave the Mines promptly after acquiring a digging tool; avoid exhaustive exploration on the return.
- `1c4099e80253`: autoascend/dive_logic.py: drop possible scare-monster scrolls before a minotaur reaches melee, hold the square and throw safely at it.
- `41c961256c41`: Exception: no additional active strategy to transfer; this is the older Tourist strategy with Castle crossing disabled.
- `429cf0108271`: rog/global_logic.py: staircase-directed pack reduction for diagonal squeezing out of the Mines.
- `44f826234d72`: autoascend/combat/fight_heur.py: Ranger point-blank archery avoids a weapon-swap turn when an enemy closes.
- `47a6c840a4cf`: autoascend/agent.py: escape a bear trap using legal diagonal movement attempts, which advance escape reliably.
- `5088ac9a49a3`: autoascend/power_route.py: use teleport control plus a cursed teleport scroll to bypass the Castle floor.
- `51a41284fa08`: autoascend/agent.py: diagonal bear-trap escape rather than repeatedly trying the same orthogonal route.
- `6ecc35e91af2`: autoascend/dive_logic.py: a tool carrier begins descending at XL7 rather than XL8 (already tried unsuccessfully for Tourists; not adopted).
- `725cafa6a87d`: pf_kef_d42161f/agent.py: explicit bear-trap state and diagonal escape attempts.
- `7c1ec61015bf`: autoascend/power_route.py: controlled level-teleport route with a bounded multi-action strategy.
- `81ea959c3b98`: autoascend/power_route.py: identify carried rings/scrolls to find a controlled level-teleport combination.
- `985b175cae53`: s21db872/agent.py: diagonal bear-trap escape without permanently forbidding the blocked route.
- `ae053ca704ff`: rog/global_logic.py: lower inventory weight specifically when it opens the Mines staircase route.
- `ae17b4a50322`: pf_hg/agent.py: track bear-trap confinement and escape diagonally.
- `b4c2edc23ce3`: autoascend/agent.py: diagonal bear-trap escape during descent.
- `bded98c686e3`: pf_hg/agent.py: diagonal bear-trap escape during descent.
- `c49b46fdffa0`: autoascend/agent.py: diagonal bear-trap escape during descent.
- `c526d8d41f20`: aa_dd/global_logic.py: staircase-directed squeeze-weight cap after obtaining a digging tool.
- `d44c89c2ffd8`: pf_hg/agent.py: diagonal bear-trap escape; its portfolio contains this mechanism absent from our strategy.
- `d4eab8c5a4f0`: pf_v25/global_logic.py: staircase-directed squeeze-weight cap in the Mines.
- `d4f9cab6e621`: autoascend/combat/fight_heur.py: independent range budgets for each simulated reflected wand-ray branch.
- `e9c44042710b`: aa_dd/global_logic.py: staircase-directed pack reduction in the Mines.
- `f362a746154d`: autoascend/combat/fight_heur.py: Ranger point-blank archery while the launcher is already wielded.
- `f5d169eb6076`: pf_hg/agent.py: diagonal bear-trap escape during descent.

## Online reading

Successful HTTP lookups:
- https://nethackwiki.com/wiki/Tourist
- https://nethackwiki.com/wiki/Minotaur
- https://nethackwiki.com/wiki/Castle
- https://nethackwiki.com/wiki/Level_teleport
- https://nethackwiki.com/wiki/Scroll_of_scare_monster
- https://nethackwiki.com/wiki/Standard_strategy
- https://nethackwiki.com/wiki/Valley_of_the_Dead
- https://nethackwiki.com/wiki/Potion_of_extra_healing
- https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/monmove.c
- https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/potion.c

Reddit search returned HTTP 403; Tourist/Strategy returned 404. Neither is counted
as a successful lookup. Tourist itself includes the early/mid/late-game strategy.
Wiki sections labeled 3.7 are excluded. In 3.6.6 monmove.c, onscary checks a floor
SCR_SCARE_MONSTER before the minotaur, blind-monster, and Gehennom exclusions for
Elbereth. A dropped scroll therefore stops these melee attacks. Unlike Elbereth,
attacking does not erase the scroll. A second pickup can destroy it; fire can too.
It does not protect against lawful minions, Riders, the Wizard, or ranged attacks.

## Rejected scare-scroll draft

Three variants were tested, all removed: depth-20 retention with reactive defense
(six games); full SCARE_KEEP reservation with reactive defense (ten games); and
proactive Castle-arrival drops without reservation (eight games). None showed an
improvement. The final strategy contains none of these edits. The samples exposed
unknown potions preventing a reactive response and inventories with no effective
scare scroll. Files: /tmp/scare-sample.json, /tmp/scare-reserve.json,
/tmp/scare-arrival.json. No deterministic seed/program pair was repeated.

## Rejected controlled level-teleport draft

The leading dwarf Valkyrie's power_route.py identifies stored rings and scrolls,
learns teleport control from prompts, and combines it with cursed teleport scrolls
or level-teleporter traps. This provides a route past the undiggable Castle floor.
The Tourist wiki also emphasizes using found magic to compensate for weak combat.
This draft ported that resource/escape strategy. It has now been removed; the
existing make_agent/reset/act contract and adapter remain unchanged.

Read 3.6.6 teleport.c directly:
https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/teleport.c
Lines around 996–1008 confirm an over-deep request clamps to the Valley from the
Dungeons, or the deepest accessible level of Gehennom before invocation. The bot
asks for 99, letting the game select that legal destination; it does not use the
reference's score-table-specific destination choice. Confusion usually randomizes
a controlled answer, so a sure cursed-scroll jump waits until confusion clears.

Known identify scrolls and unknown stacks are read during quiet, healthy moments
of the dive, using the reference's menu handling and inventory priorities. Ring
control is learned from teleport prompts; a known control ring is worn before
using a jump. At the Castle, after ordinary crossing preparation gives up, unknown
rings and scrolls can provide an escape. Identify-by-altar and speculative ring
wear tests are disabled. Confused-scroll gambles are limited to the late dungeon,
the Castle after crossing failure, and Gehennom. Unholy water can turn a known
teleport scroll into a reliable level-teleport trigger. All readiness/loop guards
remain bounded and preserve ordinary emergency preemption.

Imports, factory construction, configuration references, and focused route checks
(known control, cursed/uncursed distinction, postponement under confusion) passed.
Four samples failed to improve the parent: /tmp/teleport-sample.json,
/tmp/teleport-v2.json, /tmp/teleport-v3.json, /tmp/teleport-v4.json. Identifying on
Dlvl 1 severely damaged survival. Delaying preparation to depth 20 avoided that
large loss but did not produce successful level teleports. Integration fixes
included reading identify-menu page numbers from the raw terminal footer (the
popup parser strips them), preserving the menu iterator across pages, and avoiding
a BFS-cache mutation in a hostile-readiness check. All teleport edits are removed.

## Rejected launcher draft

Additional online reading:
- https://nethackwiki.com/wiki/Inventory
- https://nethackwiki.com/wiki/Encumbrance
- https://nethackwiki.com/wiki/Ranged_combat (redirects to Ranged_attack)
- https://nethackwiki.com/wiki/Sling

The inventory wiki describes the 52-stack limit; encumbrance advice emphasizes
leaving unnecessary equipment behind. The sling page confirms that sling
enchantment improves accuracy. The other-character leaders' pack-reduction
strategies also show that inventory management affects survival and navigation.
These are 3.6 mechanics, not upcoming 3.7 changes.

The traces showed repeated slings filling letters while useful rings, wands, and
potions waited behind weapons in retention priority. For example, seed 7 carried
slings at f, g, K, M, P, W, alongside a crossbow. The parent explicitly retains
EVERY launcher for Tourists, then may retain more through its generic unknown-item
rule. The change selects one non-cursed launcher per ammunition family, preferring
known safe items, higher enchantment, and an equipped item on ties. All retention
paths share this filter. Mandatory equipped items remain handled by the existing
forced-items rules. Ammunition and thrown weapons keep their existing policy.

This draft scored 0.21369 over all 15 female games, well below the parent.
Seed 12 improved to depth 23, but many previously successful games failed much
earlier. Files: /tmp/launcher-sample.json and /tmp/launcher-rest.json. Removed.

## Rejected bear-trap draft

Read https://nethackwiki.com/wiki/Bear_trap and the NetHack-3.6.6_Released
src/hack.c trapmove() implementation. Ported the explicit trap-state tracker and
diagonal escape from /refs/top/47a6c840a4cf/autoascend/agent.py, first for descent,
then for all phases. The six-game descent sample and five-game all-phase sample
never invoked the strategy, so there was no benefit. Both variants removed.
Files: /tmp/bear-sample.json and /tmp/bear-allphase.json.

## Rejected early-HP draft

The Potion of extra healing wiki explicitly recommends that weaker characters
can drink their starting potions immediately for maximum HP. The Tourist wiki
identifies the role as especially fragile early on. Verified in 3.6.6 potion.c:
POT_EXTRA_HEALING calls healup with +2 max HP if uncursed and +5 if blessed when
the healing would exceed maximum HP. This can turn the Tourist's starting 10 HP
into 14 before hostile encounters and exercises strength and constitution.

The strategy drinks known, non-cursed extra healing at full HP while XL 1,
unpolymorphed, and with no hostile visible. Fight and emergency strategies retain
priority. It uses ordinary inventory knowledge and character state, no seed tests.
Logs confirmed the HP increase, but neither using both potions nor retaining one
improved the six-game sample. Both variants removed. Files:
/tmp/fortify-sample.json and /tmp/fortify-reserve.json.

## Rejected reflected-wand planning draft

Source: /refs/top/d4f9cab6e621/autoascend/combat/fight_heur.py, the leading female
gnome Healer, has independent range budgets for each possible reflected ray and
propagates probabilities through the entire ray path. Read additional wiki pages:
https://nethackwiki.com/wiki/Ray, https://nethackwiki.com/wiki/Wand_of_fire,
https://nethackwiki.com/wiki/Wand_of_death. The Ray page explains range deductions
for walls/targets and probabilistic angled reflections. Advice from variant-only
sections, including minotaur death resistance, is excluded.

The parent mutates range_left between mutually exclusive branches and resets the
probability to 1.0 at each recursive step. Thus a rare reflected self-hit can be
counted as certain and later branches can end prematurely, changing which wand
shots the bot chooses. The sole code change gives each branch its own budget and
propagates probability * next_prob. The focused check verifies a 25% / 75% branch
retains those probabilities through subsequent squares, and reversing the branch
order leaves expected hits unchanged. Only combat/fight_heur.py differs from the
parent. The six-game sample did not improve: /tmp/wand-sample.json. Removed.

## Further rejected drafts

- Restrict redundant-launcher removal to the descent, preserving equipment
  collection during leveling: /tmp/launcher-dive.json, six female games, no gain.
- Strictly use only known sleep/death wands (including their engraving ambiguity),
  excluding the broad unknown-wand gambles of history #1: /tmp/sleep-ray.json,
  five female games, no useful opportunities and no gain.
- Throw from a wielded digging tool during descent to avoid switching to a melee
  weapon and back, inspired by the Ranger's point-blank archery:
  /tmp/dig-throw.json, six female games, worse. This left the leveling phase alone,
  unlike the older all-phase close-range dart draft in RESEARCH.md.
- Add missing experience, dexterity, and thrown-weapon skill to ranged accuracy;
  then model launcher/throwing damage as well: /tmp/ranged-model.json and
  /tmp/ranged-full.json, six female games each, both worse. Read the 3.6.6
  dothrow.c thitmonst(), uhitm.c hmon_hitmon(), and weapon.c dbon()/weapon_dam_bonus()
  implementations, plus https://nethackwiki.com/wiki/Wield and
  https://nethackwiki.com/wiki/Dart. Melee skill modeling was unchanged.
All these drafts are removed.

## Selected idea: use identified haste magic

Read:
- https://nethackwiki.com/wiki/Wand_of_speed_monster
- https://nethackwiki.com/wiki/Potion_of_speed
- https://nethackwiki.com/wiki/Speed
- https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/zap.c
- https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/potion.c

The minotaur strategy recommends speed for keeping distance. The bot carries
identified haste resources but does not deliberately use them. In 3.6.6,
zapyourself(WAN_SPEED_MONSTER) sets HFast |= FROMOUTSIDE: permanent intrinsic speed.
A speed potion provides temporary very-fast speed for 40–49, 100–109, or 160–169
turns depending on BUC. It does NOT grant intrinsic speed in 3.6.6; newer wiki
advice to that effect is excluded, as is 3.7's temporary wand effect.

The first haste variant scored 0.3892395924 over all 15 female games, just below
the required threshold (/tmp/haste-sample.json and /tmp/haste-rest.json). It used a
speed potion on Dlvl 1, too early to help with the Castle. A second version kept
permanent haste until descent and consumed potions near strong monsters or at the
Castle. Its seven-game sample regressed on a dragon encounter: the additional
quaffing turn preceded a lethal poisoned blast (/tmp/haste-ready.json).

The current candidate self-zaps a known speed wand once in a quiet moment after
descent starts. Known speed potions are reserved for preparation on the confirmed
Castle floor, before the existing crossing strategy tries equipment. It avoids
known speed boots and repeated potions during the maximum possible duration for
their recorded BUC. It skips polymorphed and excessively burdened states, and
leaves ordinary emergencies above the new strategy. All conditions use ordinary
game state and inventory knowledge. No earlier candidate remains in the code.

All 30 games completed: female 0.4052955215, male 0.3705310699,
overall 0.3879132957. The male seed 8 did not improve and seeds 5/11 regressed.
Below parent, so the haste candidate is removed. Results: /tmp/haste-castle-all.json.

## Range-two camera defense

Source: the expensive-camera wiki and 3.6.6 uhitm.c flash_hits_mon():
https://nethackwiki.com/wiki/Expensive_camera
https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/uhitm.c
The camera causes fleeing with probability 3/4 when squared distance is below 9.
Both straight and diagonal range-two flashes qualify, before the enemy reaches
melee. The parent only flashes adjacent enemies. Extend the existing camera
policy to range two, retaining all Elbereth and role-phase guards, rejecting
unaligned targets or an intervening creature/wall, and allowing nonunit direction
conversion. No haste code remains. This differs from previously tried camera
policies by acting at range two, not changing early-game or Elbereth eligibility.


Range-two sample: /tmp/camera-range.json, no improvement. Removed.

## Selected idea: remember successful camera blindness

The same camera wiki and 3.6.6 flash_hits_mon() show a blind monster cannot be
blinded or scared by another flash. Current logs show repeated blank flashes
against the same moving wererat/elf while attacks land. Track confirmed adjacent
flash blindness through uniquely matching glyph movements, and omit those camera
actions. Forget when matching is ambiguous, a target disappears, the level
changes, hallucination occurs, or more than one game turn elapses between updates.
All other camera policy stays as in the parent, including adjacent-only range.

First memory sample: /tmp/camera-memory.json. A wererat encounter regressed:
suppressing a blank flash selected a move out of our own pit, which failed and
triggered panic, losing the blindness record. The corrected candidate keeps the
fallback to effective stationary actions while a tracked blinded neighbour holds
us in our own digging pit. This is part of replacing the ineffective flash with
a useful combat action, scoped to precisely that situation.

Corrected memory variant also failed: /tmp/camera-memory-pit.json. Removed.

## Selected idea: protect Castle preparation with the camera

The Castle arrival strategy has priority above normal camera combat. Give a
charged non-cursed camera an opportunity to repel a visible minotaur at range
one or two before continuing the crossing kit. Ordinary emergencies remain
higher priority. Clear aligned shots only, confirmed Castle only, with an eight
turn cooldown to let the existing crossing policy act. The earlier proactive
wand attempt gambled unidentified charges; this uses the starting camera whose
75% fleeing effect in range two is verified in 3.6.6 uhitm.c and the camera wiki.
No blindness-memory or haste edits remain.

The Castle range-two sample (/tmp/castle-camera.json) did not improve.
The next camera version targets approaching minotaurs throughout descent at
ranges 1–6. Outside range two, the flash blinds without scaring; monmove.c
set_apparxy confirms blind monsters guess the hero's position, reducing the chance
of a lethal first melee volley. All intervening squares are checked for walls,
pets and monsters, and the cooldown allows escape preparations to proceed.

## Final outcome: no change kept

The final ranged minotaur-camera sample also regressed (minotaur-camera.json).
All source edits from this iteration are removed. The final autoascend package
matches /refs/parent; the factory/reset/act interface and arena_adapter.py are
unchanged. There is no successful hypothesis to submit, and no improvement is
claimed.

Saved the complete 30-game failed haste evaluation as rejected-haste-eval.json,
with means in rejected-haste-eval-summary.json. Saved the subsequent camera
samples together as rejected-camera-evals.json. Earlier draft results are listed
above. No program/seed/identity pair was deliberately evaluated twice.
