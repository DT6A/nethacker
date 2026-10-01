# Tourist early-survival research

The retained change is emergency summoning of allied animals in were form.
It scores **0.412597 overall on all 30 games**, above the 0.3996 target.
The research and rejected prototypes below are a chronological record; only
the final summoning strategy and its scheduler call remain in production code.

## Loss classification (before choosing a change)

`/refs/parent-eval.json` actually contains 15 female games, not 30. Early means
max_depth <= 4, an Xp milestone <= 5, or turns <= 3000. Four games (26.7%)
qualify: seed 0 bat (1644 turns, depth 3, Xp2), seed 1 jackal (787 turns,
depth 3), seed 6 hallucinated jackal (8807 turns, depth 1, Xp6), seed 12 hill
orc (22290 turns, depth 1, Xp7). Early mean 0.030916; remaining 11 mean
0.537348. Relative to that survivor mean, early losses cost 0.135049 of the
supplied female overall score. There is no supplied male baseline to count.
This iteration targets early melee, not the late game.

## History

Read `/refs/history.md`: #1 minotaur wands scored 0.3722; #2 Castle crossing
scored 0.3896 and was kept; #3 camera/haste experiments scored 0.3848 and
were discarded. Also read the Tourist entries in `/refs/past_runs.md`:
repeated prayer, camera, escape and trap-disarm experiments are already
well explored. The first prototype tested close-range use of the starting darts; it was later reverted.

## All other-character leaders

Read the README, all 27 other-program diffs, and the corresponding combat,
configuration and relocated strategy packages. Many leaders share code.
A concrete mechanism per program follows; shared mechanisms are listed
explicitly rather than presented as independent discoveries.

- `0716a5964bc4`: Models prayer success against the probability of surviving three more combat turns.
- `0875c3519bed`: Uses XL-dependent grind depths (Dlvl 3 at XL5, Dlvl 2 at XL7) in its strategy packages.
- `1c17ee5b7216`: Uses XL-dependent grind depths rather than remaining on Dlvl 1.
- `1c4099e80253`: Moves the early grind to Dlvl 3/2; its comments report fewer hunger prayers and grind deaths.
- `41c961256c41`: No new production strategy relative to this parent: it adopted this Tourist code. Its extra recovery/spell test files are not an implemented advantage here.
- `429cf0108271`: Uses a monster-aware hunger guard and an XL-dependent grind route.
- `44f826234d72`: Allows Rangers to shoot at adjacent enemies instead of spending a turn swapping to melee.
- `47a6c840a4cf`: Uses XL-dependent grind depths and tracks fresh corpses to reduce hunger exposure.
- `5088ac9a49a3`: Contains the Ranger point-blank archery mechanism, eliminating unnecessary weapon swaps.
- `51a41284fa08`: Enables GRIND_LEVELS={5:3,7:2}, increasing early experience acquisition.
- `6ecc35e91af2`: Allows unknown-item last resorts instead of holding them behind LR_ELBERETH; much of this older leader removes Tourist-specific behavior.
- `725cafa6a87d`: Uses XL-dependent grind depths in its role strategy packages.
- `7c1ec61015bf`: Tracks were-family corpse restrictions to avoid cannibalism after lycanthropy, alongside a moving grind route.
- `81ea959c3b98`: Contains the Ranger point-blank archery mechanism.
- `985b175cae53`: Contains point-blank archery and a short-cooldown Healer strategy package.
- `ae053ca704ff`: Moves the grind between shallow levels as XL rises.
- `ae17b4a50322`: Includes a moving grind route and role-specific hunger handling.
- `b4c2edc23ce3`: Moves XL5-6 grinding to Dlvl 3 and XL7 to Dlvl 2.
- `bded98c686e3`: Includes the moving grind route in its role strategy packages.
- `c49b46fdffa0`: Reduces early Healer ghost-melee priority, preferring a legal retreat.
- `c526d8d41f20`: Keeps four lichen corpses as emergency food (LICHEN_RESERVE=4).
- `d44c89c2ffd8`: Uses the moving grind route; also packages role-specific strategies.
- `d4eab8c5a4f0`: Uses the moving grind route and prayer probability model.
- `d4f9cab6e621`: Avoids prolonged low-level Healer ghost melee and fixes wand path branch range accounting.
- `e9c44042710b`: Keeps four lichen corpses and enables the floating-eye melee guard.
- `f362a746154d`: Contains point-blank archery and the moving grind route.
- `f5d169eb6076`: Includes the moving grind route and a Healer hunger policy.

## Online sources read

- https://nethackwiki.com/wiki/Tourist — early game: use enchanted darts until
  a good melee weapon; Unskilled weapons suffer -4 to hit; around XL5 melee
  training becomes more practical. Ignore explicitly marked 3.7 changes.
- https://nethackwiki.com/wiki/Bat — fast early attacker.
- https://nethackwiki.com/wiki/Jackal — packs kill weak starting roles; darts
  are a valid emergency attack for Tourists; use corridors against crowds.
- https://nethackwiki.com/wiki/Hill_orc — avoid fighting a whole pack at once.
- https://nethackwiki.com/wiki/Dart — enchanted starting darts bridge the gap
  to a better weapon; darts do not need a launcher.
- https://nethackwiki.com/wiki/Talk:Tourist — player discussion of missing
  repeatedly with melee weapons, dagger use, Dexterity and Luck.
- https://nethackwiki.com/wiki/Talk:Multishot — players' tests confirm throw
  and fire both support multishot, including launcherless missiles.
- https://nethackwiki.com/wiki/Talk:Weapon — weapon choice and damage discussion.
- https://gaming.stackexchange.com/questions/5059/avoiding-hunger-in-nethack
  (question and answers read through Stack Exchange API) — players explain
  safe fresh corpses, reserving prayer, and how encumbrance increases hunger.
- https://gaming.stackexchange.com/questions/292577/how-do-i-deal-with-all-of-these-snakes
  (question and answers via API) — players recommend avoiding unprepared
  fights, corridor crowd control and escape resources; explicitly discusses
  3.6 Elbereth changes. Relevant to the pack aspect of the jackal/orc deaths.
- https://raw.githubusercontent.com/maciej-sypetkowski/autoascend/master/README.md
  — bot architecture and challenge write-up overview.
- https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/dothrow.c
  — verified the exact target version: +2 missile to-hit at adjacency,
  launcherless dart use, and Tourist dart multishot at Skilled.

Reddit requests were blocked (403), Google yielded no usable results, and
Google Groups was rate-limited (429); those are not counted as read sources.

## First prototype: close-range darts (rejected)

The Tourist wiki's early dart advice, supported by 3.6.6 dothrow.c and the
Ranger point-blank code in 44f826234d72, suggests using enchanted darts at
close range before XL5 to prevent bat/jackal melee deaths. Keep projectile
checks for peacefuls, pets, Minetown and Elbereth. Preserve melee against
weak targets and special handling for exploding and ranged-only monsters.
Darts chosen by the melee scorer must still be available for throwing:
non-cursed wielded darts are usable ammunition without a weapon swap.

Initial priority-only prototype: all four reference early seeds still lost
early; scores [0.018478,0.017540,0.036888,0.036888]. It exposed the inventory
exclusion and was superseded by the complete implementation of the same
idea. No switch to mid/late-game work was made.

Completed dart handling on the four reference early seeds: scores
[0.050758,0.029109,0.378957,0.074536] (see actual result JSON for exact
values); early losses fall from four to two. Full evaluation follows.

Dart candidate rejected after 10 female games: mean 0.196463 versus 0.332506 for
the same parent seeds. New early deaths on former survivors outweighed rescues.
Both dart code edits were reverted.


## Second early-game hypothesis: skill damage accuracy

The Tourist guide and its player discussion emphasize the cost of Unskilled
melee. Further checked https://nethackwiki.com/wiki/Skill and the exact 3.6.6
https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/weapon.c
(`weapon_dam_bonus`): Restricted/Unskilled damage is -2. The bot had +2,
overvaluing untrained weapons by four damage. Test this correction alone.

Skill correction rejected: all four reference early losses remained early;
mean 0.021085 versus reference 0.030916. Reverted completely.


## Third early-game hypothesis: check disarm safety at action time

Further read https://nethackwiki.com/wiki/Untrap and
https://nethackwiki.com/wiki/Arrow_trap (the latter marked 3.6.6). Most disarms
fail two-thirds of the time; failure commonly moves the hero onto the trap.
The old Tourist attempt #21 checked visible monsters only at strategy entry,
BEFORE `go_to`. That explains why it could not prevent the documented seed 1
trap-plus-jackal death: walking to the trap can reveal monsters and lose HP.
The new check is immediately before EACH disarm, after `go_to`, and checks
both current monsters and the existing health safety threshold. This is a
general revalidation of a dangerous action, not a seed-dependent rule. This
is the only retained strategy edit while this candidate is evaluated.


Trap revalidation rejected: all four reference early-loss scores unchanged;
seed 1 died at turn 829 rather than 787 but still scored 0.017540. The stale
check was real, but fixing it did not resolve the survival bottleneck. Reverted.

## Fourth early-game hypothesis: bounded-difficulty shallow leveling

The leading Valkyrie (`1c4099e80253`) and Archeologist (`51a41284fa08`) programs
use an XP-dependent shallow grind route. Read their `_grind_level` mechanism
and https://nethackwiki.com/wiki/Monster_difficulty plus
https://nethackwiki.com/wiki/Monster_generation. Maximum random difficulty is
floor((depth+XL)/2). Grinding Dlvl 3 at XL5-6 and Dlvl 2 at XL7 keeps this cap
at four, with better XP and more chances to get a dwarf's pick-axe than Dlvl 1
at XL5-6. The shallow route should shorten exposure to hunger, werecreatures
and accumulated combat, targeting reference early losses 6 and 12. It is an
early-game change; no switch to later stages was made. Only GRIND_LEVELS is
changed, enabling the existing route implementation. Dart, skill and trap
changes are all absent from the final candidate.

Shallow route rejected on four female games (6,12,2,5): mean 0.106404; both
early-loss seeds remained early and both former survivors lost progression.


## Isolate the useful dart mechanism

The aggressive point-blank policy caused new early losses, while the initial
priority-only test did not change the two earliest trajectories. Test the
inventory correction alone: a non-cursed dart stack remains eligible as
ammunition even if the melee scorer selected or wielded it. This preserves
all original combat priorities, shot safety checks and melee weapon reserve
rules for real melee weapons. NetHack 3.6.6 dothrow.c permits throwing the
wielded stack without a swap. This is the same dart-use hypothesis isolated
from the rejected close-range aggression policy. No route, damage-table,
trap, prayer or camera change remains.

Ammunition availability only rejected on six female games: mean 0.033190.

Exclude missile melee rejected on six female games: mean 0.134705.


## Food-aware rescue descent

The trace of the unchanged bat-loss game (from the trap candidate, whose
seed 0 trajectory stayed identical) exposed the transition: a failed prayer
at T1341 triggers rescue descent at XL1, reaching Dlvl3 at XL2 and dying to a
bat. The Tourist guide advises slow early preparation, and the Stack Exchange
food discussion separates food supply from prayer availability. The leader
c526d8d41f20 uses stored lichen food to sustain preparation. Gate the early
rescue trigger on actually having no edible carried food, matching the
existing late-rescue principle. Normal planned/tool/XL descent remains
available. This changes resource-aware early routing, not prayer timing.
All dart/weapon/trap/shallow-depth experiments have been reverted.

Food-aware rescue rejected on six female games: mean 0.213210; only the bat
loss changed, from 0.018478 to 0.021062, still early. All other scores tied.


## Structural prayer model (rejected after ten games)

Ported the prayer model from `/refs/top/0716a5964bc4`, including its 3.6.6
monster data and prayer integration. Read the complete model and the relevant
agent call sites, plus https://nethackwiki.com/wiki/Prayer. This is a single
coherent decision model: track prayer timeout distribution, Luck, alignment
and divine anger; distinguish actual major HP trouble from merely low HP;
compare emergency healing probability with near-term combat mortality.
The earlier discarded LOWHP_EXACT experiments only tightened a threshold;
this model also supplies earlier viable emergency prayers, lasting-anger
vetoes, sacrifice recovery and fainting threat decisions. Its source describes
why the old HP<12 rule unnecessarily angers gods at nearly full HP, exactly
as the bat-loss trace showed at 11/12 and 10/12 HP.

Copied source modules live under `autoascend/nhmodel/`. Existing agent methods
call them, with the peer's error fallback. A driver restart has no model
history, so it uses the original policy. Adapter and contract are unchanged.
No dart, weapon, trap, shallow-route or food-aware-rescue edits remain.

Checks: compilation and make_agent construction/close passed. Focused model
checks passed for no HP prayer at 11/12 HP, critical HP prayer after initial
cooldown, anger persisting after Luck recovers, and mollification clearing
anger. The initial fixture omitted prop_mask, then expected the first prayer
two turns earlier than the source model's conservative startup margin; both
fixture errors were corrected without changing the strategy.

Prayer model rejected after ten female games: 0.075127 versus 0.332506 for the matched parent sample. Reverted completely. Full evaluation was stopped after this clear regression; this does not count as an all-seed failed attempt for switching to later stages.

## Pack positioning

The accepted player answer at https://gaming.stackexchange.com/questions/292577/how-do-i-deal-with-all-of-these-snakes recommends corridors, or even corners, to reduce simultaneous attackers. The Jackal and Hill_orc wiki pages also describe pack danger. Implement short retreats to nearby narrow terrain when at least three threatening monsters approach, before being surrounded. Do not move toward more adjacent attackers or try to outrun an adjacent faster monster. This targets the jackal/werejackal and hill-orc early deaths; no switch to later-stage work.

Pack positioning: semantic safety cases passed (pack retreat; no retreat for lone enemy, adjacent faster enemy, or pit). First four female early-loss scores: [0.018478, 0.01754, 0.029109, 0.074536]. Three remain early; the hill-orc game reaches Dlvl7. Survivor sample follows.

Pack positioning rejected after eight female games: 0.241423 versus 0.304106. Three survivor scores tied, but one fell from 0.554 to 0.037, outweighing the rescue to Dlvl7. Reverted.

## Prompt unloading after polymorph

Read https://nethackwiki.com/wiki/Lycanthropy and https://nethackwiki.com/wiki/Encumbrance, plus exact 3.6.6 src/hack.c. Animal forms have sharply reduced carrying capacity; overloaded characters cannot move, attack or eat. The unchanged hill-orc loss trace shows transformation followed by over 200 turns of failed movement, until hunger finally permits were_unload. Remove that hunger/food prerequisite so the existing overload recovery runs when movement becomes blocked. Preserve its food reserve and ordinary post-transformation pickup handling. This is an early survival state-handling fix, not prayer tuning.

Prompt unloading rejected: [(6, 0.029109), (12, 0.050758), (4, 0.425836)]. Former survivor tied, both early losses remained early, and seed6 lost score. Reverted.

## Summoned allies in were form

The same Lycanthropy reference describes #monster: summon allied animals for 10 power while transformed. Verified in exact NetHack 3.6.6 polyself.c dosummon() and were.c were_summon(): 1–5 allied rats/canines appear. The bot already tracks lycanthropy but never uses this ability. Use it against nearby hostile monsters in an explicitly recognized were-animal form; the ability can supply blockers and attackers during the vulnerable, armorless form. This targets the two were-associated early deaths without altering ordinary human combat, prayer, or inventory policy.

Allies first measured version: [(6, 0.029109), (12, 0.425836), (4, 0.036888)]. Summoning rescues the hill-orc early loss to Dlvl23, but causes a new early loss on the former survivor; it repeatedly summons on successive turns. Refine the same ability implementation to at most one call per animal transformation, so it supplies help without repeatedly sacrificing combat turns. An earlier incomplete run was stopped because the form check used display letters rather than NLE monster-class constants; that check was corrected and verified before these measured results.

One-call-per-transformation version rejected: [(6, 0.029109), (12, 0.050758), (4, 0.050758)]. It lost the early rescue. The regression trace in the unrestricted version includes an ordinary iguana fight; summoning for any single enemy is too broad. Restrict the ability to packs (at least two nearby hostiles), matching the original pack-survival hypothesis and player advice. Keep multiple calls available for ongoing pack pressure.

Pack-only summon trigger tied the three reference scores: [(6, 0.036888), (12, 0.050758), (4, 0.425836)]. It missed the dangerous initial contact before enemies summon their own pack. Test a contact trigger instead: use allies when a hostile is already adjacent, not merely visible at range. This preserves the ability against a lone summoner while avoiding idle-time pet creation before combat.

Contact-trigger sample: [(6, 0.029109), (12, 0.425836), (4, 0.074536)]. The early hill-orc loss reaches Dlvl23; former survivor reaches Dlvl8 (down from23). Sample sum slightly improves, so proceed to all 30 pairs rather than infer the overall result.

Broad contact summoning rejected on all 30 pairs: overall 0.334248. It rescues an early loss but reduces later progression in several survivors. Final refinement of the same ability: honor the bot's existing poly_hp_is_buffer distinction. A dying animal form returns the hero to the saved human HP (verified in 3.6.6 polyself.c rehumanize); preserve ordinary combat when that human HP is healthy, summon as an emergency resource when it is not. No new HP threshold is introduced.

## Retained result and validation

All 30 candidate pairs completed in the `local` namespace. Overall: 0.412596612; supplied best: 0.3896; target: 0.3996. The missing male baseline was evaluated once, yielding combined parent mean 0.386402326. Female baseline games were not repeated.

- tou-hum-neu-fem: 0.402299515 -> 0.404727387; early losses 4/15 -> 3/15.
- tou-hum-neu-mal: 0.370505137 -> 0.420465836; early losses 4/15 -> 3/15.

Overall early losses: 8/30 -> 6/30. The previously early hill-orc game now reaches Dlvl23 for both identities. Individual regressions remain, but both identity means rise.

Only `summon_were_allies` and its scheduler call are retained. It uses the ordinary NetHack `#monster` ability in a recognized were-animal form, with 10 power, adjacent hostiles, and no safe human-HP buffer. Existing emergency healing remains higher priority. Failed commands disable the ability to prevent a zero-turn loop. No seed, identity or dungeon fingerprint conditions are used.

Checks passed for sufficient/insufficient power, healthy human buffer, hallucination, human versus animal forms, absence of adjacent enemies, rejected-command fallback, imports, and make_agent construction/close. All 30 actual games exercised reset/act. Diff whitespace checks passed. No identical seed/program evaluation was repeated. No switch to mid- or late-game optimization was made.

Files: `summon-eval.json`, `summon-eval-summary.json`, `baseline-eval.json`, and `exploratory-evals.json`.
