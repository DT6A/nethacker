## Final retained change
Potion conservation (candidate A) passed the complete paired held-out gate
and was installed in autoascend/agent.py at 05:06 UTC. No other strategy change
is included. Training parent 0.412354363504 -> candidate 0.415351912530;
held-out parent 0.138366233885 -> candidate 0.140362121861, on fresh seeds
6390–6419 (30 per identity). Held-out female 0.148864505749 -> 0.148755435749
(-0.000109070001); male 0.127867962020 -> 0.131968807974. No evaluation errors.
Early losses remain 6/30; the gain is below the requested 0.4224 target.
Source: Tourist and extra-healing wiki advice to preserve starting healing
for emergencies; targets potion depletion before early bat/jackal/wererat fights.
The armor prototype's apparent gain is INVALID: its added branch was inactive
under the actual parser invariant. It is excluded from all retention decisions.
No proven neutral fixes were measured or are awaiting carry-forward.
Final import and make_agent/reset/act checks passed; adapter and bot unchanged.
All three valid candidates completed their held-out comparisons with no errors.
Weapon readiness and camera use were rejected; details are recorded below.
No experiments or long evaluations were started after 05:10 UTC.

# Iteration 9 research and evaluation

Research preceded selecting or writing strategy changes.

## Parent losses
Early definition: max_depth <=4, Xp milestone <=5, or turns <=3000.
6/30 early (20%): bat twice (seed0,depth3,XL2,1644 turns), jackal twice
(seed1,depth3,787 turns), wererat twice (seed6,depth1,XL5,5920 turns).
Mean early .0217089754593; other24 .5100157105155. Replacing early scores
with survivor mean would add .0976613470112 to overall. Early work required.
Survivors die at depths19–29, clustering around Medusa/Castle, to minotaurs,
dragons, sharks and ordinary melee. Those guides/discussions were read too.

## Prior work
Read /refs/CONTEXT.md, history.md (all eight entries), past_runs.md's relevant
Tourist history, and the inherited detailed research for iterations4,6,7,8.
Kept changes: were allies, protected dig sequence, Castle scare scrolls.
Failed: broad and regeneration-specific missiles, true throwing range (old
out-of-range shots accidentally held position), max-HP potion use, recovery,
pet shielding, armor shopping, homeward routes, door shelter, prayer models.
No absent proven-neutral fix was listed. Parent already has chest handling
and prior mapping/camera fixes. No later-stage switch has been made.

## All other-character leaders
Opened every one of the31 other-character .diff files. Several are truncated
at300kB because they replace autoascend with role packages, so also read their
packaged configuration. Read combat, survival and configuration hunks; shared
mechanisms repeat across leaders. Concrete inventory (confirmed against the
current snapshots; many agree with iteration8):
- `0716a5964bc4`: Models prayer success against the probability of surviving three more combat turns.
- `0875c3519bed`: Uses XL-dependent grind depths (Dlvl 3 at XL5, Dlvl 2 at XL7) in its strategy packages.
- `1c17ee5b7216`: Uses XL-dependent grind depths rather than remaining on Dlvl 1.
- `1c4099e80253`: Moves the early grind to Dlvl 3/2; its comments report fewer hunger prayers and grind deaths.
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

- `7a51fb10f011`: Its strategy packages use the XL5/Dlvl3, XL7/Dlvl2 grind route absent from the parent configuration.
- `b7b5c4432930`: Its pf_base package uses probabilistic prayer success and incoming-harm models, rather than the parent's fixed gap.
- `54a4478212c0`: Its Ranger point-blank ranged policy avoids swapping to melee when an enemy closes.
- `e3d145aa2b6c`: Its Ranger point-blank ranged policy retains effective ranged combat at adjacency.
- `77455e96f688`: Uses the moving grind route and a prayer probability model in its role packages.

## Online sources actually fetched and read
- https://nethackwiki.com/wiki/Tourist — weak melee; preserve/use starting resources, trained darts, pet support; disregard upcoming3.7 sections.
- https://nethackwiki.com/wiki/Bat — speed22,1d4 bite, erratic motion.
- https://nethackwiki.com/wiki/Jackal — early packs and corridor advice.
- https://nethackwiki.com/wiki/Wererat — regeneration, human/animal forms, summons.
- https://nethackwiki.com/wiki/Talk:Tourist — player discussions of poor to-hit, dagger skill, dexterity/Luck and early equipment.
- https://gaming.stackexchange.com/questions/292577/how-do-i-deal-with-all-of-these-snakes — player answers: escape supplies, corridors/pets, don't engage a pack in the open; ignore pre3.6 engraving advice.
- https://gaming.stackexchange.com/questions/297198/how-do-i-deal-with-medusa — player answers: reflection/blinding and digging past her island to reach Castle supplies.
- https://nethackwiki.com/wiki/Medusa%27s_Island — crossings and gaze.
- https://nethackwiki.com/wiki/Castle — undiggable floor/moat/drawbridge.
- https://nethackwiki.com/wiki/Potion_of_extra_healing —6d8 uncursed healing, emergency resource or maxHP use.
- https://nethackwiki.com/wiki/Healing — natural recovery; its old prayer thresholds are NOT used.
- https://nethackwiki.com/wiki/Standard_strategy — retreat/recover before critical HP.
StackExchange questions/answers accessed via api.stackexchange.com/2.3
with filter=withbody; also searched questions for werewolf/healing.
Downloaded texts under /tmp/research9. More than5 lookups and2 substantive
player discussions, including the target role page.

## First hypothesis: reserve healing for danger
From Tourist, Potion_of_extra_healing and Standard_strategy: preserve known
healing potions during quiet early recovery, so bat/jackal/wererat fights
still have healing available. This differs from failed proactive maxHP use:
it spends fewer potions, rather than drinking one preemptively.
XL<=5 only; recent damage or a visible monster within5 squares preserves
the parent's healing action. No changes to prayer, movement or thresholds.
Isolated /tmp/tourist-reserve; workspace remains the parent.
Early6: seed0 and6 unchanged; both seed1 advance .0175395 -> .0368876,
last10968 turns but still depth3, so all6 remain early under the depth rule.
Remaining24 training in progress.

## Held-out plan
Fresh random block6390–6419,30 seeds per character,60 games. Prior recorded
held-out gap is large, so use30 despite the unexpanded generalization prompt.
Parent and each frozen candidate run on the same block. Only scores used for
final yes/no; no held-out trajectories read and no tuning to those outcomes.

## Additional early candidates prepared independently
B: ready the selected melee weapon while visible attackers remain more than
one turn outside contact, rather than wielding on the first melee turn.
Sources Wield and Tourist wiki, and /refs/top/5088ac9a49a3's Ranger weapon-swap
avoidance. Existing weapon scoring, attack priorities and ammo eligibility
are retained. Applies atXL<=5; disables while blind, hallucinating, polymorphed
or with welded hands. Isolated /tmp/tourist-ready. Not yet evaluated.
C: fill empty armor slots with recognized mundane armor even before BUC test.
Sources Tourist, Armor, Beatitude (87.68% of ordinary armor is noncursed).
Current parent requires known noncurse even for an empty slot; seed6 was
fighting a wererat atAC9. Avoid magical items and require positive estimated
AC improvement. No existing armor is removed to try an unknown item. This
addresses free carried armor, unlike the discarded shop-purchase experiment.
Isolated /tmp/tourist-armor. Not yet evaluated.

A full training: parent .412354363504 (female .404485138786, male
.420223588222); reserve .415351912530 (female .415193172702,
male .415510652358). Early6->6. Gain .002997549, below desired .01;
male loses .004713. Provisional only pending paired held-out.
Parent all60 held-out launched03:52UTC. Code for B/C already frozen before
any held-out outcome. No trajectories from held-out are used for development.
Exact3.6.6 wield.c confirms wield/swap consumes the ready_weapon action;
mkobj.c confirms ordinary armor curse/enchantment probabilities and hazardous
magic types. Additional fetched sources: Wield, Weapon, Melee, Talk:Weapon,
Armor, Curse-testing, Beatitude, NetHack3.6.6 src/wield.c and src/mkobj.c.

Parent held-out all60 complete: overall .138366233885, female
.148864505749, male .127867962020. All completed. Only summary scores/status
read; no held-out causes, depths or actions inspected. Large training gap
confirms the30-per-character validation size. Armor training all30 started
04:07UTC with the frozen implementation. Prepared weapon-readiness remains
unevaluated, and is not counted as a failed early attempt.

C armor full training: overall .422077040268 versus .412354363504
(+.009722676763); female .426786122063 versus .404485138786;
male .417367958472 versus .420223588222 (-.002855629750).
Early6->6, original six unchanged; all30 completed. This is just below the
.4224 aim, but above the strict keep bar. It targets early low-AC exposure,
though available armor did not rescue the known six failures. Held-out in
paired30-game batches started04:17UTC, with no candidate edits.

IMPORTANT: C INVALIDATED by static audit04:18UTC. ItemManager.get_item_from_text
(item/item_manager.py:211) converts every successfully parsed UNKNOWN status
to UNCURSED, so the added unknown-armor branch cannot normally execute.
No code assigns UNKNOWN afterward. Its apparent training gain is therefore
NOT evidence for this idea and it must not be retained. The synthetic fixtures
missed the production parser invariant. Stopped incomplete held-out C batchA;
read no held-out results. This is not a qualifying genuine failed early attempt.
The underlying parent status assumption is dubious, but no correction was
measured and it is NOT claimed as a proven neutral fix.
Prepared B was unchanged since03:49 and now goes to full30 training; all
other strategy files in its copy still match parent. Its branch is reachable:
fight2 normally wields only after selecting melee, whereas B readies at range.

D final early candidate, from Tourist/Expensive_camera/Lycanthrope and exact
3.6.6 uhitm.c flash_hits_mon: use a camera once when an early human were
fight is rapidly consuming HP. Reuses existing30%-in3-turns damage detector
and standard-strategy half-HP retreat advice. Human forms already ignore
Elbereth; animal forms excluded so blindness cannot destroy that defense.
Unlike prior broad/proactive flashes, requires actual rapid HP loss, and
records a completed flash once per species/level (adjacent blindness is
indefinite; resists_blnd prevents a second flash from scaring it). The old
last-resort flash waits until critical HP. Two earlier known failure mechanisms
are explicitly addressed: blinding ward-respecting foes and repeatedly
flashing blinded opponents. Isolated /tmp/tourist-burst-camera, independent
of potion conservation and weapon readiness. All code frozen before first
training run; no held-out trajectories consulted. This is not a later-stage
switch. New retrieved source texts are in /tmp/research9.

B all30: .204400414529 overall, female .204387448044, male .204413381014;
16early losses vs6. Original bat game lasts21094 turns but remains shallow;
weapon preparation changes productive early combat sequences and many old
survivors die early. Rejected for training loss; paired held-out still planned.
D started04:26UTC, max16 concurrent, unchanged code and arena local namespace.

D full30: .406745894734 overall, female .403585751812, male .409906037656;
6early losses unchanged. Rejected: no known early loss rescued and effects
on other fights reduce overall. No claim is made about why the original
wererat encounter failed to trigger (camera availability vs damage window
would need a diagnostic). Eligibility fixtures with actual NLE human/animal
wererat data passed; repeat-flash and stable-health exclusions passed.
No more candidates will be developed. A is the only valid training winner.
A held-out batchA began04:37UTC; B/D held-out comparisons follow as required.
All candidate code remains frozen; workspace strategy still equals parent.

Held-out completion planning04:46UTC: remaining independent runs share a
14-worker budget (A second half8, B all603, D all603). Each uses a foreground
arena command owned by a tool session; no shell background/detached jobs or
turn-ending notification waits. All started before05:10, all results will be
collected. Larger rejected-candidate batches avoid starting fresh evals after
the cutoff. Workspace still parent until A passes all60.
A held-out first30: .107928296880 versus matched parent .108146436881
(-.000218140001), same for both identities; no errors. Not a retention decision
until the second30 complete. No code changes or held-out trajectory inspection.

## Completed comparisons

All results use evaluation-id local. Training is seeds 0–14 for both
identities; held-out is fresh seeds 6390–6419, 30 per identity. No held-out
trajectories were inspected or used for tuning.

| Program | Training overall | Training female | Training male | Early losses | Held-out overall | Held-out female | Held-out male | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Parent | 0.412354364 | 0.404485139 | 0.420223588 | 6/30 | 0.138366234 | 0.148864506 | 0.127867962 | Reference |
| Potion conservation | 0.415351913 | 0.415193173 | 0.415510652 | 6/30 | 0.140362122 | 0.148755436 | 0.131968808 | Retained |
| Weapon readiness | 0.204400415 | 0.204387448 | 0.204413381 | 16/30 | 0.150940611 | 0.153045569 | 0.148835653 | Rejected: training regression |
| Camera burst response | 0.406745895 | 0.403585752 | 0.409906038 | 6/30 | 0.137690563 | 0.147513164 | 0.127867962 | Rejected: training and held-out regressions |

Potion conservation improves overall training by 0.002997549 and held-out
by 0.001995888. Training male declines 0.004712936; held-out female declines
0.000109070, within the requested tolerance. This is a modest gain, below the
0.4224 target. The two former seed-1 jackal deaths survive to turn 10,968
before dying to foxes at depth 3, so they still count as early losses.
Training deltas are archived in iteration9-evals/reserve-training-deltas.json.

Weapon readiness has a positive held-out result despite its severe training
regression; it is not retained under the training acceptance requirement.
This contrast is recorded rather than tuning either candidate to held-out games.
The camera response rescues no original early loss and loses on both sets.

The inactive armor prototype is excluded from this table: the production item
parser makes its added condition unreachable, so its apparent score difference
cannot validate the hypothesis. No neutral fix is claimed.

The only final strategy diff is iteration9-evals/reserve.diff, applied to
autoascend/agent.py. Hypothesis and source comments are directly adjacent.
Import and make_agent/reset/act checks passed. The full machine-readable
summary and completed evaluation rows are in iteration9-evals/.
