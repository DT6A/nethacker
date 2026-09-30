NetHack research: Castle arrival and crossing

History: /refs/history.md records one previous iteration, premature minotaur
wand use, 0.3722 versus 0.4023. It changed fights before the Castle and lost
large amounts of progression on seeds 8 and 11. The final Castle policy does not repeat it; it is gated by observed Castle terrain.
/refs/past_runs.md also records unsuccessful Castle passage enablement,
Elbereth-combat overrides, and several camera policies; none is adopted here.

Parent outcomes: the supplied JSON has 15 male rows, not the advertised 30.
Minotaur is the leading cause (four games). The deepest milestone is Dlvl:29.
Four runs end early (bat, jackal, distorted jackal, hill orc); rescuing an early
run is potentially much more valuable than prolonging a Castle fight.

All other-character leaders: inspected all 15 .diff files. Several are
portfolio wrappers whose diffs omit the nested packages; inspected their
selected packages too. Concrete mechanisms absent from the parent:

- 0875c3519bed, elf Ranger leader (0.461): pf_s25p8/dive_logic.py retains
  control through consecutive escape actions and immediately breaks eel wraps.
- 1c17ee5b7216, Samurai/Ranger leader: pf_v37/dive_logic.py engraves before
  walking to a safe digging square and handles eel wraps before other escapes.
- 1c4099e80253, dwarf Valkyrie leader (0.526): castle_power.py identifies
  unknown wands on arrival and uses polymorph forms to cross the moat;
  castle_logic.py can retreat from a monster-blocked moat channel.
- 429cf0108271, chaotic Wizard leader: castle_logic.py backs out of a blocked
  moat channel and tries the opposite side, up to four attempts.
- 44f826234d72, neutral Wizard leader: fight_heur.py's ranger_point_blank
  lets an already-wielded bow beat a melee weapon swap when an enemy is adjacent.
  This suggested the dart-priority draft, which was tested and removed.
- 47a6c840a4cf, gnome Ranger/human Rogue leader: castle_logic.py records which
  moat channel has sea monsters and changes sides when its route is blocked.
- 5088ac9a49a3, orc Rogue leader: castle_logic.py probes a moat corner from
  dry ground and switches channels when sea monsters block progress.
- 51a41284fa08, human Ranger leader: castle_logic.py retries the opposite
  moat channel instead of remaining against a sea monster.
- 725cafa6a87d, human Valkyrie leader (0.465): pf_v38/dive_logic.py prioritizes
  escaping an eel's wrap before ordinary digging or combat.
- 81ea959c3b98, lawful Priest leader: castle_logic.py probes the relevant
  north/south corner and backs out of a blocked moat channel.
- 985b175cae53, elf Wizard leader: castle_logic.py uses the same dry-corner
  probing and bounded moat-channel retreat.
- ae053ca704ff, neutral Priest leader: pf_kef_d42161f/dive_logic.py has the
  uninterrupted digging-escape/eel-release sequence absent from the parent.
- d44c89c2ffd8, Ranger/Wizard leader: pf_base/dive_logic.py rechecks the
  engraving after sight returns before spending a turn engraving again.
- f362a746154d, Priest/Ranger/Valkyrie leader: castle_logic.py records recent
  sea-monster sightings to choose the other moat channel.
- 41c961256c41, chaotic male Wizard leader: its active autoascend strategy is
  identical to the parent (agent.py comparison confirms this); the only new
  hypothesis is the wholesale adoption of this parent's Tourist strategy.
  There is no absent active mechanism to claim for this exception.

Online reading (successful HTTP fetches):
https://nethackwiki.com/wiki/Tourist
https://nethackwiki.com/wiki/Minotaur
https://nethackwiki.com/wiki/Castle
https://nethackwiki.com/wiki/Standard_strategy
https://nethackwiki.com/wiki/Scroll_of_scare_monster
https://nethackwiki.com/wiki/Wand_of_teleportation
https://nethackwiki.com/wiki/Expensive_camera
https://nethackwiki.com/wiki/Dart
https://nethackwiki.com/wiki/Multishot
https://nethackwiki.com/wiki/Ranged_combat
https://nethackwiki.com/wiki/Skill
https://nethackwiki.com/wiki/Scroll_of_magic_mapping

Reddit search for minotaur/Castle returned HTTP 403; not counted as a read.
The wiki contains 3.7/5.0 material, so checked 3.6.6 source directly:
https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/dothrow.c
https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/apply.c
https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/monmove.c

dothrow.c confirms the adjacent-distance hit bonus and the Tourist's Skilled
multishot exception for darts. Tourist advice recommends the starting +2 darts
as the bridge to a viable melee weapon and reserves melee training for weak
monsters. This informed a discarded draft, not the final Castle policy.

Final hypothesis: port the leading dwarf Valkyrie's integrated Castle arrival
and crossing policy, with terrain recognition by magic mapping before minotaurs
can prevent a diagnostic dig. Try the carried crossing kit on arrival, give
its escape precedence over ordinary combat, and use the direct moat launch or
a wall-walking polymorph form to reach a trap door.

Why this differs from earlier discarded CASTLE_PASSAGE toggles: those waited
for an unsuccessful floor dig and ran item preparation below combat, after
walking through the western maze. The reference castle_cross.py documents
47/61 arrivals dying before using an item; the new entry points act at arrival.
The first port sample also showed no Castle activation before death, motivating
the mapping survey rather than assuming every deep maze is the Castle.

Discarded drafts (fully removed from submitted strategy):
- Close-range dart priority: 30 games, mean 0.2272013261.
- Correcting the unskilled damage sign: 30 games, mean 0.1310890944.
  The mechanics are confirmed by the Skill wiki and NetHack 3.6.6 weapon.c,
  but the change regressed this bot's early-game weapon training and survival.
No deterministic seed-program result was rerun for confirmation.

Discarded integration refinement for the same Castle crossing policy:
- Accept equipped ring descriptions for polymorph anatomy, including foreclaws
  and scale gaps, as in the reference item manager.
- Prepare the dry path to the moat before an uncontrolled polymorph can drop
  the pick. Skip this preparation with identified polymorph control (xorn can
  pass through walls); bound attempts and fall back when the path is blocked.
  Real Castle logs showed a brown pudding stranded behind an undug rock, then
  the equipment parser asserting on a black naga hatchling's ring.
  The refinement reached the moat launch in both seed-7 games, but a shark
  killed both characters; their progression scores were unchanged. Its full
  30-game mean was 0.3705310699, with female seed 8 falling from 0.6015648510
  to 0.3654881095. Both refinement edits were reverted; their individual
  effects were not isolated. The submitted policy is the earlier fully
  evaluated version, with its known polymorph crossing limitations.

Selected policy validation (30 distinct games, local namespace, seeds 0–14):
- Overall: 0.3784002946, +0.0061002946 over the stated 0.3723 keep threshold.
- tou-hum-neu-fem: 0.3862695193.
- tou-hum-neu-mal: 0.3705310699.
- Misses the 0.3823 target by 0.0038997054. The male mean is lower than the
  supplied male-only parent reference; no per-identity improvement is claimed.
- Raw results: castle-eval.json; summary and submitted strategy hashes:
  castle-eval-summary.json. These combine castle-survey-eval.json (seeds
  7, 9, 11, 14) and castle-final-rest.json (all remaining seeds).
- Imports, initial inactive Castle state, configuration attribute references,
  wall-walking route adjacency/bounds, and git diff --check passed. The bot
  factory retains its reset/act contract. arena_adapter.py is unchanged.
- No identical seed/program pair was evaluated twice. Reverting the rejected
  refinement restores the selected evaluated program; it was not reevaluated.
