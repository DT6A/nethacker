# Early-survival research and experiments

## Loss split (before choosing the change)
The reference has 15 female rows, not the advertised 30. Early means maximum depth <=4, turns <=3000, or reported XP <=5. Four of 15 (26.7%) qualify: 0 bat (XL2, depth3, turn1644); 1 jackal (depth3, turn787); 6 hallucinated jackal (XL6, depth1, turn8807); 12 hill orc (XL7, depth1, turn22290). Their mean is 0.030916; the eleven survivors average 0.537348. Replacing their scores with the survivors' mean would add 0.135049 to the overall mean. The required focus is early survival. Male baseline seeds 0,1,6,12 were measured once and have identical losses.

## History read
/refs/history.md: minotaur wands lowered score; Castle crossing had mixed reported results; haste/camera iteration was discarded; summoning were allies produced a small recorded gain. Container-trap safety is already in the parent, so no absent proven-neutral carry-forward is listed. /refs/past_runs.md: repeated prayer, camera, early-diving and trap-disarm experiments failed or were marginal. This experiment instead changes weapon use.

## Other-character top programs
Read /refs/top/README.md and strategy additions/removals in all 31 other-character diffs. Several programs package multiple shared strategy trees; the same transferable mechanism is recorded for each. The highest leaders (Valkyrie 1c4099e80253 and Archeologist d44c89c2ffd8) were included.

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

## Online sources read
1. https://nethackwiki.com/wiki/Tourist — early darts bridge to a better melee weapon; unskilled weapons have -4 accuracy, low HP and poor armor make trading blows dangerous. Disregarded the explicitly marked 3.7 camera XP features.
2. https://nethackwiki.com/wiki/Bat — fast early attacker; escaping by walking is unreliable.
3. https://nethackwiki.com/wiki/Jackal — packs threaten starting characters; use darts and avoid surrounding melee.
4. https://nethackwiki.com/wiki/Floating_eye — passive paralysis can make the eventual killer appear to be a weak monster.
5. https://nethackwiki.com/wiki/Dart — throwing, enchantment, training and breakage.
6. https://nethackwiki.com/wiki/Talk:Tourist — player discussion “Miss Miss Miss Miss Miss”; low dexterity and weapon skill explain poor melee accuracy; collect/train daggers.
7. https://nethackwiki.com/wiki/Talk:Throw — players discuss training weapon skill through successful thrown hits.
8. https://nethackwiki.com/wiki/Talk:Floating_eye — player discussion of long paralysis and preventing sight of the eye.
9. https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/dothrow.c — thitmonst: +(3-distance) to-hit, +2 for throwing weapons, skill bonus; confirms point-blank throwing is valid in 3.6.6.
10. https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/weapon.c — exact skill bonuses.
11. https://raw.githubusercontent.com/maciej-sypetkowski/autoascend/master/README.md — bot architecture and combat strategy integration.

Google/reddit/Google Groups/StackExchange lookups were also attempted, but returned challenges, 403 or 429. The three wiki Talk pages above are actual player discussions, not reference articles; they were successfully fetched and read.

## Selected hypothesis
The Tourist guide's trained-dart advice plus the peer's point-blank shooting mechanism should prevent early bat/jackal deaths by replacing weak, inaccurate melee with dart throws, until a useful melee weapon is available. Preserve existing pet, peaceful, shop and Elbereth guards.

## Implementation finding
The initial priority-only variant left seeds 0 and 1 byte-for-byte unchanged, and reduced seed 6's score. Inspection showed get_ranged_combinations excludes both the best melee weapon and the wielded weapon. The melee scorer can choose the Tourist's darts, so the entire starting stack is then unavailable for throwing. The revised variant permits a non-welded dart stack with more than one dart to remain ammunition, and raises its close-combat priority while the bot lacks a trained or high-damage melee weapon. This is one complete dart-use change, not a separate strategy.

Early-seed test of the complete dart change: female [0,1,6,12] scores [0.408323,0.029070,0.036888,0.125585]; male [0.408323,0.029070,0.036888,0.050758]. Female seed 12 reaches depth 10; male seed 12 remains on depth 1. All four original male early-loss rows were measured, not assumed from female results. Full validation was completed and rejected; see the complete-results table below.

Complete baseline (female supplied, male measured once): female 0.4022995155, male 0.3802407802, pooled 0.3912701478. Eight early losses out of thirty. The acceptance target remains strictly above the user-specified 0.4029, preferably 0.4129, regardless of this lower pooled baseline.

### Additional player discussion sources (successful, outside the wiki)
Fetched via the public Stack Exchange API, including answers:
- https://gaming.stackexchange.com/questions/18905/making-your-actions-properly-repeatable — player died to a giant bat after accidentally meleeing a floating eye; answers explain single-turn multishot and protecting peaceful creatures behind targets.
- https://gaming.stackexchange.com/questions/134068/how-to-find-out-which-weapon-is-better — players explain why skill and target size matter when comparing weapons, and why training useful weapon families matters.
- https://gaming.stackexchange.com/questions/95633/when-should-i-start-twoweaponing — train the main weapon before switching modes; armor and skill readiness matter.

### Failed broad dart variant
All 30 games measured once: female 0.1103253900, male 0.1053368834, overall 0.1078311367, 17 early losses. Although original early seed 0 was rescued, many previously successful level-one grinds collapsed. Never copied into /workspace.

### Proven weapon-model bug, exploratory correction
NetHack 3.6.6 weapon.c weapon_dam_bonus returns -2 at Unskilled/Restricted; character.py uses +2. Correcting the sign alone on female [0,1,6,12,2,7] keeps 0,1,2 scores but lowers 6 (0.036888 to 0.024234), 12 (0.050758 to 0.024234), and 7 (0.646505 to 0.125585). Further investigation required before deciding whether to retain it.

The damage-only correction's first logged divergences occur after shared events at turn 4000 (seed 6), turn 4164 (seed 12), and turn 4000 (seed 7), all XL3-4. The old model's inflated unskilled damage favors taking/training real melee weapons over retaining improvised darts. Follow-up 1 preserves the correct -2 penalty, but explicitly values Basic-skill potential only with high HP and no hostile other than weak monsters; follow-up 2 will account for enemy AC in weapon hit probability.

Damage correction follow-ups on female seeds [6,12,7,0,1,2]:
- Safe training of unskilled melee weapons: [0.024234,0.021185,0.117033,0.018478,0.017540,0.379002], worse than parent.
- Defender AC included in melee choice: [0.024234,0.024234,0.125585,0.018478,0.017540,0.466376], same scores as sign-only on the sample, still worse than parent.
Neither is being retained. The correction is proven but NOT neutral.

Diagnostic replay (partial only, not another score measurement) ran the parent's decisions with a shadow corrected scorer. First concrete divergent choices:
- seed 6, turn 4075, XL4: old selects crude dagger; corrected selects 28 +2 darts.
- seed 12, turn 4314, XL4: old selects dagger; corrected retains +2 darts.
The accidental benefit is stronger than training alone: switching to a dagger makes the dart stack eligible for ranged combat, because the bot excludes the best melee weapon from ammunition. The corrected scorer keeps wielding the darts and thereby disables their throwing. A third follow-up will keep the correct damage rule and explicitly allow dart stacks as ammunition, without the failed broad close-range priority boost.

Third damage-model follow-up (correct penalty plus dart-stack eligibility, no close-combat priority boost) also failed the same sample: seeds [6,12,7,0,1,2] scored [0.029070,0.036888,0.021185,0.024234,0.020797,0.466376]. The incorrect +2 rule is therefore left in place after three substantive follow-ups; its accidental benefits were dagger training and releasing wielded darts for ranged use. None of these were proven neutral.

Selective dart variant full evaluation: female 0.3076790888, male 0.2743039445, overall 0.2909915166; early losses 13/30. Rejected.

Proactive human-lycanthrope camera sample: original seeds 0 and 1 unchanged, female 6 fell to 0.029070, female 12 stayed 0.050758, male 6 fell to 0.029070, male 12 rose to 0.074546. Rejected as an early-survival rescue.

Trap recheck idea: /refs/past_runs/20260929-112307/21.diff only checked get_visible_monsters at the beginning of untrap_traps, before go_to. It did not fix the targeted arrow-trap/jackal death. Recheck both hostiles and HP immediately before each actual untrap after approaching the trap. Sources read: https://nethackwiki.com/wiki/Untrap, https://nethackwiki.com/wiki/Arrow_trap, NetHack-3.6.6 src/trap.c untrap_prob and try_disarm (1/3 success; most failures enter the trap).


## Further early-survival experiments
All variants stayed in /tmp; none was promoted until full validation.
- Full peer PrayerModel from /refs/top/44f826234d72: female [0,1,6,12,2,7] approximately [.029,.075,.098,.075,.024,.126], rejected. Tracking timeout/anger accurately did not preserve the productive long grind in the controls.
- Initial prayer only: true HP trouble plus initial major-trouble timeout; same female sample approximately [.029,.075,.029,.037,.024,.126], rejected.
- No missile melee: same sample [.029,.292,.024,.051,.051,.021], rejected.
- Recheck hostiles immediately before disarming: delayed seed 1 death, scores unchanged on tested original early seeds; rejected.
- Skip arrow/dart trap disarming: six-sample scores unchanged; eight additional female games gained .047 on seed 5 but lost .193 on seed 11. Seed 1 avoided its trap-triggered jackal death but later died to a bat. Rejected.
- Were allies proactively when no nearby pet: six-sample seed 6 fell to .029, seed 7 to .126; rejected.
- Remove the lone weak-monster recovery exemption for fast monsters: no substantial early rescue; seed 2 entered a pre-existing turn-inactivity recovery loop, which was terminated and recorded as bot_error. Rejected without rerunning.
- Emergency dart throws only against nearby fast monsters at low HP: six-sample controls unchanged, no original early loss rescued; rejected.
- Classify lycanthropes as dangerous: sample seed 12 improved .050758 -> .554359 female, .425841 male; seed 6 fell .036888 -> .029107 both. Full validation was completed and rejected; see the complete-results table below.

## Lycanthrope candidate rationale (subsequently rejected)
Source: https://nethackwiki.com/wiki/Werejackal (regeneration, pack summoning, infection; avoid animal-form melee), Tourist strategy, and /refs/top/c49b46fdffa0 proactive disabling. The existing danger predicate omitted all lycanthropes, so combat undervalued wands and stayed near them at HP levels it already considers unsafe against dangerous foes. Include wererat/werejackal/werewolf in the shared danger predicate; this updates existing wand, movement and defensive-engraving decisions as one coherent threat-classification change. It targets the original pack-associated early losses (6 and 12); no seed/turn identity checks.


## Complete 30-game results

| Variant | Female | Male | Overall | Early losses |
|---|---:|---:|---:|---:|
| baseline-all | 0.402300 | 0.380241 | 0.391270 | 8/30 |
| dart-usable-all | 0.110325 | 0.105337 | 0.107831 | 17/30 |
| dart-danger-all | 0.307679 | 0.274304 | 0.290992 | 13/30 |
| lycan-danger-all | 0.375382 | 0.376232 | 0.375807 | 8/30 |

No switch to mid/late-game work was made. The two dart trials are variants of the same idea, not two distinct qualifying attempts.

### Lycanthrope ablations
- lycan-distance: 6=0.02911, 12=0.07454, 9=0.03689, 8=0.36549, 11=0.60156, 5=0.60156. Rejected.
- lycan-disable: 6=0.03689, 12=0.05076, 9=0.55436, 8=0.36549, 11=0.40832, 5=0.60156. Rejected.
- lycan-ward: 6=0.02911, 12=0.07454, 9=0.55436, 8=0.36549, 11=0.40832, 5=0.60156. Rejected.
- dart-lycan: 6=0.03689, 12=0.05076, 9=0.12559, 8=0.36549, 11=0.40832, 5=0.60156. Rejected.
- dart-pack: 0=0.03689, 1=0.01754, 6=0.02911, 12=0.02911, 2=0.12559, 7=0.64650, 9=0.07454, 5=0.07454. Rejected.

Version check: NetHack 3.6.6 src/mhitu.c mattacku() invokes were_summon while adjacent; src/were.c were_summon() includes both PM_HUMAN_WERE* and PM_WERE* cases. Both forms can summon in this version. This corrects the modern wiki strategy sentence claiming only animal forms summon.

### Availability-only final trial
Wielded dart stacks exposed to the unchanged ranged policy: 0=0.05076, 1=0.02081, 6=0.02648, 12=0.03689, 2=0.05076, 7=0.02122. Rejected.


## Final disposition
No winning strategy change was found. /workspace/autoascend remains identical to /refs/parent/autoascend. Measured pooled baseline remains 0.3912701478; early losses remain 8/30 (4/15 for each gender). The supplied female baseline is 0.4022995155; measured male baseline is 0.3802407802. No candidate met the user-specified 0.4029 acceptance threshold. No new proven-neutral fix was established, and no absent carry-forward neutral fix was found in this run's history.

The proven weapon damage-sign correction was not neutral. NetHack 3.6.6 weapon.c weapon_dam_bonus() gives -2 damage for Restricted/Unskilled; parent character.py incorrectly gives +2. After three substantive follow-ups it remained worse. The wrong bonus accidentally promotes acquiring/training a dagger and makes the starting darts eligible for throwing (the ammunition filter excludes the selected melee weapon). Preserving those useful effects explicitly through safe-training valuation, defender-AC valuation, and dart availability did not recover the sample's lost score. This correction is therefore documented for later work, not silently retained in a worse program.

All score measurements used evaluation-id local. No deterministic seed/program score was repeated. The partial weapon-selection diagnostic inspected behavior; the fast-defense inactivity loop was terminated and recorded as bot_error rather than treated as a successful result. All strategy experiments remained isolated under /tmp.
