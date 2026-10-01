# Tourist iteration 7 research (2026-10-01)

## Required loss split, before choosing a change
Early = max_depth <= 4 OR explicit Xp milestone <= 5 OR turns <= 3000.
Parent: 6/30 early losses, seeds 0, 1, 6 in both identities: bat x2,
jackal x2, wererat x2. Early mean 0.0217089754593; remaining 24 mean
0.500148367938. The gap contributes 0.095687878496 to the overall mean.
Parent overall 0.404460489442 (computed below in result summary).
At exactly 20%, the early-game rule applies.
Survivors cluster at depths 22-29 (Medusa/Castle); Castle and its player
Talk discussion were read, but no late-game change is authorized yet.

## History
Read /refs/CONTEXT.md, /refs/history.md, relevant /refs/past_runs.md, and
previous attempts' detailed RESEARCH / ITERATION_RESEARCH documents.
Existing retained ideas: camera and inventory support, lycanthrope summoning,
dig sequence. Failed ideas include broad darts, proper damage skill penalty
(three follow-ups; old error promotes dagger training and frees darts), prayer
models and thresholds, shallow grind route, trap action-time guards/topology,
HP buffer potions, pet shielding, and early retreat changes. Do not repeat.
No absent proven-neutral fix is listed. Container trap checks are already present.

## Other-character leaders
Opened README and all 31 other-character .diff files, extracting the added
strategy hunks and reading their relevant functions, including relocated
strategy trees. The snapshots are unchanged from the previous iteration;
these mechanisms were independently checked in their diffs / source. Shared
mechanisms appear in several programs; they are not separate discoveries.

| Program | Concrete mechanism absent from this parent |
|---|---|
| 0716a5964bc4 | Alternate Healer strategy proactively uses its starting sleep wand and healing spell, instead of relying only on melee and late emergency items. |
| 0875c3519bed | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| 1c17ee5b7216 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| 1c4099e80253 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| 41c961256c41 | No additional strategy mechanism: this Wizard leader adopts our Tourist strategy and adds regression checks. Its strategy is not a new source to copy. |
| 429cf0108271 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| 44f826234d72 | Point-blank Ranger archery avoids needless weapon swaps; shots can outrank melee even with an adjacent enemy. |
| 47a6c840a4cf | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| 5088ac9a49a3 | Point-blank Ranger archery avoids needless weapon swaps; shots can outrank melee even with an adjacent enemy. |
| 51a41284fa08 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| 54a4478212c0 | Point-blank Ranger archery avoids needless weapon swaps; shots can outrank melee even with an adjacent enemy. |
| 6ecc35e91af2 | Starts a tool-equipped descent at XL7 rather than XL8, reducing exposure to the level-one grind (already tried unsuccessfully in the Tourist history). |
| 725cafa6a87d | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| 7a51fb10f011 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| 7c1ec61015bf | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| 81ea959c3b98 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| 985b175cae53 | Point-blank Ranger archery avoids needless weapon swaps; shots can outrank melee even with an adjacent enemy. |
| ae053ca704ff | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| ae17b4a50322 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| b4c2edc23ce3 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| b7b5c4432930 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| bded98c686e3 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| c49b46fdffa0 | Proactively sleeps dangerous nearby monsters, including lycanthropes; checks reflected-ray safety before zapping. |
| c526d8d41f20 | Alternate Healer strategy proactively uses its starting sleep wand and healing spell, instead of relying only on melee and late emergency items. |
| d44c89c2ffd8 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| d4eab8c5a4f0 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |
| d4f9cab6e621 | Proactively sleeps dangerous nearby monsters, including lycanthropes; checks reflected-ray safety before zapping. |
| e3d145aa2b6c | Point-blank Ranger archery avoids needless weapon swaps; shots can outrank melee even with an adjacent enemy. |
| e9c44042710b | Alternate Healer strategy proactively uses its starting sleep wand and healing spell, instead of relying only on melee and late emergency items. |
| f362a746154d | Point-blank Ranger archery avoids needless weapon swaps; shots can outrank melee even with an adjacent enemy. |
| f5d169eb6076 | Blindfold/towel attacks against floating eyes avoid their paralysis; recover the tool afterward (FEYE_BLIND in the strategy tree). |


## Successful online lookups read before implementation
- https://nethackwiki.com/wiki/Tourist : weak melee/armor; darts, pet assistance, extra healing; disregard 3.7 camera XP.
- https://nethackwiki.com/wiki/Bat : speed 22, 1d4 bites, early fast attrition.
- https://nethackwiki.com/wiki/Wererat : regeneration, summons, infection and armor loss.
- https://nethackwiki.com/wiki/Untrap : 1/3 ordinary success; failures enter traps.
- https://nethackwiki.com/wiki/Floating_eye : passive long paralysis.
- https://nethackwiki.com/wiki/Talk:Tourist : actual player discussion of missing with weapons, stats and Luck.
- https://nethackwiki.com/wiki/Talk:Floating_eye : players discuss long paralysis and making the eye unseen.
- https://gaming.stackexchange.com/questions/292577/how-do-i-deal-with-all-of-these-snakes : question answers fetched via Stack Exchange API; pets, escape tools, corridors, explicit 3.6 caveats.
- https://gaming.stackexchange.com/questions/5059/avoiding-hunger-in-nethack : answers fetched via API; corpses, food reserves, reducing burden and reserving prayer.
- https://nethackwiki.com/wiki/Castle : undiggable floor, moat, entry and trapdoors.
- https://nethackwiki.com/wiki/Talk:Castle : drawbridge safe distances, chest trap version correction, pet leash for trapdoor descent.
- https://nethackwiki.com/wiki/Lycanthropy : regeneration, transformations, lost armor, cure resources.
- https://nethackwiki.com/wiki/Potion_of_holy_water : cure lycanthropy, bless/uncurse equipment.
- https://nethackwiki.com/wiki/Expensive_camera : fleeing is not guaranteed and blind attackers ignore Elbereth.
- https://nethackwiki.com/wiki/Door : close doors to escape early combat; monsters able to pass/open them.
- https://nethackwiki.com/wiki/Close : closing action.
- https://nethackwiki.com/wiki/Standard_strategy : break off combat before critical HP.
- https://nethackwiki.com/wiki/Talk:Door : player discussions of door noise and pets finding routes.
- https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/lock.c : doclose, requirements and chance of resistance.
- https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/monmove.c : m_move, can_open requires hands/non-tiny; giants break doors, amorphous and wallwalking bypass.
Google search returned a challenge and Reddit search returned 403; these are
not counted as successfully read discussions. Wiki Talk and Stack Exchange
answers above were successfully read.

## Diagnostic (not a repeat score check)
A truncated diagnostic replay of female seed 6, stopped at 7100 actions before
death, collected state/action stacks at the end of the known losing fight.
At turn 5908 it engages a human wererat, 43/43 HP and AC9. Repeated melee
reduces HP to 8 by 5916; an unknown potion restores energy rather than HP.
Transformation sheds shirt/helm/daggers, allied summons spend two turns, and
it reverts at 4 human HP. Thus no attack wand was being withheld, and an
Elbereth-immunity change would not address the initial loss of health.

## Candidate A: physical door shelter
One idea from Door#Use_doors_to_get_out_of_combat: an injured hero closes a
nearby separating door against animals and recovers, with a one-step retreat
out of a doorway if the pursuer is far enough away. Targets fast bat and
jackal attrition, unlike the earlier failed pet/Elbereth/stair escapes.
Restricts to enemies that cannot open/break/pass doors, checks actual map
connectivity, aborts on new threats, hunger or lost barrier. No seed or gender
conditions. Candidate copy: /tmp/tourist-doors.

## Held-out plan
Fresh randomly drawn block: 87366-87395, thirty seeds per identity (60 games).
The prior block 86547-86561 had a very large parent/training gap, so use thirty
per identity even though the prompt left its generalization field unexpanded.
Parent and frozen candidates use exactly the same block, evaluation-id local.
Held-out results are only yes/no validation; no trajectories will be examined.

## Training measurements
A (door shelter): all 30 seeds mean 0.362673954027, female 0.368434891723,
male 0.356913016332. Original six early losses unchanged. Reject. Door-based
recovery altered surviving games adversely; no usable barrier in original losses.

## Candidate B: direct homeward stairs
Source: Tourist early-game survival, Trap_door, and the top Valkyrie direct stair
routing. Complete FALL_HOME's intent by taking known reachable stairs directly
and removing the outer HP-recovery exploration detour while homebound. Targets
the accidental early falls preceding the bat/jackal losses.

## Candidate C: purchase armor
Source: Tourist early-game advice to exploit starting wealth for equipment,
Armor_class and Shop wiki pages. Current shopping buys food only. Buy affordable
recognized armor upgrades before diving, retaining a food reserve and avoiding
known cursed items, unwanted magic boots, and excess carrying weight. Targets
the low-AC melee attrition shared by bat, jackal and wererat deaths.

B early subset: mean 0.171321235411; seed 1 in each gender improves from
0.017539535799 to 0.466376315653 (depth25); seeds0 and6 unchanged. Four
early losses remain among these six. Full training and held-out pending.
C is prepared but untested; if B validates, prefer its smaller single change.

B full training: overall 0.407028848865, female 0.425863934192, male
0.388193763539. Six early losses remain: saved seed1 (both), but seed5
(both) now dies to a bolt of fire on depth2. Overall +0.002568, male -0.025710:
not a convincing all-round win. Testing a narrower version B2 that disables
only the outer HP-recovery exploration while homebound, retaining normal
inventory handling during travel. No held-out outcomes have been read.

B2 ablation: disabling only the outer HP-recovery exploration leaves all six
original early seed results exactly unchanged (mean 0.021708975459). It does
not explain B's rescued jackal losses. Do not promote. B3 tests direct stairs
only, retaining the original outer HP-recovery exploration; full30 underway.

B3 direct travel only: all30 mean 0.403298472973, female 0.408045170598,
male 0.398551775347. Early losses 4/30, but overall falls below parent.
Reject. The routing idea saves jackal losses but changes surviving paths adversely.
Lost preparation was a hypothesis, not a traced cause; B4 local pickup later
failed to repair the seed5 regression. C (armor purchases) is now evaluated
on all30; its code was prepared from the role research before B's results.

C full training: overall 0.414062042207, female 0.398164852942, male
0.429959231471. Both identities improve; mean gain 0.009601552765. Original
six early losses remain unchanged. Keep frozen for held-out yes/no validation.
B4 is a final routing variant: direct homebound travel still permits pickup
and equipment changes on the current square, but no remote item-gathering
excursions or altar detours. It retains normal recovery priorities. This tests
whether removing all item handling unnecessarily harmed preparation in B3.

B4 full training: overall 0.404885027676, female 0.401724884754, male
0.408045170598; early losses4/30. The +0.000425 average gain is too small
to be compelling, and local pickup did not fix the seed5 regression.
All strategy code is frozen before held-out evaluation. Parent and armor
purchases will be measured on all60 held-out pairs; no held-out trajectories
will be inspected for tuning.

Door prototype limitation found in code review: after closing a door it
requires `not agent._hurt_recently(2)` to continue its stored recovery. Damage
from before closure can therefore cancel recovery immediately. This was not
fixed or measured; the failure of A does not establish that a correctly
implemented door shelter is useless. A future attempt should distinguish new
damage through the barrier from old damage that prompted the retreat.

Held-out first half (87366-87380, 15 per identity): parent and C each
0.208855871767 overall and for each identity, no errors. This is a score tie,
not evidence of a held-out gain. The planned second half continues without
any code changes. The large training/held-out gap supports using the full
thirty seeds per identity.

## Full held-out decision
Parent and C each score 0.148848134509 overall, female and male, on
87366-87395 (60 pairs, thirty per identity). Both have38/60 early losses
(19 per identity). No errors. C passes the no-regression bar but shows no
held-out gain. Training C: 0.414062042207 vs parent0.404460489442 (+0.00960155),
just below the 0.4145 stretch target, and both training identities improve.
No code was tuned using held-out results. A truncated training-only diagnostic
of seed10 female and seed11 male (30,000 steps, below their known terminal
step counts) is used only to check purchase-path activity, not to revalidate
any deterministic scores.

Promotion: the frozen C files were copied into /workspace only after the full
sixty-game held-out comparison passed. Source diff against /refs/parent is
limited to inventory.buy_armor and its global scheduling call. Compilation
and make_agent construction/close passed; reset/act remain callable and
arena_adapter.py is byte-identical to parent. No proven-neutral parent fixes
were found missing from the inherited code.

Final diagnostic limitation: neither truncated training trace logged an armor
purchase before its cutoff. These traces therefore do not confirm the causal
purchase path and were not used as repeated score measurements or for tuning.
The retained decision uses the completed standard-command training evaluation
and the full paired60-game held-out evaluation only. Rejected prototypes were
screened on training; their held-out runs were not completed in this iteration.
No later-stage switch was made.

Final retained change: C (affordable armor purchases before diving).
Training: female0.395017676506 -> 0.398164852942;
male0.413903302378 -> 0.429959231471; overall0.404460489442 -> 0.414062042207.
Held-out: all means0.148848134509 -> 0.148848134509.
Early losses: training6/30 -> 6/30; held-out38/60 -> 38/60.
