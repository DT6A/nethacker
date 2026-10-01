# Iteration 8 research and validation

## Required research, completed before selecting a change
1. Parent losses: 6/30 (20%) early, seeds 0, 1, 6 for each gender.
   Bat x2 (depth3, XL2, 1644 turns), jackal x2 (depth3, 787 turns),
   wererat x2 (depth1, XL5, 5920 turns). Early mean 0.021708975459;
   other24 mean0.500148367938. Relative to survivor mean the early losses
   cost0.095687878496 overall. Early-game changes are mandatory.
   Survivors cluster at depths19–29, including Medusa/Castle deaths to
   minotaurs, dragons, snakes, sharks and drowning. Read those level guides,
   but no later-stage work was selected until three early attempts failed.
2. Read /refs/history.md, /refs/past_runs.md, prior detailed research in
   /refs/attempts/5/research.md, /refs/attempts/7/RESEARCH_ITERATION_7.md,
   and inherited ITERATION_RESEARCH.md. Kept: allies, digging sequence.
   Also reviewed #1 minotaur wands (regressed) and #2 Castle passage (kept
   in a different lineage; inactive in this parent). These are not retried.
   Failed: aggressive darts (new early losses), damage-sign correction
   (accidentally suppresses dagger training/dart availability; three failed
   follow-ups), HP-buffer quaffing, trap handling, pet shielding, homeward
   routing, door recovery, armor buying. Armor buying had a claimed local
   gain but official evaluation discarded it. No missing proven-neutral fix.
3. Opened README and all31 other-character leader diffs. Read added combat,
   survival, configuration and hypothesis excerpts; much is shared code or
   relocated role packages. Concrete mechanism inventory follows (shared
   findings agree with the previous iteration's inventory):
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

- `7a51fb10f011`: Its strategy packages use the XL5/Dlvl3, XL7/Dlvl2 grind route absent from the parent configuration.
- `b7b5c4432930`: Its pf_base package uses probabilistic prayer success and incoming-harm models, rather than the parent's fixed gap.
- `54a4478212c0`: Its Ranger point-blank ranged policy avoids swapping to melee when an enemy closes.
- `e3d145aa2b6c`: Its Ranger point-blank ranged policy retains effective ranged combat at adjacency.


4. Successful online lookups this iteration (using urllib/curl-equivalent):
- https://nethackwiki.com/wiki/Tourist — weak early melee, trained darts, pets,
  food to tame domestic animals, armor. Excluded future3.7 camera XP.
- https://nethackwiki.com/wiki/Bat — speed22, 1d4 bite, erratic movement.
- https://nethackwiki.com/wiki/Jackal — packs, corridors, weak starting roles.
- https://nethackwiki.com/wiki/Wererat — regeneration, 2d4 human attacks,
  infectious animal form and summons; pet help and corridor advice.
- https://nethackwiki.com/wiki/Dart — launch-free throwing, skill growth.
- https://nethackwiki.com/wiki/Castle — no floor digging; moat and drawbridge.
- https://nethackwiki.com/wiki/Medusa%27s_Island — water crossings and gaze.
- https://nethackwiki.com/wiki/Standard_strategy — recover before critical HP.
- https://nethackwiki.com/wiki/Hit_points — natural regeneration and healing.
- https://nethackwiki.com/wiki/Pet — hunger, loss of support, pet following.
Player discussions actually read:
- https://nethackwiki.com/wiki/Talk:Tourist — dagger progression, poor to-hit,
  skills/attributes/Luck; protection racket is unreliable for Tourists.
- https://gaming.stackexchange.com/questions/292577/how-do-i-deal-with-all-of-these-snakes
  — answers read through api.stackexchange.com/2.3/questions/292577;297198/answers?site=gaming&filter=withbody;
  corridors and pets limit simultaneous attackers. Disregard pre3.6 Elbereth.
- https://gaming.stackexchange.com/questions/297198/how-do-i-deal-with-medusa
  — same API; reflection/blinding and bypass to Castle. Disregard retracted
  nonexistent anti-stoning jewelry advice.
- https://nethackwiki.com/wiki/Talk:Pet — hunger, lost pets and healing.
Google, Bing and Reddit searches also attempted; challenges/blocked results
are not counted as substantive sources. Raw fetched text is in /tmp/research8.

5. Selected first idea: quiet early recuperation, from Standard_strategy,
Tourist and Hit_points, to prevent bat/jackal attrition. The existing early
strategy explicitly explores until80%HP; the new strategy rests until that
same target when safe, and yields to combat/hunger/emergencies. This is not
the prior Elbereth threshold, door shelter or homebound routing experiment.

A partial parent diagnostic (7000 actions, stopped before the known death)
showed seed6's dog fell through a trap at turn3091. Thus pet feeding would
not fix that specific loss; it was considered but never implemented.
An initial diagnostic logger failed before taking useful actions and was
terminated; it is not an evaluation result.

## Validation plan
Fresh random block9947–9976,30 seeds per gender, because prior recorded
held-out gaps are large. Freeze candidates before held-out evaluation;
read only scores, never held-out trajectories. Do not repeat deterministic
seed/program evaluations. Workspace retains the parent until a winner passes.

## Second early hypothesis, prepared while first training batch completes
Regenerating enemies require concentrated damage (Wererat/Lycanthrope wiki).
Use an already available trained projectile against them even at close range;
retain the existing pet/peaceful line-of-fire, Minetown, ammo eligibility and
Elbereth safeguards. Source peer5088ac9a49a3 shows point-blank shooting is
useful when the projectile is a trained weapon. Unlike the failed broad dart
policy, ordinary enemies are unchanged and no global ammo-eligibility change
is made. This targets the two human-wererat losses from full43HP at AC9.
Exact3.6.6 include/monflag.h confirms M1_REGEN=0x00800000; NLE's human and
animal wererats both expose that flag. Bat/jackal do not.
Additional lookups: Regeneration (disambiguation), Lycanthrope,3.6.6 mon.c
and monflag.h; StackExchange search for werewolf encounters found289572
(the player's infection shed their gear). Talk:Wererat was404, not counted.

Quiet recuperation all30:0.120683630945 overall; female0.109394944906,
male0.131972316985;20early losses. Original six sample mean0.012005980120,
all six still early (seed6 now dies to a dart at turn352). Rejected.

Regeneration-specific missiles early six: seeds0/1 unchanged; seed6 reaches
Dlvl26,0.506760563380, both genders (parent0.029108986017). Two of six
original losses rescued. Remaining24 training pairs running. No held-out
outcomes read, and no changes to the candidate after its first score run.

Regeneration missiles all30:overall0.189932942606, female0.185155682266,
male0.194710202946;12early losses. Rescues original wererat pair but
reshapes routine fights and loses multiple former survivors. Rejected.

Emergency-dart follow-up: keep missiles for critical HP, after available
healing/prayer, against adjacent fast enemies that cannot safely be outrun.
Allows the wielded dart stack explicitly for this one emergency, without
changing normal inventory/ranged eligibility. Preserves line-of-fire and
Elbereth checks. Sources Tourist/Bat/Jackal and peer point-blank archery.
First implementation uses !diving as the early gate; original0/1 unchanged,
6 regresses to0.0211845677. Full24 remaining training running.
Code inspection found !diving excludes the very early rescue dives after
failed prayers (including the bat loss). Corrected draft uses XL<=5,
the user's early-game definition and Tourist guide's weak-melee phase.
It remains frozen in a separate copy, awaiting its first evaluation.

Emergency darts v1 all30:overall0.366213710796, female0.363053567874,
male0.369373853718;8early losses. Rejected. The XL-based gate v2 early
sample gives0:.0264824495,1:.0175395358,6:.0211845677 for both genders;
still6/6 early, with a small bat-death delay outweighed by the seed6 loss.
It is not promoted. This is a refinement of the same missile idea, not an
independent qualifying early attempt for the later-stage rule.

Third independent early idea: actual hand-thrown projectile range.
Proof: exact3.6.6 dothrow.c throwit() uses ACURRSTR/2 minus object weight/40,
with levitation recoil. NLE winrl.cc maps ACURRSTR to NLE_BL_STR25 (the
legacy field named strength_percentage). Parent returns7 unconditionally.
Throw wiki confirms role-independent strength/weight range and that thrown
weapon stacks are split; tests verify strength11 => range5 for50 darts,
levitation =>4, minimum1; launcher behavior remains outside this narrow fix.
Targets early missile attrition/weak attacks, particularly the wererat loss.
Early6:0/1 unchanged;6 advances toXp7,0.050758, but remains at depth1.
Full30:overall0.110188029585, female0.114574449439,male0.105801609731;
19early losses. Regressed seeds2,3,4,5,7,8,9,10,11,12,14 for BOTH genders.
The proven correction cannot be called neutral. Investigating the accidental
benefit rather than immediately abandoning it. Partial parent/corrected
seed2 diagnostics capped at15000 actions (well before either known death)
compare decisions; they are not duplicate full-score checks.
Prepared follow-up1: keep true range and explicitly wait once for an
approaching enemy to enter range, preserving the old wasted shot's stance.
Stationary/passive hazards are approached rather than waited for indefinitely.

Confirmed first divergence for regressed female seed2: both versions match
through action7490. At T7598, XL5,47HP, hero(6,42), a gnome is six squares
east at(6,48). Parent throws (out of actual range) and stays(6,42); corrected
version moves east to(6,43). At T7599 the gnome is five squares away from the
parent, four from the correction. By T7602 it is three vs two squares away.
Thus the wrong range accidentally buys an extra turn of ranged combat by
holding position. This is a traced effect, not merely inferred from endpoints.
Follow-up1 restores the stance with a bounded wait; sample six in progress.

Range correction follow-ups: both bounded search and actual WAIT preserve
stance but score identically on female seeds0,1,6,2,4,8. Scores respectively
.0184784,.0175395,.3088124,.4451814,.4258361,.0241601.
The original wererat loss is rescued, but seed8 collapses from .365 to .024
(starvation on Dlvl1). Thus the correct range plus deliberate waiting still
fails to preserve the old game's combat/RNG trajectory. Dropped after tracing
the accidental benefit and two follow-up implementations, not called neutral.

Switching to later-stage work after three different fully measured early
ideas failed: recovery .120684, regenerative-enemy missiles .189933, actual
range .110188 (parent .404460). The first reshapes the productive levelling
loop; the second rescues wererats but degrades routine fights; the third
removes accidental stand-off attacks, and two explicit-wait follow-ups still
regress. Emergency-dart refinements were also unsuccessful (.366214 full).

Later-stage hypothesis from peer1c4099e80253 and3.6.6 monmove.c onscary:
a scare scroll on the ground protects against minotaurs/humans (including
blinded monsters) that ignore Elbereth, without being erased by attacks.
Targets original minotaur deaths (female2/14,male2), Elvenking(female8),
soldiers(both11), and late melee pressure. A bounded strategy drops one known
scroll or possible labels against an Elbereth-ignorer, fights/digs from the
square, avoids immune monsters, and abandons a false pile on melee damage.
No inventory-policy changes: uses scrolls already carried. Frozen candidate
/tmp/tourist-scare, full30 training running. Original parent stays /workspace.

Broad ward result .3590908 (female .3638375,male .3543441),6early.
Important review correction: this candidate called a peer-only signature,
_note_dropped(...,force=True), absent from the parent. Thus these outcomes
are not clean strategy evidence. The first Castle-only trial was stopped
before completion when this was discovered. Corrected frozen candidate
/tmp/tourist-scare-castle-fixed adds optional forced recording of ward drops
and honors those records even when normal SCARE_KEEP is disabled. Ordinary
inventory drop behavior is unchanged. Full30 restarted with different code.
The scope matches peer Castle wards: depth>=25 (earliest possible Castle),
not a training-seed-specific encounter. Focused eligibility and forced-drop
fixtures pass; normal retention remains disabled and non-ward tiles unaffected.

Source/integration audit: all invoked parent APIs checked; ward eligibility,
immune-monster exclusions, failed-label suppression, leaving the square, and
forced drop bookkeeping pass mock fixtures. No known neutral fixes added.
The final inventory diff only enables explicit ward-drop records; ordinary
SCARE_KEEP remains false. Candidate remains frozen throughout evaluation.

Corrected Castle ward training ALL30: overall0.426664998065 versus parent
0.404460489442 (+0.022204508623). Female0.420223588222 vs0.395017676506;
male0.433106407907 vs0.413903302378. Early losses6->6. Meets training target.
Frozen code now undergoing paired held-out validation on9947–9976 (30 each),
in two blocks of15 each identity. Read scores only; no tuning on those runs.

Held-out parent first block9947–9961 (15/gender,30total): overall
0.082623150932;female0.081830564882,male0.083415736982. This is only
half the planned block, not a final comparison. Candidate batchA started
unchanged. No held-out causes, depths, or action trajectories inspected.

Matched held-out batchA complete: candidate0.084121153950 vs parent
0.082623150932 (+0.001498003019);female unchanged0.081830564882;
male0.086411743019 vs0.083415736982. Partial gate passes. Parent batchB
(seeds9962–9976,both identities) running. Code remains frozen.

Parent held-out ALL60 (9947–9976,both genders) complete: overall
0.084442523519;female0.084839507846,male0.084045539193. Final candidate
batchB started03:26UTC, before the03:34 no-new-evaluations cutoff.

## Final result and installation
Held-out ALL60 candidate0.085191525029 vs parent0.084442523519
(+0.000749001509). Female unchanged0.084839507846;male0.085543542211
vs0.084045539193. No overall or character loss. This passes the held-out
bar, though its gain is much smaller than the+0.0222045 training gain.
Seeds9947–9976,30/gender,all evaluations namespace local; no held-out
trajectory/causes were read and no code was tuned on these results.
Four frozen, hash-verified strategy files installed in /workspace. Imports,
make_agent/reset/act interface, eligibility guards and forced-drop checks
pass. arena_adapter.py is byte-identical to parent. No neutral fixes added.
Training early losses remain6/30 (two bats,two jackals,two wererats).
Full numerical evidence is in iteration8-evals/{summary,training,parent-heldout,heldout}.json.

Validation limitation: rejected prototypes were screened on training only;
they did not receive the requested held-out runs. Final candidate and parent
both received all60 matched held-out games. No deterministic full evaluation
of an unchanged seed/program pair was repeated; partial diagnostics and the
stopped invalid-signature candidate were distinct diagnostic/invalid runs.
