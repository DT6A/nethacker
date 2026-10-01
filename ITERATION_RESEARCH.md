## Retained result

The retained strategy is the independent digging-sequence change in
`autoascend/dive_logic.py`, copied byte-for-byte from its evaluated candidate.
Training: 0.4028609683 -> 0.4092071871. Female 0.3949917435 -> 0.4170764118;
male 0.4107301930 -> 0.4013379623. This misses the 0.4129 target.
Held-out seeds 86547-86561, 15 per character: 0.1147732685 -> 0.1173049572.
Female 0.1329857429 -> 0.1339438434; male 0.0965607941 -> 0.1006660710.
Both held-out character means improve. Training early losses remain 6/30;
held-out early losses remain 18/30. Raw data and source hash are saved in
iteration-training.json, iteration-heldout.json, iteration-parent-heldout.json
and iteration-eval-summary.json. Imports, factory contract, strategy-only
diff and whitespace checks passed. arena_adapter.py is unchanged.

Three fully measured early attempts failed before this later-stage change:
HP buffer 0.1355507905, trap topology 0.4028609683, pet shielding 0.2608789029.
Their mechanisms, failures, early-loss counts, and all research follow below.
No absent proven-neutral fix was identified. The combat-only blind-floor contender scored 0.1147732685 on held-out
seeds, exactly the parent overall and per character. It was not selected:
the digging change has the higher training mean and also gains on held-out
seeds. Both candidates were frozen before those checks. No held-out trajectories were examined.

# Current iteration research (2026-09-30)

## Loss classification
Early = max_depth <= 4 OR explicit Xp milestone <= 5 OR turns <= 3000.
6/30 early losses: seeds 0,1,6 for both Tourist genders. Bat x2, jackal x2,
wererat x2. Early mean 0.0217089755; other 24 mean 0.4981489665.
Replacing early scores with survivor mean would add 0.0952879982 overall.
Thus all candidates must address early losses, unless three different fully
measured early ideas fail. A later permitted switch is documented below.
Survivors cluster at Dlvl22-29 (Medusa/Castle), especially minotaur deaths.
Read their wiki strategies and player Medusa discussion, but early work has priority.

## History
Read /refs/history.md and Tourist sections of /refs/past_runs.md, plus parent's
RESEARCH.md. Failed: minotaur wand intervention, camera/haste variations,
aggressive early darts, skill damage correction, action-time disarm guards,
moving grind route, food-aware rescue, prayer model, pack retreat, early
were-form unloading. Existing summoning and container checks are retained.
No missing proven neutral fix is listed in this run's history.

## All other-character leaders
Opened all 31 other-character .diff files (many delete/relocate whole modules),
then inspected relocated configuration packages and combat mechanisms. The
concrete mechanisms found are below; shared mechanisms are not independent findings.
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

## Online research read this iteration
- https://nethackwiki.com/wiki/Tourist : starting combat is weak; slow preparation, potions, darts, pet assistance.
- https://nethackwiki.com/wiki/Bat : speed22 and pack attacks threaten starting HP.
- https://nethackwiki.com/wiki/Jackal : packs, corridors, early Tourist combat.
- https://nethackwiki.com/wiki/Wererat : regeneration, summoning, lycanthropy and pet protection.
- https://nethackwiki.com/wiki/Potion_of_extra_healing : early permanent HP increase, reserve versus emergency use.
- https://nethackwiki.com/wiki/Talk:Tourist : player discussion of weak to-hit and preparation; potions for HP.
- https://gaming.stackexchange.com/questions/292577/how-do-i-deal-with-all-of-these-snakes : answers read via StackExchange API; pets, escape tools, narrow terrain, explicit 3.6 Elbereth caveats.
- https://gaming.stackexchange.com/questions/5059/avoiding-hunger-in-nethack : answers via API; food, prayer conservation, burden and nutrition.
- https://nethackwiki.com/wiki/Medusa%27s_Island : crossing and bypass options.
- https://nethackwiki.com/wiki/Castle : undiggable floor, drawbridge, moat, trapdoor exits, minotaur/army danger.
- https://gaming.stackexchange.com/questions/297198/how-do-i-deal-with-medusa : answers via API; reflection/blinding and digging past water level, 3.6 applicability.
- https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/potion.c : exact target version confirms extra healing gives 6d8 uncursed and +2 max HP on overheal (+5 blessed).
New-version wiki advice is excluded; exact 3.6.6 source checked for selected mechanics.

## First hypothesis
Convert one spare extra-healing potion into permanent HP at XL1 while safe,
keeping one for emergencies. From Potion_of_extra_healing strategy, targeting
bat/jackal/wererat early deaths. Candidate isolated at /tmp/tourist-hp.

## Second hypothesis (independent candidate)
Only voluntarily disarm a trap when some adjacent walkable terrain is unreachable
by the existing safe pathfinder. The old local terrain-transition count cannot
tell whether the map already contains a route around it. Sources: Untrap,
Arrow_trap (also Dart_trap redirect), Tourist. The 3.6 rules say ordinary
untrapping succeeds only 1/3 of the time; most failures move onto the trap.
This differs from the earlier failed action-time health/monster guard: it
eliminates unnecessary attempts even at full HP with no visible monster.
Targets the trap-associated jackal early loss. Candidate /tmp/tourist-traps.

HP-buffer training result: all 30 pairs, overall 0.135550791, both characters
0.135550791. Early losses 22/30 versus 6/30. The starting reserve is much
more valuable as emergency healing than as two extra permanent HP. Rejected.
No production strategy was changed.

Fresh random held-out block reserved: 86547-86576; the evaluated subset is
86547-86561, 15 seeds per character.
No block in history matched it. Results will only decide retention; no held-out
traces will be inspected or used to choose thresholds.

## Third independent early hypothesis
Respond to a companion's starvation warning by throwing suitable spare food to
an adjacent dog/cat when no enemy is adjacent. Tourist and Pet guides emphasize
companions as protection against early melee; the snake-pack discussion explains
pets as blockers. Exact 3.6.6 dogmove.c dog_hunger confirms starvation reduces
max HP to one third and kills 250 turns later (the modern wiki says one quarter,
so use the source version). dog.c dogfood confirms suitable pet ration types.
This is absent from this bot. Candidate /tmp/tourist-pets; no HP/trap edits.
Also inspected prior attempt #5's detailed research: proactive were cameras,
lycanthrope danger classification and additional dart variants failed; none
are being repeated. Its proven damage-sign fix regressed after three follow-ups,
so it is not an absent neutral fix to carry forward.

Trap topology candidate: 30 training pairs, overall unchanged at 0.4028609683;
early losses remain 6/30. Seed1's jackal loss becomes a later bat loss at
identical progression. Not a proven-neutral game-rule correction: this is a
heuristic choice, so no exception applies. It is not retained.

The pet-feeding draft has not been evaluated and is not a qualifying failed
attempt. Logs instead identify a direct bat-death mechanism: seed0 at t1643
starts a stair retreat at 5/19 HP, takes 4 damage, then tries Elbereth at 1HP.

## Third measured early hypothesis: viable stair retreats
The Bat and Speed pages explain that bats move nearly twice as fast as a
normal hero. Do not walk toward upstairs with an adjacent faster enemy if
sighted, human and able to engrave, and the enemy respects that protection.
Immediate climbing while already on upstairs is still allowed. The normal
combat/shelter policy then handles the fight, without sacrificing a move
on an escape the pursuer can follow. Candidate /tmp/tourist-retreat.
This differs from the previous failed faster-monster shelter experiment:
that changed a shelter exemption but did not stop the higher-priority stair
retreat that consumes the last safe HP here.

Retreat refinement (/tmp/tourist-retreat2): account for enemies able to cover
their current distance in a turn, and do not exempt a lone fast weak monster
from shelter. Female early sample became [.0264824495, .0291089860, .0291089860],
all still early. Full training in progress.

Additional source check: NetHack 3.6.6 invent.c look_here returns !!Blind;
mondata.c resists_blnd also confirms repeated flashes cannot frighten already
blinded monsters. Camera-memory was already tried in history #3, so that
is not selected as a new hypothesis.

Next independent early candidates prepared, not yet measured:
- Blind combat bookkeeping: extend the existing dive-only no-LOOK guard to
  tour combat (visible hostile or recent damage). Avoid extra combat turns.
  Exact proof: invent.c look_here in NetHack-3.6.6_Released.
- Pet shielding: when injured, exchange places with an adjacent pet capable
  of fighting the current attackers, only if its square is outside all visible
  enemies' melee reach. Tourist/Pet and the snake-pack player discussion
  recommend pet blockers. This is distinct from feeding the pet, still untested.

Retreat2 all-seed batch did not finish: seed2 for both genders reproduced
the prior iteration's inactivity loop, and it was stopped. Many completed
survivor games regressed badly. No aggregate score is assigned and it does
NOT count as a fully measured early attempt for the switching rule.

Pet shielding early sample: original female seeds 0,1,6 all unchanged.
Full validation in progress; no final judgement yet.

Blind combat LOOK guard early sample: original female seeds 0,1,6 all
unchanged. Full validation in progress; completed survivor rows include
both unchanged and improved games. No promotion or late-stage switch yet.

Additional early candidate: enable the existing HOLD_LOOP mechanism, which
the leader's _hold_loop and dig_first comments explain. It keeps a defensive
strategy active instead of allowing a lower-priority exploration/combat action
to run between its steps. Read Elbereth wiki and exact 3.6.6 uhitm.c; normal
attacks call u_wipe_engr(3). Original early female sample remains unchanged;
seed2 control still running. No full-score claim.

## Completed early attempts and permitted switch (23:57 UTC)
1. HP buffer: 0.1355507905 overall (both identities), early losses 22/30.
2. Trap topology: 0.4028609683 overall, exactly parent, early losses 6/30.
3. Pet shielding: 0.2608789029 overall; female 0.2592923482, male
   0.2624654576; early losses 16/30. Original six early-loss seeds unchanged.
All three were measured on all 30 training pairs, with no overall gain.
Thus switching to the later-survival blind bookkeeping improvement is now
permitted. HP consumption sacrificed emergency healing; trap avoidance moved
one loss to a later bat without progression; pet shielding disrupted productive
grinds without rescuing original early seeds.

Blind combat-only complete training: overall 0.4058901669, female
0.3968970474, male 0.4148832863. Early losses 6/30. Both identities improve,
but the pooled gain is only 0.0030291986. Broader version under test removes
automatic blind floor scans also outside combat, since the parser expects
sighted descriptions and LOOK consumes a turn regardless of nearby enemies.
This is the same action-cost hypothesis; no thresholds or held-out traces
were used to select it.

HP candidate held-out 86547-86561 (15 per character): overall and each
identity 0.1268718261. Parent held-out: overall 0.1147732685; female
0.1329857429, male 0.0965607941. HP candidate remains rejected for its
large training loss. No held-out trajectories were examined.

Hold-loop screen: female 0,1,6 and survivor control2 all exactly the same
scores as parent. Not a fully measured early attempt and not selected.

## Final independent candidate: keep the digging escape in control
The other-character leader /refs/top/0875c3519bed/pf_s25p8/dive_logic.py
(dig_first / ESCAPE_V2) explicitly describes the lower-priority action that
runs between separate escape activations. Port its bounded 40-action loop,
rechecking the existing eligibility and emergency hooks after every action.
The parent returns after one action; this can allow a combat action to erase
the engraving before the next dig. uhitm.c calls u_wipe_engr(3) on attack,
and mhitu.c missmu calls stop_occupation even on a miss. This targets deep
dragon/raven/ant and approaching-monster losses, after the three qualifying
failed early attempts. No early policy, thresholds or item choices changed.
Candidate /tmp/tourist-dig-sequence; full training planned after the broader
blind-floor batch, then matched held-out validation if competitive.

The broader blind-floor draft is a policy experiment, not an absent proven
neutral fix: the parent already documents LOOK's cost and deliberately keeps
quiet tour floor/container bookkeeping. Partial results show that removing
those checks can harm successful grinds; it will not be retained on those
results. The combat-only version preserves that quiet bookkeeping.

Broader blind-floor policy full training: overall 0.3475232170, female
0.3553924417, male 0.3396539923, early losses 10/30. Rejected. This supports
preserving quiet floor/container bookkeeping, as the combat-only guard does.
No code was changed after inspecting any held-out candidate results.

Dig-sequence full training started 00:04 UTC, after all earlier batches
finished. The code keeps the unchanged one-action predicates/body in
_dig_first_step, with the peer's bounded outer loop and per-action emergency
preemption. All experimentation must end by 00:26 UTC.

Dig-sequence full training: overall 0.4092071871 (+0.0063462188), female
0.4170764118 (+0.0220846682), male 0.4013379623 (-0.0093922306).
Early losses 6/30. The female seed8 gain is offset by a male seed8 loss;
seeds3 and9 improve for both genders. This is a general scheduling change,
with no identity/seed branches. It misses the +0.01 target and now needs
held-out validation, particularly for the male score. Held-out run started
00:14 UTC on the unchanged candidate, seeds86547-86561 for each identity.

Final comparison: combat-only blind guard held-out overall 0.1147732685,
female 0.1329857429, male 0.0965607941, exactly parent. Dig-sequence is
retained with the higher training score and positive held-out gains for both.

Coverage limitation: the training-rejected trap, pet-shield and broader
blind-floor variants did not receive held-out evaluations. Both training-
positive contenders and the HP-buffer variant did receive 15 matched held-out
seeds per character. No claim of held-out validation is made for other drafts.
All experiments are stopped; no game/seed/program pair was rerun to confirm
a score. No new policy edits followed held-out results.
