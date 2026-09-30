# Research for proactive minotaur defence

Read `/refs/CONTEXT.md`, `/refs/history.md` (no earlier iterations), `/refs/top/README.md`, all 26 other-character program diffs, relevant implementation excerpts, and `/refs/past_runs.md`. Several reference diffs are truncated and/or mostly contain renamed portfolio packages; inspected their underlying strategy files as well. The two Tourist leaders are identical to the parent.

## Peer mechanisms absent or disabled in the parent

| Program | Concrete mechanism |
| --- | --- |
| `0716a5964bc4` | Mines squeeze detection caps inventory at 580 so a found pick can leave the branch. |
| `1c17ee5b7216` | Portfolio includes a moving grind: XL5–6 on Dlvl3, XL7 on Dlvl2. |
| `1c4099e80253` | BREACH_MINO selects sleep/death/teleport/polymorph against minotaurs before critical HP. |
| `41c961256c41` | Bounded quiet recovery tracks actual healing and backs off when resting makes no progress. |
| `429cf0108271` | Deep defensive polymorph supplies a fresh HP pool and sometimes a moat-crossing form. |
| `47a6c840a4cf` | Scare-scroll hold loops prevent a lower-priority action from stepping off protection. |
| `5088ac9a49a3` | Landing guard treats big melee threats separately from ranged lich threats. |
| `51a41284fa08` | Dropped scare-scroll protection supports resting and digging without engraving erosion. |
| `6ecc35e91af2` | Digging-tool carriers begin descent at XL7 rather than extending the grind. |
| `725cafa6a87d` | Portfolio includes XL-dependent grind depth to reduce the number of hunger prayers. |
| `7c1ec61015bf` | Astra quiet recovery and pit/boulder escape handle hazards outside ordinary combat. |
| `81ea959c3b98` | Deep defensive polymorph is available before an otherwise fatal melee exchange. |
| `985b175cae53` | Landing guard selects known healing potions and decisive wands on dangerous arrivals. |
| `ae053ca704ff` | Portfolio contains the multi-depth grind policy, absent from the parent configuration. |
| `ae17b4a50322` | Portfolio contains the XL5/Dlvl3, XL7/Dlvl2 grind policy. |
| `b4c2edc23ce3` | Scare-scroll holding remains active through repeated strategy-preemption cycles. |
| `bded98c686e3` | Portfolio has the multi-depth grind policy and specialised priest routes. |
| `c49b46fdffa0` | Astra proactive sleep and quiet recovery support frail Healers. |
| `c526d8d41f20` | Mines squeeze handling frees paths blocked by the inventory weight limit. |
| `c718d0f2c2fd` | Portfolio adjusts grind depth by XL instead of farming Dlvl1 throughout. |
| `d44c89c2ffd8` | Portfolio includes grind-depth scheduling rather than the parent’s empty GRIND_LEVELS. |
| `d4eab8c5a4f0` | Healer portfolio includes proactive sleep/quiet recovery and multi-depth grinding. |
| `d4f9cab6e621` | Proactive sleep disables approaching threats before healing becomes urgent. |
| `e9c44042710b` | Mines tool retrieval uses a squeeze-aware inventory cap and direct return routing. |
| `f362a746154d` | Scare-scroll shelter works in Gehennom, where Elbereth does not. |
| `f5d169eb6076` | Healer portfolio adds proactive disabling of mobile threats. |

## Losses and online sources

The supplied parent-eval.json contains 15 male Tourist games, not the advertised 30. Mean 0.4022995. Minotaurs are the most common exact cause (4/15, at depths 25, 26, 28, 28); deepest milestone is Dlvl29. Four low-progress games end at XL2, Dlvl3, XL6 and XL7. Both genders must be tested explicitly.

Successfully fetched and read:

- https://nethackwiki.com/wiki/Tourist
- https://nethackwiki.com/wiki/Minotaur
- https://nethackwiki.com/wiki/Scroll_of_scare_monster
- https://nethackwiki.com/wiki/Castle
- https://nethackwiki.com/wiki/Expensive_camera
- https://nethackwiki.com/wiki/Standard_strategy
- https://nethackwiki.com/wiki/Wand_of_teleportation
- https://nethackwiki.com/wiki/Wand_of_sleep
- https://nethackwiki.com/wiki/Wand_of_slow_monster
- https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/zap.c
- https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/uhitm.c

Reddit search was attempted but returned HTTP 403. No claim relies on it. Wiki sections marked upcoming 3.7 were excluded. Checked the relevant wand and camera effects against the 3.6.6 source.

Chosen hypothesis: use carried disabling magic against approaching minotaurs, from the Minotaur wiki strategy and the Valkyrie leader’s BREACH_MINO. Parent combat explicitly excludes sleep and non-ray wands; minotaurs also receive only ordinary target priority.

Prior Tourist experiments already tried prayer changes, broad corpse collection, Castle enablement, digging changes and adjacent camera heuristics. This iteration does not repeat those changes.


## Implementation screening

All candidates below were separate programs; no identical seed/program pair
was evaluated twice. Rejected candidates were fully reverted.

- A known-disabling-wand policy never activated on either gender's seeds
  2, 10, 11, 14. These runs did not establish a benefit.
- Proactive ranged camera use was tested and refined to avoid repeatedly
  flashing already-blind monsters. Its final 15-male mean was 0.3705051,
  below the keep threshold. Seven female games matched their male counterparts.
- Blinding floating eyes before melee regressed a six-game sample.
  Additional source: https://nethackwiki.com/wiki/Floating_eye.
- Bounded quiet recovery from the Healer references regressed the sample.
- Enabling the existing HOLD_LOOP scheduler continuation also regressed the
  sample. Additional source: https://nethackwiki.com/wiki/Elbereth.

## Current candidate

The remaining strategy change returns to the recorded main killer: minotaurs.
It adapts the Valkyrie leader's BREACH_MINO selection to use promising ambiguous
wands as well as known ones, before critical HP. The initial known-wand version
failed to activate because the carried wands were unidentified. This version
can use those resources, using their possible identities to reject harmful
choices and preferring potentially decisive effects.

The hook runs before digging when a visible minotaur is within eight squares
on a clear horizontal, vertical or diagonal line. Existing
emergency and retreat layers retain higher priority. It avoids impaired aiming,
known-empty wands, already-tried unidentified wands, paths hitting pets or
peaceful creatures, and
known ray rebounds into the hero. A cooldown prevents spending successive
turns testing wands. The action uses only observable game state.

The adjacent-only version scored 0.3736782 on all 15 male seeds; five female
games matched their male counterparts. It produced two actual uses (seeds 2
and 10), without a score increase in those games. The final version adds the
reference’s ranged targeting and permits reuse of known useful wands. Eleven
focused checks cover eligibility, impaired aiming, blocked and misaligned
paths, friendly fire, ray rebounds, and known versus unidentified wand reuse.
The final four-game targeted sample matched the adjacent-only version.
The supplied parent has no female results, so a paired 30-game comparison is
not available.

## Final measurement

All 30 final-program games (seeds 0–14 for both identities, evaluation ID
`local`) completed successfully. Every seed/program pair was evaluated once.
Results are in `minotaur-eval.json`; the means and strategy-file hashes are in
`minotaur-eval-summary.json`.

| Identity | Games | Mean |
| --- | ---: | ---: |
| tou-hum-neu-fem | 15 | 0.3736782463 |
| tou-hum-neu-mal | 15 | 0.3736782463 |
| Overall | 30 | 0.3736782463 |

This exceeds the stated 0.3706 keep threshold by 0.0030782463, but misses the
0.3806 target. It is not evidence of a 0.01 improvement. The male mean is
0.0286212691 below the supplied male parent mean (0.4022995155); no female
parent rows were supplied, so a full paired parent comparison is unavailable.
The observed wand uses did not increase the reached milestone on those seeds.
The ranged extension did not improve the targeted four-game sample.

Validation: Python compilation, entry-point import, eleven focused wand-policy
checks, clean diff formatting, and 30 completed arena games. The adapter and
entry-point contract are unchanged. Only the minotaur strategy and its
preemption hook remain as code changes.
