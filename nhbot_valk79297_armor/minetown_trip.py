"""MINETOWN_TRIP: a stairs trip to Minetown's temple at the start of the dive.

# hypothesis: the grind hands over to the dig-dive at XL 7-8 without ever seeing the Gnomish Mines (parent: Minetown
# reached and used in 0% of games). Minetown (Mines level 3 or 4) has the one guaranteed temple of the early game:
# every carried item of unknown BUC dropped on its altar shows its curse status (black flash = cursed, amber =
# blessed, none = uncursed), and its priest sells 2-4 points of permanent AC for 400*XL (below 600*XL) gold. So the
# planned dive (never a rescue) first walks there: the Mines branch on Dlvl 2-4, down the Mines by the stairs
# (fighting what comes instead of the dive's dig-away reflex, resting below 80% HP), the town recognised by its
# doors / altar / fountains / people, the altar found, every unknown item dropped on it and taken back and the best
# uncursed armor put on, a donation when the gold is there, then back up the known stairs to the main dungeon, where
# the dive proper starts once the prayer timeout allows (DIVE_PRAYER_GAP again). What the measured games needed on
# top of the route:
#   - trap doors drop 1-3 levels, so Mines 3 and 4 are judged (town / filler) by their middle band and a fall past
#     the town is climbed back from (_judge, _look_for_town, _climb);
#   - a '>' / '<' that stays out of reach: an inventory over 600 cannot squeeze through the Mines' diagonal gaps
#     (dropped to 550 where a squeeze opens the level) and known traps are walls to the BFS (unblock);
#   - a fight being lost above the town (half HP or less, a hostile adjacent) is dug away from (escape_dig_due) --
#     the only digging the trip does;
#   - Orcish Town (1 of the 7 town maps: walled in behind iron bars, 5-15 orc-captains and Uruk-hai inside, no
#     priest) is recognised by its bars and left alone;
#   - budgets per phase (branch, level, town, total) and an immediate end on a failed prayer: the trip never strands
#     the game, and a trip that ended early still tests on the altar when the way back passes it (passing).
# Ideas tried and combined. Measured on 109 games against the parent on the same seeds (0-14, 386141-386150,
# 67278-67301, 5025-5054, 23095-23124; the last two blocks were drawn as held-out seeds and became development
# seeds once their games were read): games that used the temple / mean progress / games ending on level <= 4
# (parent: 0% / 0.457 / 8%).
#   1. the trip as tour milestones (AutoAscend's FIND_MINETOWN; seeds 0-8 only): 33% / 0.29 -- dropped;
#   2. the trip as a dive task with the dig reflex off, budgets, fall handling, the Orcish Town skip, the escape hole,
#      unblock and the post-trip prayer hold: kept (25 seeds: 56% -> 80% as the pieces came in);
#   3. STUN_TOWN_GUARD, UNICORN_AVOID, ALTAR_NO_PRAY (agent.py; each from a death in or near the town): kept;
#   4. a pick-axe hole whenever the '>' stays cut off for 600 turns (79 games): 75% / 0.424 -- dropped for 5.: the
#      hole lands away from the level's '<', the way back took 500+ turns instead of ~120 and 5 games died on it;
#   5. stairs only, with 6. and 7. (this version): 59% / 0.424 / 17%;
#   6. an earlier Elbereth against a pack (crowd_alert) and 7. no peaceful dwarf hunted during the trip (prayers
#      stay available): kept as rules, no measurable change on their own (61% / 0.425 and 59% / 0.424);
#   8. dropped without a gain on 25-109 games each: the dwarves' piles looked through for armor, an explorer
#      without item gathering (trips 25% shorter, not safer), the pack held at 550 for the whole stay, the trip of
#      a tool-less dive delayed until it has a pick-axe (59% / 0.428 / 17%).
# What is left: about 1 game in 10 dies on the trip (the Mines' packs, mumakil, wands, out-of-depth mind flayers --
# the wiki's "minesflayers"), which takes the games ending on level <= 4 from 8% to 17%; Orcish Town (9% of games)
# and a '>' not found within the level budget (10%) are the trips that end without the temple.
# sources: read for this change -- https://nethackwiki.com/wiki/Minetown (Mines level 3-4; Orcish Town: iron bars,
# "you must dig through the walls or break the iron bars", 5-15 orc-captains / Uruk-hai inside, no priest, an
# unaligned altar; what angers the Watch) ; https://nethackwiki.com/wiki/Gnomish_Mines ("you tend to get swarmed as
# you enter each new level", retreat upstairs and Elbereth, 6 random traps per filler level, minesflayers) ;
# https://nethackwiki.com/wiki/Altar (a dropped item: black flash = cursed, amber = blessed, none = uncursed) ;
# https://nethackwiki.com/wiki/Unicorn ; https://nethackwiki.com/wiki/Stun ; https://nethackwiki.com/wiki/Prayer ;
# player discussions: https://nethackwiki.com/wiki/Forum:Have_a_good_strategy_for_descension%3F (Minetown at XL 4-5
# with ~50 HP and AC 0 for the altar's curse test and the shops; "don't be afraid to run away and heal"; trap doors
# near Minetown drop several levels) and https://groups.google.com/g/rec.games.roguelike.nethack/c/ugsH00JMaqw
# ("Lets face it: it's the Altar": curse-testing "works with any altar"; buy the priest's base protection first);
# NetHack 3.6.6 dat/mines.des and dat/dungeon.def as shipped with NLE (minetn-1..7: Orcish Town's bars and orc army,
# where the altars and stairs are; the fillers have no doors, altars or fountains; RNDLEVEL "minetn" @ (3, 2));
# reference run 20261102-161819 #918/#833 (buy_protection: the #chat + offer keys, the 400*XL..600*XL tier and the
# priest's "Thou hast been rewarded for thy devotion" as quoted there from priest.c) and #862 (town recognition
# without a shopkeeper); past run 20261106-211643 #85/#116 (a trip held before the first dive; the altar as its
# exit condition); this engine's own agent.unsqueeze (no diagonal squeeze with more than 600 carried).
#
# ---- third iteration: THE ALTAR SHOWS ITS FLASH, THE PICK-AXE MAKES THE WAY BACK (ALTAR_FLASH, PICK_TUNNEL) ----
# Where the parent's trips ended, on 139 fresh games (79 development, 60 held-out): the temple used with a flash
# in 54%; no trip at all in 15% (dead in the grind, or a rescue dive); the level budget 13%; Orcish Town 6%; an
# altar test that showed no flash 4%; dead in the Mines 5%; no Mines branch found 4%. Ideas tried, each measured
# against the parent on the same seeds (est = progress x the run's multiplier rebuilt from XL, AC, the temple's
# flash, holes and starvation):
#   1. ALTAR_FLASH (_flash): an altar that stayed dark gets one object already known to be cursed or blessed, the
#      wielded Excalibur if nothing else -- kept: all 5 dark altars of the 79 development games flashed
#      (temple used 56% -> 63%), nothing else in those games changes before the altar;
#   2. PICK_TUNNEL on the way back (tunnel_up, _tunnel_step): walk-and-dig straight to the known '<' that the BFS
#      cannot reach, or to cut-off floor when no '<' is known -- kept: turns from the end of the trip to the main
#      dungeon -30% (development) and -36% (held-out);
#   3. the same tunnel on the way down plus a hole when the '>' stays cut off (DIG_AFTER_TURNS 1000) -- dropped: of
#      the 8 level-budget trips with a pick-axe 2 reached the temple and 4 died on Mines 2-4;
#   4. the way-down tunnel alone at 300 turns (TUNNEL_DOWN_AFTER) -- dropped: temple used 63% either way, raw
#      progress 0.419 -> 0.401 on the 79 development games.
# 1 + 2 together, parent -> this version: 79 development games (0-14, 386141-386150, 71000-71053): temple used
# 56% -> 63%, raw progress 0.407 -> 0.419, est 0.393 -> 0.411; held-out 78367-78426 (60 games, run once, read
# afterwards): temple used 52% -> 52%, raw 0.386 -> 0.392, est 0.378 -> 0.383. (About 5 games in 79 differ between
# two runs of the same program: some move of the dive is timed.)
# What is left for this stage: a trip that goes on from a stuck level dies as often as it arrives (3., 4.), so the
# 13% of level-budget trips need a stronger hero rather than a way through; Orcish Town has no priest (its temple
# is not "the temple"); no game came within half of the 400*XL gold for protection (median 3% of it).
"""
import heapq

import numpy as np
import nle.nethack as nh
from nle.nethack import actions as A

from . import jf_config, utils
from .character import Character
from .glyph import G, MON, Hunger
from .level import Level
from .strategy import Strategy

# ---- seventh iteration: THE TRIP COMES LOOSE FROM THE DIVE -- IT LEAVES FROM THE GRIND, AND IT IS MADE AGAIN ----
# (EARLY_TRIP, TRIP_RETRY; with ALTAR_GATHER, BRANCH_BOULDER and the fixes BRANCH_CLOCK_FIX, FRIDAY13_FIX)
# The hypothesis and its sources stand at dive_logic.DiveLogic._early_trip_due; this block has the numbers.
# Where the parent's games end, 187 of them replayed with logs (fresh blocks 22427-22480, 56070-56123,
# 11423-11476, the public seeds, the extra development seeds): the temple altar flashed in 116 (62%); dead in the
# grind before the trip 25 (13%); dead on the trip 18 (10%); alive with the trip over 27 (14%): Orcish Town 10,
# the Mines branch not found 10, a level budget 5, a dark altar 2. Of the 25 dead in the grind 12 had lost a
# hunger prayer (two of them on a Friday the 13th, see FRIDAY13_FIX) and 4 more died within 50 turns of a hunger
# prayer that had left them none for their HP: the grind lives on prayer (5-9 a game).
# Ideas tried, each against the parent on the same seeds (used = the altar flashed, counted from the game's own
# flash messages; raw = mean progress):
#   1. EARLY_TRIP at XL 7 + hand-back to the grind + TRIP_RETRY at the dive's start (dive_logic._early_trip_due,
#      _early_trip_handback, MinetownTrip.retry): 187 games: used 116 -> 115, raw 0.369 -> 0.378; dead before
#      the trip 25 -> 21, dead on it 18 -> 18. Alone it only moves the losses about -- kept as the frame for 2.
#   2. TRIP_RETRY for Orcish Town (orc_pending, orc_grind, the retry in DiveLogic.plan_step): a tool holder turned
#      away at XL 7 grinds on to XL 8 instead of diving and goes again; so does one who had just prayed; one whose
#      tool comes later in the Mines goes straight back. The 11 games of 1. that ended at the wall: 9 used the
#      altar, nobody died in the town (6 of 6 of the XL-7 tool holders). Kept.
#   3. ALTAR_GATHER (_gather_job): a dark altar gets the weapons and armor lying on the town level's squares the
#      hero has stood on. 5 dark altars looked at: 1 flashed (5 stacks fetched), 2 had nothing to fetch, 2 one
#      potion. Small, kept: it acts only at an altar that has answered nothing.
#   4. BRANCH_BOULDER (dive_logic._branch_boulder_push): boulders closing off unexplored ground are pushed before
#      a Dlvl 2-4 is written off. 16 trips that had ended without the branch: 2 found it. Small, kept.
#   5. EARLY_TRIP at XL 6 (54 games): used 28 -> 27, raw 0.372 -> 0.375: dead before the trip 10 -> 5, but the
#      XL 6 trips run out their level budgets (first-try success 46% against 65%) and stand before Orcish Town
#      unfit. Dropped for XL 7.
#   6. a hero fit for Orcish Town but for her prayer waits outside the wall for it (2 games): both waited, one
#      turned Weak in front of the wall and one ran out the town's budget inside; one died later. Dropped for
#      2.'s way (back to the grind, where the prayer comes back among weaker monsters).
#   7. no escape hole on the trip (the 18 parent trips that dug one): dead 7 -> 7, used 10 -> 9. Dropped (as in the
#      fourth iteration).
#   8. FRIDAY13_FIX on its 3 known games: the prayer is not said and nobody is smitten, but all three still die
#      on Dlvl 1-7 (0.024 -> 0.029, 0.048 -> 0.048, 0.024): the fix is right, the game stays lost. Kept as a rule
#      of the game; a real answer needs a food plan without prayer.
# Final version against the parent (1-4 and the two fixes; the rows marked * were run before 4. was added):
#   development: 22427-22480*: used 28 -> 33, raw 0.372 -> 0.381; 56070-56123*: 37 -> 37, 0.371 -> 0.387;
#     11423-11476* (drawn as held-out, read after an intermediate version lost there, 32 -> 27): 32 -> 34,
#     0.334 -> 0.339; public 0-14*: 12 -> 11, 0.499 -> 0.513 (the judge's parent run: 0.506); extra
#     386141-386150*: 7 -> 8, 0.330 -> 0.345. All 187: used 116 -> 123 (62% -> 66%), raw 0.369 -> 0.379.
#   held-out, each run once: 81588-81641*: used 36 -> 40, raw 0.411 -> 0.388; 84082-84135 (final code): used
#     26 -> 31, raw 0.329 -> 0.348; 71140-71193 (final code): used 36 -> 41, raw 0.360 -> 0.410. All three
#     (162 games): used 98 -> 112 (60% -> 69%), raw 0.367 -> 0.382.
#   Games ending on Dlvl 1-4: 82 -> 76 of 349. No game was aborted or errored in any run.
# What is left (the final version's 349 games; used 214 -> 235, 61% -> 67%): dead in the grind 11%, dead on the
# trip 9%, the Mines branch not found 6% (hidden for good: the wall search finds nothing in its 1700 turns), a
# level or town budget 3%, a dark altar 1%, Orcish Town 1% (AC above 3, or the breach ran out its 1500 turns).
#
# ---- sixth iteration: THE TRIPS THAT END ALIVE WITHOUT THE TEMPLE, AGAIN -- THE BREACH FROM XL 8, A SHORTER
# ---- BRANCH SEARCH ----
# hypothesis: (stage "use Minetown") of 130 parent games replayed with logs -- 45 fresh development games
# 5348-5392, the held-out blocks 63532-63561 and 59936-59965, the public seeds and the extra development seeds
# -- the temple altar was used in 74 (57%). Of the other 56, 19 heroes died before the trip and 9 on it; in 28
# the hero was alive and the trip simply ended: 12 on the 1500-turn level budget of a Mines filler level, 11 at
# Orcish Town's wall, 4 without the Mines branch, 1 on the town budget. The first two are what /refs/history #11
# built SECOND_WIND and ORCISH_ALTAR for (its notes follow below as the "fifth iteration"). It was discarded on
# the run's score, which is mean progress: both act only where the parent's trip was already over, so they move
# the stage's figure and not that one. They are combined here, re-measured on seeds #11 never saw, with one rule
# changed from what those games showed and one budget cut where the trip only loses heroes:
#   1. SECOND_WIND (unchanged): fired in 9 of the parent's 12 level-budget trips; 7 of the 9 went on to use the
#      temple and 2 found Orcish Town (one of them used its altar); nobody died on the added turns. The 3 trips
#      it left alone stood on a level that was not opening (reach 300 -> 300, 426 -> 448, 423 -> 432).
#   2. ORCISH_ALTAR, the breach only from XL 8 (ORC_MIN_XL 7 -> 8): in this iteration's runs 7 heroes breached
#      the wall at XL 8 and all 7 used the altar and left the town alive; 3 breached at XL 7, as #11's rule
#      allowed: 2 died inside (70 and 48 max HP, seven orcs with three orc-captains round the altar; an
#      orc-captain has two weapon attacks a turn) and 1 gave the wall up. An XL 7 hero leaves the town alone
#      again, as the parent does.
#   3. BRANCH_TURNS 3000 -> 1700 (new): the search for the Mines branch ends where it stops finding. In all the
#      runs of this iteration 230 trips reached the Mines, half of them within 100 turns of the trip's start, 95%
#      within 610, the slowest after 1532; of the 19 that searched on, none found it, and 2 of the parent's 6 such
#      heroes died in that tail (turns 2547 and 2583 of the search, on Dlvl 2-4 at XL 8-9, living on hunger
#      prayers). On the parent's 6 such games: 1 of the 2 deaths avoided (0.117 -> 0.554; the other
#      hero was held by her hunger past the new budget and died as before), the 4 others dive 1300 turns
#      earlier and are new draws (0.257 -> 0.647, 0.554 -> 0.161, 0.466 -> 0.445, 0.647 -> 0.647); temple use
#      unchanged, as expected. Also tried on those 6: DiveLogic.HIDDEN_SEARCH2 (the engine's switched-off search
#      "toward the void"): the branch found in 0 of 6, left off.
# Measured, parent -> this version, same seeds (used = an altar on the town level answered a drop; raw = mean
# progress; only the games whose trip the parent ended at Orcish Town, on a level budget or after more than
# 1700 turns of branch search were replayed, plus controls -- the others are the same game move for move):
#   fresh development block 5348-5392 (45 games): used 20 -> 28 (44% -> 62%), raw 0.363 -> 0.373 (0.362 with 1.
#     and 2. alone);
#   held-out 63532-63561 (30 games, run once): no such trip but one Orcish Town reached at XL 7: used 22 -> 22,
#     raw 0.411 -> 0.411;
#   held-out 59936-59965 (30 games, run once): used 14 -> 18 (47% -> 60%), raw 0.395 -> 0.387 (0.400 with 1. and
#     2. alone: the one held-out dive that 3. redrew ended on Dlvl 11 instead of 27);
#   both held-out blocks (60 games): used 60% -> 67%, raw 0.403 -> 0.399 (0.405 with 1. and 2. alone);
#   public seeds 0-14: used 11 -> 12 (seed 0: Orcish Town's altar). Raw: the parent 0.473 in my replay (0.486 in
#     the judge's run), this version 0.506 and 0.534 in two runs -- seeds 1, 4, 11 and 14 differ run to run in
#     both programs (seed 1: 0.379 or 0.807); what the change itself moves is seed 7, whose dive 3. redrew
#     (Dlvl 13 -> 29, +0.026 on the mean, the same in both runs): the luck of one draw, not a measure of the rule.
#     Extra seeds 386141-386150: no such trip.
#   All 130 games: used 74 -> 87 (57% -> 67%), raw +0.004.
# Early-game ideas tried first in this iteration, each measured on the same seeds, none of which raised the score
# (on the fresh blocks 22-27% of games end on Dlvl 1-4, most of them in the grind before the trip):
#   a. FAINT_NOT_WAITED_OUT -- a Fainting hero prays once her last prayer is 1000 turns back (jf_config, at
#      TOUR_FAINT_PRAYER_GAP: the grind's Fainting deaths 7 -> 1 on 130 games, its failed prayers 6 -> 9, raw
#      0.403 -> 0.387 on the 60 held-out games with this version's two rules on top);
#   b. FAINT_FIGHT -- she strikes the weak monster next to her instead of re-engraving (9 games: 3 of 4 faint
#      deaths survived the spell, 1 new death in the next faint: an intact Elbereth does protect);
#   c. MINES_FINISH -- a hero without a digging tool starts the trip at XL 7, as a tool holder does, instead of
#      grinding on to XL 8 on Dlvl 2 (a median 3,800 turns; the grind needs a hunger prayer every 1,700 turns,
#      the trips one every 4,100: the Mines feed her). On the 16 games it changes: games ending on Dlvl 1-4
#      4 -> 2 and raw 0.365 -> 0.409, but temple used 8 -> 5 and the dives that follow end 2.5 levels higher;
#      restricted to heroes who already know the branch: raw 0.365 -> 0.322. Not a gain 16 games can show.
# What is left (130 games, this version: the temple used in 87, 67%): dead before the trip 15%, dead on it 7%,
# Orcish Town below XL 8 / with AC above 3 / without a tool 5%, no Mines branch 3%, a level that is not opening
# 2%, a town whose temple stays out of reach 1% (a floating eye in its only corridor).
# sources: /refs/history.md #11 and /refs/history/11.diff (SECOND_WIND and ORCISH_ALTAR: the code and its
# measurements; #2 and #6 for the earlier breach and frontier-walk attempts) ; NetHack 3.6.6 dat/mines.des
# (minetn-1 "Orcish Town": the orc army "inside", "ALTAR:(20,13),noalign,shrine") and src/monst.c (orc-captain:
# level 5, two weapon attacks 2d4) ; https://nethackwiki.com/wiki/Minetown (Orcish Town: no priest, the altar
# unaligned but there, "many orcs carry poisoned orcish arrows", entry "requires a digging tool"; Minetown on Mines
# level 3 or 4) ; https://nethackwiki.com/wiki/Forum:OrcTown (players: dig straight into the temple; the town's
# orcs come to you) ; https://nethackwiki.com/wiki/Gnomish_Mines ("a mines level is often substantially harder
# than a level of the main dungeon"; filler levels are caverns; back off and come back stronger) ;
# https://nethackwiki.com/wiki/Valkyrie and https://nethackwiki.com/wiki/Standard_strategy (Minetown for the
# altar's curse test; pray when Weak, about 1000 turns apart) ; https://nethackwiki.com/wiki/Protection_racket
# (400*XL gold a point: out of reach here, median gold at the temple ~100) ; https://nethackwiki.com/wiki/Nutrition
# and https://nethackwiki.com/wiki/Elbereth with NetHack 3.6.6 src/eat.c, src/pray.c, src/allmain.c, src/monmove.c
# (read at https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/) for a. and b. ; player
# discussions: the Maniac's Ascension Guide (https://www.alt.org/nethack/mirror/homepage.mac.com/mhjohnson/mag-r2.html:
# Minetown "is not a destination you should die for"; a Valkyrie at XL 5 buys one donation there),
# https://gamefaqs.gamespot.com/boards/582497-nethack/37928712?page=2 (pray as soon as you are Weak, a thousand
# turns apart; the Mines' gnome and dwarf corpses as food) and
# https://steamcommunity.com/app/341390/discussions/0/481115363875217535/ ("Always dying from starvation": the
# Mines have plenty to eat, starvation comes from staying too shallow) ; /refs/top/README.md (every top program is
# a dive-first engine of this lineage; the leader of val-hum-law-fem is this program's ancestor without the trip)
# ; /refs/reference/README.md (#918 / #862: FIND_MINETOWN tours and the 400*XL protection price).
#
# ---- fifth iteration: THE TRIPS THAT END ALIVE WITHOUT THE TEMPLE (ORCISH_ALTAR, SECOND_WIND) ----
# hypothesis: the stage "use Minetown" is lost in three ways -- the hero dies (before or on the trip), the town is
# Orcish Town, or a budget ends the trip -- and only the last two can be changed without touching the games that
# already succeed (every game replays move for move until the trip's own decision differs). Of 175 parent games
# replayed with logs (development 0-14, 386141-386150, 72855-72899; held-out 48857-48916 and 73613-73657) the
# temple altar flashed in 96 (55%); 19 trips ended at Orcish Town's wall and 11 on the 1500-turn level budget of
# a Mines filler level; 40 heroes died before or on the trip.
# Ideas tried, each against the parent on the same seeds, and the two combined here:
#   1. ORCISH_ALTAR (_orc_go, _orc_step; new): Orcish Town (1 town in 7) has no priest, but its altar is there
#      ("useful for BUC", mines.des) and shows a black / amber flash like any other; the map is fixed and centred,
#      so the altar's square is known before it is seen. A hero with a pick-axe or mattock, XL 7+ and not below
#      the level's depth, AC 3 or better, not Weak and with her prayer in hand (800 turns since the last one)
#      walks round the town on the strip of floor outside its wall to the point south of the temple and digs in
#      there: the outer wall, the lane, the temple's back wall, the altar -- two walls, four steps (dig.c: the
#      level is a maze level without NON_DIGGABLE, a dug wall becomes floor; no Watch to mind it). The opened wall
#      is held from OUTSIDE first: what comes out comes one at a time and only the lane square behind the gap has
#      a line of fire to her (the wiki: "breach the walls strategically, to funnel the orcs"; many orcs shoot
#      poisoned arrows) -- until nothing hostile has been in view for 25 turns, then rest, then in. A floating eye
#      or mold is neither waited for nor walked into. A town whose wall a dwarf has already opened is simply
#      walked into (tool or not). Measured on the 8 heroes it was built on (4 development games, 4 of the block
#      48857-48916): first version (nearest wall, no prayer rule): 4 of 5 at the altar, 1 dead (she had prayed 95
#      turns earlier); south entry without the hold: 5 of 8 at the altar, 2 dead within 40 turns of opening the
#      wall; with the hold (this version): 7 of 8 flashed the altar, none died in the town, 1 turned back Weak.
#      On the fresh block 73613-73657 (run once, after the code was final): 5 heroes qualified, 4 flashed the
#      altar, 1 turned back, none died in the town.
#   2. SECOND_WIND (_second_wind, exploration_logic.mines_walk; new): the level budget ended 9 trips whose level
#      was still opening -- the squares in reach had grown by 30 to 340 in the last 400 turns: slow exploration,
#      not a wall (dwarves had tunnelled the level into hundreds of corridor squares, each dead end of which
#      AutoAscend's explorer searches 15 times, and every step onto new ground is followed by a search for traps
#      that finds an adjacent one 1 time in 8). Such a trip, with a fit hero (60% HP, not Weak), gets 1200 more
#      turns once per level and walks them without that searching: the Mines' caves have no secret doors or
#      corridors (mkmap.c join_map joins them with floor, sp_lev.c dig_corridor hides a square only in a real
#      corridor). A trip that stands still ends as before. Measured:
#      fired in 6 of the 9 (3 development, 3 held-out): all 6 reached the town, 5 used the temple and the 6th
#      found Orcish Town (used with 1.); no death on the extended levels. Fresh block 73613-73657: fired in 2
#      trips, 1 used the temple, 1 ran out the next level's budget standing still.
#   3. TRIP_FAST_EXPLORE -- the same search-free walk for every trip from its first turn (/refs/history #6's
#      frontier walk on its own): 70 development games, temple used 45 -> 46, raw progress 0.429 -> 0.418, deaths
#      on the trip 5 -> 7, and every game takes another path (a change that diverges all games needs hundreds of
#      games to judge): dropped for 2., which acts only where the parent's trip had ended.
# Both act only at a point where the parent's trip was over, so every other game is unchanged move for move
# (checked on control seeds). Results are at the end of this block's sources.
# Not done: the towns built from rooms where the temple stays unfound (3 of 70: a hero boxed in by a scroll of
# earth's boulders, a mold in a doorway that the explorer keeps walking to, a floating eye in the temple door);
# protection from the priest (median gold at the temple 100, 400*XL = 2800+ needed).
# sources: NetHack 3.6.6 dat/mines.des as shipped with NLE (nle/nethackdir/dat/mines.des: minetn-1 "Orcish Town":
# the MAP with its closed outer wall and iron bars, "ALTAR:(20,13),noalign,shrine", "the altar's defiled; useful for
# BUC but never coaligned", the orc army "inside", no NON_DIGGABLE line; minefill: "STAIR: random", INIT_MAP mines) ;
# https://nethackwiki.com/wiki/Minetown (Orcish Town: "requires a digging tool or a means of breaching the iron
# bars"; "Use the corridors, or breach the walls strategically, to funnel the orcs into rows and columns"; "many
# orcs carry poisoned orcish arrows and will shoot through the bars"; orcs are slow; no Watch, shopkeepers or
# priest) ; https://nethackwiki.com/wiki/Gnomish_Mines (filler levels are "simple caverns"; "a mines level is often
# substantially harder than a level of the main dungeon") ; https://nethackwiki.com/wiki/Valkyrie ("smart
# retreating and Elbereth usage ... especially against groups such as soldier ants and Mordor orcs"; "an AC of
# roughly -5 by the end of the Gnomish Mines") ; https://nethackwiki.com/wiki/Pick-axe (tunnels through walls;
# digging is an occupation a hostile's approach interrupts; the Watch warns only where there is one) ;
# https://nethackwiki.com/wiki/Altar (a dropped object flashes black / amber on any altar) ; NetHack 3.6 src/dig.c
# dig() ("if (level.flags.is_maze_lev) lev->typ = ROOM": a dug wall of this level is floor), src/mkmap.c join_map
# ("dig_corridor(&sm, &em, FALSE, fg_typ, bg_typ)") with src/sp_lev.c dig_corridor ("if (ftyp != CORR || rn2(100))
# crm->typ = ftyp; else crm->typ = SCORR": the Mines' fg_typ is ROOM, so nothing is hidden) and src/detect.c
# dosearch0() ("!trap->tseen && !rnl(8)": one search finds an adjacent trap 1 time in 8), read at
# https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/ ; player discussions: https://nethack-yanis.github.io/tag/orctown (players on Orcish
# Town: entry "takes digging or acid", "conquer Orctown" by killing the orcs, the lost priest as the complaint) and
# the search summaries of r/nethack and rec.games.roguelike.nethack for "Orcish Town" (no thread with a tactic
# beyond the wiki's funnel; "the priestless altar as the level's sole upside") ; /refs/history.md #2 (a breach
# through the nearest wall: 4 of 4 entered, 2 died -- here the entry point, the prayer rule and the hold), #6 and
# #9 (the frontier walk for every trip; discarded on the held-out seeds) ; /refs/top/README.md (the top programs
# are dive-first engines without a Minetown trip) ; /refs/reference/README.md (#862: Orcish Town recognised and
# skipped; #918: protection needs 400*XL gold).
# Measured, parent -> this version, same seeds (used = an altar on the town level flashed for a dropped object;
# raw = mean progress; est = progress x 1.3 where the temple was used, the stage's share of the run's multiplier):
#   development, 70 games (0-14, 386141-386150, 72855-72899): used 45 -> 51 (64% -> 73%), raw 0.429 -> 0.429,
#     est 0.525 -> 0.539; games ending on Dlvl <= 4: 9 -> 9;
#   held-out 48857-48916, 60 games: used 27 -> 33 (45% -> 55%), raw 0.331 -> 0.335, est 0.398 -> 0.416 (run once
#     for SECOND_WIND; its four Orcish games were read before the hold was added, so for ORCISH_ALTAR they are
#     development games);
#   held-out 73613-73657, 45 games, run once with the final code: used 24 -> 29 (53% -> 64%), raw 0.354 -> 0.339,
#     est 0.423 -> 0.424 (nobody died on the trip; two of the six changed games died earlier in the dive that
#     follows it -- the dive after a changed trip is a new draw);
#   both held-out blocks, 105 games: used 49% -> 59%, raw 0.341 -> 0.337, est 0.408 -> 0.420; games ending on
#     Dlvl <= 4: 29 -> 29. Public seeds 0-14 (the official command): raw progress unchanged on every seed but the
#     two that differ between two runs of the same program; seed 0 now uses Orcish Town's altar.
# (Only the games whose trip the parent ended at Orcish Town or on a level budget were replayed, plus controls:
# the others are identical move for move.)
#
# ---- fourth iteration: THE TRIP GETS THROUGH THE MINES' TIGHT SPOTS (SQUEEZE_CORNER_FIX, the way-down tunnel,
# ---- TRIP_KICK_OUT) ----
# hypothesis: of 85 parent games replayed with logs (0-14, 386141-386150, 71000-71029 and the held-out block
# 76988-77017) the temple was used in 51 (60%). The trips that end with a living hero and no temple are the ones a
# change can win back: 8 ran out their 1500-turn level budget on a Mines filler level, 2 their town budget. Map dumps
# of every development stall showed the same picture: the level's known part ends at a diagonal gap between two cave
# corners, and the hero carries 604-955 (the game lets only 600 through such a gap). Three things a player does
# there, combined here after each was measured:
#   1. SQUEEZE_CORNER_FIX (agent._corner_open, utils.bfs_corner): the path-finder's squeeze rule asks the terrain,
#      as hack.c test_move does. It refused every diagonal step whose two orthogonal neighbours were missing from its
#      own walkable mask -- which leaves out known traps, boulders and peaceful monsters -- while the game refuses
#      only when both are rock. On the trip's Mines levels a trap or a peaceful dwarf beside a corner no longer
#      closes the passage (2 of the 3 stalls of heroes without a pick-axe got through with it).
#   2. the way-down tunnel (TUNNEL_DOWN_AFTER 300, _tunnel_down: the walk-and-dig route the way back already uses):
#      a '>' still out of reach 300 turns after arriving, known floor behind the obstacle, a pick-axe or mattock in
#      the pack -- one rock corner of the squeeze is dug out, or a few squares round the trap in the only passage.
#      Alone, on the 7 development stalls: the 4 with a tool -> 3 reached the temple, 1 died (soldier ants).
#   3. TRIP_KICK_OUT (_kick_out, ported from /refs/history #6): the room-built towns put each staircase in a room of
#      its own behind a door that may be locked; the trip searched that room's walls until the town budget ran out.
#      With nobody of the town in view the door is kicked open (3 of 3 such games on the measured seeds got out).
# Measured, parent -> this version, same seeds (est = progress x the run's multiplier rebuilt from XL, AC, temple
# use and holes, floored at 1): development 55 games: Minetown reached 40 -> 45, temple used 38 -> 40, raw progress
# 0.424 -> 0.423, est 0.455 -> 0.454; held-out 76988-77017 (30 games, run once): reached 17 -> 20, temple used
# 13 -> 15, raw 0.325 -> 0.317, est 0.339 -> 0.337. So: the temple is used in 65% of the 85 games instead of 60%,
# at an unchanged score. (The multiplier's floor is why the score does not follow: the dig-dive's -0.50 swallows
# the temple's +0.30 unless XL and AC are worth more than +0.20.)
# Tried in this iteration and dropped, each on the development games it changes: no escape dig on the trip (8 games
# where it fired: temple used 2 -> 3, 3 deaths either way); a readiness gate -- a hero whose trip would start at
# XL 7 with AC 4 or worse grinds on to XL 8 first (7 games: temple used 4 -> 1, deaths 1 -> 3: the grind adds no
# armor and the Mines kill her at XL 8 just the same); the pack dropped to 550 at any squeeze that opens one new
# square (2 games: 0 gained, 1 died); the squeeze rule and the tunnel switched on only once a level has been
# stalled for 600 turns (9 games: temple used 3 -> 2 -- too late for the level budget, and two slow trips that
# used to arrive did not).
# What is left (85 games of this version): dead before the trip 11%, dead on the trip 8%, no Mines branch found on
# Dlvl 2-4 6%, Orcish Town 7% (now that more trips arrive), a temple that stays out of reach in the town 1-2%.
# sources: NetHack 3.6.x src/hack.c read at https://nethackwiki.com/wiki/Source:NetHack_3.6.1/src/hack.c
# (test_move: "if (dx && dy && bad_rock(youmonst.data, ux, y) && bad_rock(youmonst.data, x, uy))" ->
# cant_squeeze_thru: "if (amt > 600) return 2", "You are carrying too much to get through."; bad_rock: a boulder
# counts only in Sokoban) ; NetHack 3.6.6 dat/mines.des from
# https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/dat/mines.des (minefill: "STAIR: random"
# on a mkmap cave with 6 random traps; minetn-1 Orcish Town: closed wall, "ALTAR:(20,13),noalign,shrine") ;
# https://nethackwiki.com/wiki/Minetown (what the Watch minds: a door kicked where a watchman sees it; Orcish Town
# needs "a means of digging through the walls") ; https://nethackwiki.com/wiki/Gnomish_Mines (filler levels are
# caverns with 6 random traps; "a mines level is often substantially harder than a level of the main dungeon") ;
# https://nethackwiki.com/wiki/Valkyrie ("smart retreating and Elbereth usage"; "an AC of roughly -5 by the end
# of the Gnomish Mines") ; player discussions: https://groups.google.com/g/rec.games.roguelike.nethack/c/AQkz3Jm1NZU
# ("stuck in gnomish mines") and https://groups.google.com/d/topic/rec.games.roguelike.nethack/vGnoj7fWBE4 ("Dead
# end in the Gnomish Mines": stairs hide under objects, a pick-axe is the way through) ; /refs/history.md #9 (the
# squeeze rule), #6 (_kick_out), #4 (the tunnel on the way back; its way-down variant measured there on its own) ;
# /refs/top/README.md (all top programs are dive-first engines of this lineage, none goes to Minetown) ;
# /refs/reference/README.md (#918/#862: FIND_MINETOWN tours, already the basis of the parent's trip).
TRIP_MIN_XL = 6                 # Minetown wants XL 6-8 (the dive trigger is XL 7 with a pick-axe, XL 8 without)
TRIP_TOTAL_TURNS = 9000         # the whole trip, from its start to the hand-over
BRANCH_TURNS = 1700             # looking for the Mines branch on Dlvl 2-4 (3000 before the sixth iteration: no
#                                 trip found the branch after turn 1532 of its search -- see the top, 3.)
TRIP_LEVEL_TURNS = 1500         # on one Mines level without the trip moving on
TOWN_TURNS = 3000               # in the town itself (a locked temple, a priest on the altar)
REST_BELOW = 0.8                # the trip walks on only above this fraction of max HP (nothing hostile in view)
MIDDLE_SEEN = 90                # squares of a level's middle band seen without a town sign: a filler level
ESCAPE_HP = 0.5                 # above the town, a losing fight at or below this fraction of max HP is dug away from
UNBLOCK_AFTER_TURNS = 150       # a staircase still out of reach this long on a Mines level: squeezes and traps
TRAPS_AFTER_TURNS = 350         # ... and only this late through known traps
POST_HOLD_GAP = 800             # the dive proper starts this long after the last prayer (dive_logic.DIVE_PRAYER_GAP)
POST_HOLD_MAX = 1200            # ... or after this many turns of waiting for it
DIG_AFTER_TURNS = 0             # (off) a '>' above the town still cut off after this many turns: dig down. Measured on
# 79 development games: with 600 the trip used the temple in 75% of games instead of 63%, but a hole lands away from
# the level's '<' and the way back up took 500+ turns instead of ~120: 5 deaths on the way back against 0-1.
# Measured again in the third iteration with PICK_TUNNEL as the way back: (a) the hole at 1000 turns plus the tunnel
# to cut-off floor at 400, on the 8 development games whose trip had ended on the level budget with a pick-axe in
# the pack: 2 reached the temple, 4 died on Mines level 2-4 (the parent: none -- they turned back at the budget and
# dived); (b) the way-down tunnel alone at 300 turns, 79 development games: the temple used in 63% of games either
# way, raw progress 0.419 -> 0.401. A hero who has been stuck for hundreds of turns goes on hungry and with her
# prayer spent, and what a finished trip adds (+0.30 on the multiplier) is a third of what a death in the Mines
# costs. Both stay off: the level budget is the safe end of such a trip.
KICK_OUT_AFTER = 300            # TRIP_KICK_OUT: on the town level this long without a way to the altar
KICK_OUT_REACH = 200            # ... at most this many squares in reach -- the town is still behind the door
KICK_OUT_TRIES = 60             # ... kicks at one door
TUNNEL_DOWN_AFTER = 300         # the way down: the '>' and known floor out of reach this long: tunnel to that floor
#                                 (on again in the fourth iteration, together with SQUEEZE_CORNER_FIX: see the top)
TUNNEL_AFTER_TURNS = 400        # PICK_TUNNEL, the way up: no '<' known this long after arriving: to cut-off floor
TUNNEL_UP_AFTER_TURNS = 120     # ... the known '<' still out of reach this long after arriving: tunnel to it
TUNNEL_DIG_COST = 6             # a square of rock costs about this many turns of digging (dig.c: effort 100 at
#                                 10 + d4 + abon + enchantment + damage bonus a turn, doubled for a dwarf)
TUNNEL_MAX_DIGS = 60            # squares dug per level before the tunnel is given up there
TUNNEL_SQUARE_TRIES = 6         # applications at one square before it counts as undiggable
WIND_TURNS = 1200               # SECOND_WIND: turns added to a level budget that runs out with the level still opening
WIND_LOOK_BACK = 400            # ... "still opening": the squares in reach grew by WIND_GROWTH over this many turns
WIND_GROWTH = 30
WIND_MIN_HP = 0.6               # ... and the hero is fit: this fraction of max HP, not Weak, a prayer not failed
ORC_ALTAR = (14, 40)            # ORCISH_ALTAR: minetn-1 is a fixed map, centred: its altar (map 20,13) is always here
ORC_TURNS = 1500                # ... turns in Orcish Town before the trip gives the altar up
ORC_MIN_XL = 8                  # ... the breach is for a hero of this level (7 in /refs/history #11: see the top)
ORC_MAX_AC = 3                  # ... and this armor class or better
ORC_PRAYER_GAP = 800            # ... with the emergency prayer in hand (turns since the last one)
ORC_WAIT = 40                   # ... turns the tunnel waits for a hostile within three squares to come and be fought
ORC_HOLD_QUIET = 25             # ... the opened wall is held from outside until nothing hostile was in view this long
ORC_HOLD_MAX = 150              # ... or for this many turns
ORC_GRIND_TURNS = 5000          # TRIP_RETRY: turns a hero short of ORC_MIN_XL grinds for it before she dives without the altar
ORC_RECT = (2, 18, 21, 55)      # the town's outer wall on the screen: rows 2-18, columns 21-55 (map 1-17 / 1-35)
ORC_ENTRY = ((18, 40), (17, 40), (16, 40), (15, 40))   # the way in from the south: the outer wall, the lane behind
#                                 it, the temple's back wall, the temple floor in front of the altar
ALTAR_PICKUP_TRIES = 4
GATHER_TURNS = 400              # ALTAR_GATHER: turns spent fetching things for a dark altar
GATHER_BATCH = 6                # ... stacks carried to the altar at a time
GATHER_ROUNDS = 2               # ... drops of fetched things
GATHER_DIST = 70                # ... steps to a square worth fetching from
GATHER_STACK_WEIGHT = 60        # ... weight of one stack fetched (no mail coats)
GATHER_TOTAL_WEIGHT = 160       # ... and of a whole batch
DONATE_TRIES = 6


def _words(item):
    return f' {item.text or ""} '


def _buc_shown(item):
    w = _words(item)
    return ' cursed ' in w or ' uncursed ' in w or ' blessed ' in w or ' holy water' in w


def _glyph(item):
    return item.glyphs[0] if item.glyphs else None


class MinetownTrip:
    _PRIEST = None

    def __init__(self, dive):
        self.dive = dive
        self.agent = dive.agent
        self.active = False
        self.done = False
        self.start_turn = None
        self._level_key = None
        self._level_since = 0
        self._town_since = None
        self.altar_tested = False      # something of ours was dropped on the town's altar
        self.altar_drops = 0
        self.flashes = 0
        self.pending = None            # (altar pos, glyphs dropped, turn) still to pick up
        self._flash_tries = 0          # ALTAR_FLASH: second drops made (something known cursed / blessed)
        self._rewield = None           # ... the glyph of the wielded weapon that went on the altar
        self._pickup_tries = 0
        self.donations = 0
        self.protection = 0
        self._donate_tries = 0
        self._priest_off = False       # no priest to talk to / he refused / protection capped
        self._priest_wait = 0
        self.end_reason = None
        self._filler = set()           # Mines level 3/4 keys judged not to be the town
        self._unblock_turn = {}        # level key -> last turn unblock() acted there
        self._kicks = {}               # TRIP_KICK_OUT: (level key, door) -> kicks
        self._wear_turn = -10 ** 9
        self.holding = False           # the post-trip prayer hold (dig_first stays quiet meanwhile)
        self._hold_start = None
        self._hold_over = False
        self._escapes = 0
        self._tunnel_blocked = set()   # PICK_TUNNEL: (level key, y, x) that did not dig / could not be stepped on
        self._tunnel_tries = {}        # (level key, y, x) -> applications / step attempts
        self._tunnel_digs = {}         # level key -> squares dug
        self._tunnel_logged = set()
        self._tunnel_quiet = {}        # level key -> turn until which no route is looked for
        self._up_key = None            # the way up: the level we are on and the turn we arrived
        self._up_since = 0
        self.holes = 0
        self._reach_log = {}           # SECOND_WIND: level key -> [(turn, squares in reach)]
        self._retried = False          # TRIP_RETRY: the second trip has been started
        self.end_turn = None           # ... the turn the trip ended
        self._gather_since = None      # ALTAR_GATHER: the turn the fetching began
        self._gather_skip = set()      # ... (level key, y, x) looked at
        self._gather_glyphs = set()    # ... glyphs of what was fetched
        self._gather_weight = 0        # ... weight fetched for the next drop
        self._gather_rounds = 0        # ... drops made
        self._gather_over = False
        self._mines_seen = False       # BRANCH_CLOCK_FIX: this trip has stood in the Mines
        self._branch_since = 0         # ... the turn it was thrown back into the Dungeons of Doom
        self._winds = {}               # ... level key -> the turn its extended budget ends
        self._orc_since = None         # ORCISH_ALTAR: the turn Orcish Town was recognised
        self._orc_wait = 0
        self._orc_ok = None
        self._orc_hold = None          # [first turn, last turn something hostile was in view] at the opened wall
        self._orc_held = False

    # ------------------------------------------------------------------ helpers

    def log(self, msg):
        self.agent.log(f'MINETOWN {msg}')

    @classmethod
    def priest_glyph(cls):
        if cls._PRIEST is None:
            cls._PRIEST = frozenset({MON.from_name('aligned priest')})
        return cls._PRIEST

    def is_town_level(self, level):
        """The level is Minetown: Mines level 3 or 4 (dungeon.def) with an altar, or town people in view (Orcish
        Town has neither priest nor watch nor shopkeepers, but keeps its altar)."""
        agent = self.agent
        if level.dungeon_number != Level.GNOMISH_MINES or level.level_number not in (3, 4):
            return False
        if agent.global_logic.minetown_level == level.key():
            return True
        if level.key() in self.dive._town_levels:
            return True   # the Watch, a shopkeeper or a priest was seen here (DiveLogic._town_sighting)
        # the Mines' filler levels have no doors, altars or fountains
        return bool(level.altars) or bool(utils.isin(level.objects, G.DOORS, G.ALTAR, G.FOUNTAIN, G.BARS).any())

    def orcish(self, level):
        """Orcish Town (mines.des minetn-1: 'Note the barricades (iron bars)'): the only town variant with iron bars.
        Its temple lies behind a closed wall among 5-15 orc-captains and Uruk-hai and has no priest: not visited."""
        return bool(utils.isin(level.objects, G.BARS).any())

    def _middle_seen(self, level):
        """How much of the level's middle band (where the town map is centred) has been seen."""
        return int(level.seen[1:20, 28:51].sum())

    def _judge(self, level):
        """A Mines level 3 or 4 whose middle has been looked at without any town sign is a filler level."""
        key = level.key()
        if key in self._filler or self.is_town_level(level):
            return
        if self._middle_seen(level) >= MIDDLE_SEEN:
            self._filler.add(key)
            self.log(f'{key} is a filler level (its middle seen, no town sign)')

    def note_level(self):
        """Called from GlobalLogic.update: recognise the town (also without a shopkeeper in view)."""
        agent = self.agent
        gl = agent.global_logic
        if agent.character.prop.hallu:
            return
        level = agent.current_level()
        if gl.minetown_level is None and self.is_town_level(level):
            gl.minetown_level = level.key()
            self.log(f'town recognised on {level.key()} (depth {agent.blstats.depth}) by its altar, doors or people')

    def in_town(self):
        gl = self.agent.global_logic
        return gl.minetown_level is not None and self.agent.current_level().key() == gl.minetown_level

    def _altars(self):
        """Altars of this level: [(y, x)], reachable ones first by distance (unreachable ones have dis -1)."""
        agent = self.agent
        level = agent.current_level()
        pos = set((int(y), int(x)) for y, x in level.altars)
        pos |= set((int(y), int(x)) for y, x in zip(*utils.isin(level.objects, G.ALTAR).nonzero()))
        pos -= set(getattr(level, 'not_altars', ()))
        return sorted(pos)

    def _hostiles_within(self, radius):
        bl = self.agent.blstats
        return [m for m in self.agent.get_visible_monsters() if max(abs(m[1] - bl.y), abs(m[2] - bl.x)) <= radius]

    def _active_hostiles_within(self, radius):
        """ORCISH_ALTAR: hostiles within `radius` that come and fight -- not the floating eye, mold or jelly the
        fight strategy leaves alone (waiting for one of those to attack is waiting for ever)."""
        from .combat.monster_utils import ONLY_RANGED_SLOW_MONSTERS
        return [m for m in self._hostiles_within(radius) if m[3].mname not in ONLY_RANGED_SLOW_MONSTERS]

    def _passive_mask(self):
        from .combat.monster_utils import ONLY_RANGED_SLOW_MONSTERS
        mask = np.zeros(self.agent.current_level().walkable.shape, dtype=bool)
        for m in self.agent.get_visible_monsters():
            if m[3].mname in ONLY_RANGED_SLOW_MONSTERS:
                mask[int(m[1]), int(m[2])] = True
        return mask

    def _priests(self):
        agent = self.agent
        mask = utils.isin(agent.glyphs, self.priest_glyph()) & agent.monster_tracker.peaceful_monster_mask
        return [(int(y), int(x)) for y, x in zip(*mask.nonzero())]

    def price(self):
        return 400 * int(self.agent.blstats.experience_level)

    def can_donate(self):
        """priest.c priest_talk: 400*XL <= offer < 600*XL buys protection (u.ublessed < 9 for sure)."""
        return not self._priest_off and self.protection < 7 and self._donate_tries < DONATE_TRIES and \
            int(self.agent.blstats.gold) >= self.price()

    def altar_items(self):
        """What goes on the altar: every carried, unworn item whose curse status the display does not show. A scroll
        that may be scare monster stays in the pack (a second pickup turns it to dust, pickup.c)."""
        from . import power_route
        out = []
        for it in self.agent.inventory.items:
            if it.equipped or it.category == nh.COIN_CLASS or not it.can_be_dropped_from_inventory():
                continue
            if _buc_shown(it):
                continue
            if it.category == nh.SCROLL_CLASS and power_route.SCARE_SCROLL in it.objs:
                continue
            if it.category == nh.BALL_CLASS or it.category == nh.CHAIN_CLASS or it.category == nh.ROCK_CLASS:
                continue
            if self._is_digging_tool(it):
                continue   # the dive's pick-axe never leaves the pack
            out.append(it)
        return out

    def _is_digging_tool(self, item):
        w = _words(item)
        return ' pick-axe' in w or ' mattock' in w or ' broad pick' in w

    def _fallback_item(self):
        """Nothing of unknown BUC is carried: one light known item still shows how the altar answers."""
        best = None
        for it in self.agent.inventory.items:
            if it.equipped or it.category == nh.COIN_CLASS or not it.can_be_dropped_from_inventory():
                continue
            if it.category == nh.SCROLL_CLASS or it.category in (nh.BALL_CLASS, nh.CHAIN_CLASS, nh.ROCK_CLASS):
                continue
            if self._is_digging_tool(it):
                continue
            if best is None or it.count < best.count:
                best = it
        return best

    # ------------------------------------------------------------------ the trip

    def start(self, rescue):
        """Called by DiveLogic.should_dive at the moment the dive phase begins: the planned dive (never a rescue)
        takes the stairs to Minetown first."""
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        if self.done or self.active or not jf_config.MINETOWN_TRIP:
            return False
        if rescue or agent.prayer_failed or bl.experience_level < TRIP_MIN_XL:
            self.done = True
            self.end_reason = 'not started'
            self.log(f'no trip: rescue={rescue} prayer_failed={agent.prayer_failed} XL {bl.experience_level}')
            return False
        if level.dungeon_number not in (Level.DUNGEONS_OF_DOOM, Level.GNOMISH_MINES) or \
                (level.dungeon_number == Level.DUNGEONS_OF_DOOM and bl.depth > 4) or \
                (level.dungeon_number == Level.GNOMISH_MINES and level.level_number > 4):
            self.done = True
            self.end_reason = 'not started'
            self.log(f'no trip: on {level.key()} at depth {bl.depth}')
            return False
        self.active = True
        self.start_turn = int(bl.time)
        self._level_key = level.key()
        self._level_since = int(bl.time)
        self.log(f'trip starts at XL {bl.experience_level}, turn {bl.time}, depth {bl.depth}, gold {bl.gold}, '
                 f'hp {bl.hitpoints}/{bl.max_hitpoints}, AC {bl.armor_class}, tool {self.dive.digging_tool()!r}')
        return True

    def min_xl(self):
        return TRIP_MIN_XL

    def orc_pending(self):
        """TRIP_RETRY: the trip ended alive at Orcish Town's wall and has not been made again."""
        return bool(jf_config.TRIP_RETRY and jf_config.ORCISH_ALTAR and self.done and not self.active and
                    self.end_reason == 'Orcish Town' and not self._retried and not self.altar_tested and
                    self.start_turn is not None and not self.agent.prayer_failed)

    def orc_fit(self, min_xl=None, prayer=True, hunger=True):
        """... and the hero could breach it, by _orc_go's own rule: a digging tool, the armor class, the level
        (min_xl None: ORC_MIN_XL and the town's depth), not Weak, and -- with `prayer` -- her prayer in hand."""
        agent = self.agent
        bl = agent.blstats
        town = agent.global_logic.minetown_level
        depth = 8 if town is None else int(town[1]) + 4
        need = max(ORC_MIN_XL, depth) if min_xl is None else min_xl
        if self.dive.digging_tool() is None or bl.experience_level < need or bl.armor_class > ORC_MAX_AC or \
                agent.character.prop.polymorph or (hunger and bl.hunger_state >= Hunger.WEAK):
            return False
        last = agent.last_prayer_turn
        return not prayer or last is None or int(bl.time) - last >= ORC_PRAYER_GAP

    def orc_grind(self):
        """TRIP_RETRY: a hero with the tool and the armor for Orcish Town's breach who lacks what the grind brings
        -- the level (ORC_MIN_XL: a tool holder's dive starts at XL 7), or the prayer she has just said -- goes
        back to it instead of diving without the altar; ORC_GRIND_TURNS at most."""
        bl = self.agent.blstats
        if not self.orc_pending() or self.end_turn is None or int(bl.time) - self.end_turn > ORC_GRIND_TURNS:
            return False
        return self.orc_fit(min_xl=TRIP_MIN_XL, prayer=False, hunger=False) and not self.orc_fit()

    def retry(self, rescue):
        """TRIP_RETRY (called when the dive proper starts, before start()): the early trip ended alive without the
        altar -- it is made once more when what stopped it has changed: a level / town budget (the level's known
        part stays known, the hero is stronger, a pick-axe may have come), Orcish Town for a hero who can now
        breach it, the Mines branch once a second '>' is known. Only resets the trip; start() does the rest."""
        agent = self.agent
        bl = agent.blstats
        if not jf_config.TRIP_RETRY or not self.done or self.start_turn is None or self.altar_tested or \
                self._retried or rescue or agent.prayer_failed:
            return False
        why = self.end_reason
        if why in ('level budget', 'town budget'):
            ok = True
        elif why == 'Orcish Town':
            ok = self.orc_fit()
        elif why in ('branch budget', 'no Mines branch', 'no Mines branch above'):
            ok = self.dive._mines_branch_target() is not None
        else:
            ok = False
        if not ok:
            return False
        self._retried = True
        self._mines_seen = False
        self._branch_since = 0
        self.log(f'trip retry (the first ended: {why}): XL {bl.experience_level}, '
                 f'AC {bl.armor_class}, tool {self.dive.digging_tool()!r}')
        self.done = False
        self.end_reason = None
        self._town_since = None
        self._level_key = None
        self._winds = {}
        self._reach_log = {}
        self._orc_ok = None
        self._orc_since = None
        self._gather_over = False
        self._hold_over = False
        self._hold_start = None
        self.holding = False
        return True

    def business_done(self):
        """The altar has answered and nothing is left to do with the priest."""
        if not self.altar_tested or self.pending is not None:
            return False
        if self.can_donate() and self.in_town():
            return False
        if self._flash_due():
            return False
        if self._gather_due():
            return False
        return True

    def _flash_count(self):
        return int(getattr(self.agent, '_altar_flashes', 0))

    def _flash_items(self):
        """ALTAR_FLASH: one carried thing that is known to be cursed or blessed -- on an altar it flashes for
        certain. Something from the pack first; else the wielded weapon when it is blessed (Excalibur always is)."""
        from . import power_route
        inv = self.agent.inventory.items
        best = None
        for it in inv:
            if it.equipped or it.category in (nh.COIN_CLASS, nh.GEM_CLASS, nh.BALL_CLASS, nh.CHAIN_CLASS,
                                              nh.ROCK_CLASS) or not it.can_be_dropped_from_inventory():
                continue
            w = _words(it)
            if ' cursed ' not in w and ' blessed ' not in w:
                continue
            if it.category == nh.SCROLL_CLASS and power_route.SCARE_SCROLL in it.objs:
                continue
            if self._is_digging_tool(it) or it.is_container():
                continue
            if best is None or it.count < best.count:
                best = it
        if best is not None:
            return [best]
        main = inv.main_hand
        if main is not None and ' blessed ' in _words(main) and main.can_be_dropped_from_inventory() and \
                not self._is_digging_tool(main):
            return [main]
        return []

    # ---- ALTAR_GATHER: A DARK ALTAR GETS WHAT LIES ABOUT THE TOWN ----
    # hypothesis: the temple's altar answers with a flash only for a cursed or blessed object, and only a flash
    # shows that curse status was checked there (the run's scorer counts the flash messages). A hero whose pack
    # holds few things that can be cursed at all -- food and most tools never are (mkobj.c), weapons and armor are
    # in about 2 cases of 10 -- drops everything and sees nothing: of 54 fresh trips of this iteration's early-trip
    # heroes 4 ended at a dark altar with 4 to 6 stacks tested (a key, 3 daggers, a dwarvish cloak, a towel: two
    # objects that could have flashed), 2 of 187 for the parent's later trips. ALTAR_FLASH (third iteration)
    # helps only when something already known to be cursed or blessed is carried. What a player does at a dark
    # altar is fetch more: the town level is strewn with what its dead gnomes, dwarves and orcs dropped (2 to 14
    # object squares in view at the end of 7 of 9 trips looked at). So when the altar has stayed dark the hero
    # walks to the squares of this level she has stood on where weapons, armor, rings, amulets or potions of
    # unknown status lie (never a shop: a square she has stood on in a shop is known as one; never a corpse, a
    # scroll, a gem or a stone; nothing heavier than GATHER_STACK_WEIGHT), carries up to GATHER_BATCH stacks to
    # the altar, drops them and leaves them there. GATHER_TURNS at most, GATHER_ROUNDS drops; nothing hostile in
    # view while fetching. Acts only where the trip had already finished its business.
    # sources: NetHack 3.6.6 src/do.c doaltarobj() (the flash for every blessed or cursed object dropped, "lands
    # on the altar" otherwise) and src/mkobj.c mksobj() (weapons: 1 in 11 blessed-or-enchanted, 1 in 10 of the
    # rest cursed, blessorcurse(otmp, 10) for the others; armor alike; FOOD_CLASS and most TOOL_CLASS objects: no
    # curse state rolled), read at https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/
    # ; https://nethackwiki.com/wiki/Altar ("dropping objects on an altar ... a black flash ... an amber flash";
    # players "drop everything they find on the altar") ; https://nethackwiki.com/wiki/Curse (the generation
    # table by class) ; https://nethackwiki.com/wiki/Minetown (the temple as the place to learn curse status
    # early) ; /refs/history.md #3 (ALTAR_FLASH, and that the scorer counts flashes).
    def _gather_ok(self, it):
        try:
            if it.category not in (nh.WEAPON_CLASS, nh.ARMOR_CLASS, nh.RING_CLASS, nh.AMULET_CLASS,
                                   nh.POTION_CLASS):
                return False
            if _buc_shown(it) or it.is_corpse() or self._is_digging_tool(it):
                return False
            return it.weight() <= GATHER_STACK_WEIGHT
        except Exception:
            return False

    def _gather_fetched(self):
        """What has been fetched and not dropped yet."""
        return [it for it in self.altar_items() if _glyph(it) in self._gather_glyphs]

    def _gather_spots(self, dis):
        agent = self.agent
        level = agent.current_level()
        key = level.key()
        mask = (level.item_count > 0) & level.was_on & ~level.shop & ~level.shop_interior
        out = []
        for y, x in zip(*mask.nonzero()):
            y, x = int(y), int(x)
            if (key, y, x) in self._gather_skip or dis[y, x] == -1 or dis[y, x] > GATHER_DIST:
                continue
            if level.objects[y, x] in G.ALTAR or utils.isin(level.objects[y:y + 1, x:x + 1], G.TRAPS).any():
                continue
            if any(self._gather_ok(it) for it in (level.items[y, x] or ())):
                out.append((int(dis[y, x]), (y, x)))
        return [p for _, p in sorted(out)]

    def _gather_due(self):
        if not jf_config.ALTAR_GATHER or not self.altar_tested or self.pending is not None or self.flashes or \
                self._gather_over or not self.in_town():
            return False
        key = tuple(int(v) for v in self.agent.current_level().key())
        if getattr(self.agent, '_altar_flash_levels', {}).get(key, 0):
            return False
        return not self._flash_due()

    def _gather_job(self, here, dis):
        """('gather', square) | ('more', altar) | None (and the fetching is over)."""
        agent = self.agent
        now = int(agent.blstats.time)
        alts = [p for p in self._altars() if p == here or dis[p] != -1]
        if self._gather_since is None:
            self._gather_since = now
        fetched = self._gather_fetched()
        if alts and now - self._gather_since <= GATHER_TURNS and len(fetched) < GATHER_BATCH and \
                self._gather_weight < GATHER_TOTAL_WEIGHT and self._gather_rounds < GATHER_ROUNDS and \
                not self._hostiles_within(8):
            spots = self._gather_spots(dis)
            if spots:
                return 'gather', spots[0]
        if alts and fetched:
            return 'more', min(alts, key=lambda p: 0 if p == here else dis[p])
        self._gather_over = True
        self.log(f'dark altar: nothing (more) to fetch on this level after {now - self._gather_since} turns, '
                 f'{self._gather_rounds} drops')
        return None

    def _gather(self, pos):
        agent = self.agent
        bl = agent.blstats
        if (int(bl.y), int(bl.x)) != tuple(pos):
            self._walk(pos)
            return
        key = agent.current_level().key()
        self._gather_skip.add((key, int(pos[0]), int(pos[1])))
        inv = agent.inventory
        below = inv.get_items_below_me()
        take, weight = [], self._gather_weight
        for it in below:
            if len(take) >= 4 or not self._gather_ok(it):
                continue
            w = it.weight()
            if weight + w > GATHER_TOTAL_WEIGHT:
                continue
            take.append(it)
            weight += w
        if not take:
            return
        self.log(f'dark altar: fetching {[it.text for it in take]} at {tuple(pos)}')
        for it in take:
            self._gather_glyphs.add(_glyph(it))
        self._gather_weight = weight
        inv.pickup(take)

    def _gather_drop(self, pos):
        agent = self.agent
        bl = agent.blstats
        if (int(bl.y), int(bl.x)) != tuple(pos):
            self._walk(pos)
            return
        items = self._gather_fetched()
        self._gather_rounds += 1
        self._gather_weight = 0
        if self._gather_rounds >= GATHER_ROUNDS:
            self._gather_over = True
        if not items:
            return
        self.altar_drops += 1
        seen = self._flash_count()
        ok = agent.inventory.drop(items)
        self.flashes += self._flash_count() - seen
        self.log(f'dark altar: {len(items)} fetched stacks dropped on it (ok={ok}): {[i.text for i in items][:12]} '
                 f'-> flashes {self.flashes}')

    def _flash_due(self):
        """ALTAR_FLASH: the altar has been used but has not flashed, and something that will flash is carried."""
        if not jf_config.ALTAR_FLASH or not self.altar_tested or self.pending is not None or self.flashes or \
                self._flash_tries >= 2 or not self.in_town():
            return False
        key = tuple(int(v) for v in self.agent.current_level().key())
        if getattr(self.agent, '_altar_flash_levels', {}).get(key, 0):
            return False   # this altar has flashed already (power_route's own test of the potions and scrolls)
        return bool(self._flash_items())

    def _over(self):
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        now = int(bl.time)
        if level.key() != self._level_key:
            self._level_key = level.key()
            self._level_since = now
            if level.dungeon_number == Level.GNOMISH_MINES:
                self._mines_seen = True
            elif self._mines_seen and jf_config.BRANCH_CLOCK_FIX:
                self._branch_since = now   # BRANCH_CLOCK_FIX: thrown back into the Dungeons, the way is known
        if self.in_town() and self._town_since is None:
            self._town_since = now
            self.log(f'in town at turn {now} (trip turn {now - self.start_turn}), XL {bl.experience_level}, '
                     f'gold {bl.gold}, altars {self._altars()}')
        if agent.prayer_failed:
            return 'prayer failed'
        if self.business_done():
            return 'serviced'
        if self.in_town() and self.orcish(level) and not self._orc_go(level):
            return 'Orcish Town'
        if level.dungeon_number not in (Level.DUNGEONS_OF_DOOM, Level.GNOMISH_MINES):
            return 'off the route'
        if now - self.start_turn > TRIP_TOTAL_TURNS:
            return 'budget'
        if self.pending is not None:
            return None
        if level.dungeon_number == Level.DUNGEONS_OF_DOOM:
            if now - max(self.start_turn, self._branch_since) > BRANCH_TURNS:
                return 'branch budget'
        elif self._town_since is not None:
            if now - self._town_since > TOWN_TURNS and (self.altar_tested or self._next_job() is None):
                return 'town budget'
        elif level.level_number <= 4:
            self._note_reach(level, now)
            if now - self._level_since > TRIP_LEVEL_TURNS and not self._second_wind(level, now):
                return 'level budget'   # (below the town the climb is the dive's own way back anyway)
        return None

    def _note_reach(self, level, now):
        """SECOND_WIND: how many squares the path-finder reaches on this level, sampled every 50 turns."""
        if not jf_config.SECOND_WIND:
            return
        log = self._reach_log.setdefault(level.key(), [])
        if log and now - log[-1][0] < 50:
            return
        log.append((now, int((self.agent.bfs() != -1).sum())))

    def _second_wind(self, level, now):
        """SECOND_WIND: the level budget has run out. A trip that stands still ends here, as before; one whose
        level is still opening (new ground in reach over the last WIND_LOOK_BACK turns) with a fit hero gets
        WIND_TURNS more, once per level, and walks them without the explorer's searching
        (exploration_logic.mines_walk). See the fifth-iteration notes at the top."""
        agent = self.agent
        bl = agent.blstats
        key = level.key()
        if not jf_config.SECOND_WIND:
            return False
        if key in self._winds:
            return now <= self._winds[key]   # one per level
        log = self._reach_log.get(key) or []
        past = [r for t, r in log if t <= now - WIND_LOOK_BACK]
        if not past or not log:
            return False
        grown = log[-1][1] - past[-1]
        fit = bl.hitpoints >= WIND_MIN_HP * bl.max_hitpoints and bl.hunger_state < Hunger.WEAK and \
            not agent.prayer_failed and not agent.character.prop.polymorph
        self.log(f'level budget on {key}: reach {past[-1]} -> {log[-1][1]} in the last {WIND_LOOK_BACK} turns, '
                 f'hp {bl.hitpoints}/{bl.max_hitpoints}, hunger {int(bl.hunger_state)}: '
                 f'{"a second wind" if fit and grown >= WIND_GROWTH else "the budget stands"}')
        if not fit or grown < WIND_GROWTH:
            return False
        self._winds[key] = now + WIND_TURNS
        return True

    def _end(self, why):
        agent = self.agent
        gl = agent.global_logic
        bl = agent.blstats
        self.active = False
        self.done = True
        self.end_reason = why
        self.end_turn = int(bl.time)
        self.log(f'trip ends ({why}) after {int(bl.time) - self.start_turn} turns: town={gl.minetown_level}, '
                 f'altar_tested={self.altar_tested} drops={self.altar_drops} flashes={self.flashes}, '
                 f'donations={self.donations} protection={self.protection}, XL {bl.experience_level}, '
                 f'gold {bl.gold}, hp {bl.hitpoints}/{bl.max_hitpoints}, level {agent.current_level().key()}')

    def plan_step(self):
        """One step of the trip inside DiveLogic.plan_step. True: the trip acted (or re-planned); False: the trip
        is over and the dive's own plan goes on."""
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        why = self._over()
        if why is not None:
            self._end(why)
            return False
        level = agent.current_level()
        if self._rest():
            return True
        if level.dungeon_number == Level.DUNGEONS_OF_DOOM:
            return self._to_the_mines()
        key = level.key()
        ln = level.level_number
        town = agent.global_logic.minetown_level
        if self.in_town():
            return self._town_step()
        if ln in (3, 4) and town is None:
            # dungeon.def: minetn @ (3, 2) -- the town is Mines level 3 or 4. A fall (trap doors and dug holes drop
            # 1-3 levels) can land us on either without having seen the other.
            self._judge(level)
            other = (Level.GNOMISH_MINES, 7 - ln)
            if key not in self._filler:
                if other in self._filler:
                    return self._town_step()   # the other one is a filler: this is the town, its signs will show
                return self._look_for_town()
        target = town[1] if town is not None else (4 if ln == 3 else 3 if ln == 4 else None)
        if ln > 4 or (target is not None and ln > target):
            return self._climb()
        dive._task('minetown trip: down the Mines')
        if dive.rest_if_hurt():
            return True
        before = agent.step_count
        if self.unblock(G.STAIR_DOWN):
            if agent.step_count == before:
                agent.search()
            return True
        if self._tunnel_down():
            if agent.step_count == before:
                agent.search()
            return True
        if self._dig_fallback():
            if agent.step_count == before:
                agent.search()
            return True
        self._descend_step()
        if agent.step_count == before:
            agent.search()
        return True

    def _descend_step(self):
        """Stairs down one Mines level: walk to a reachable '>', else work at a '>' that is in view but cut off (a
        peaceful on it, a boulder), else explore until one is in reach. (Not DiveLogic.mines_step: its give-up clock
        counts from the first visit of the level, which may lie thousands of turns back in the grind.)"""
        dive = self.dive
        agent = self.agent
        level = agent.current_level()
        dis = agent.bfs()
        seen = dive._stairs_down(level)
        downs = [p for p in seen if dis[p] != -1]
        if downs:
            y, x = min(downs, key=lambda p: dis[p])
            if (agent.blstats.y, agent.blstats.x) != (y, x):
                agent.go_to(y, x)
                return
            if dive.rest_if_hurt():
                return
            agent.move('>')
            return
        if seen and dive._take_stairs(seen, '>'):
            return
        reachable = lambda: any(agent.bfs()[p] != -1 for p in dive._stairs_down(agent.current_level()))
        if not dive.exploration(0).until(agent, dive._budgeted(reachable)).run(return_condition=True):
            dive.exploration(None).until(agent, dive._budgeted(reachable)).run()

    def passing(self):
        """After a trip that ended without the altar (a budget, a fall past the town), the dive's own way back up
        still leads through the town: with its altar in reach, the test is done in passing (no searching for it)."""
        agent = self.agent
        dive = self.dive
        level = agent.current_level()
        if not self.done or self.start_turn is None or \
                (self.altar_tested and self.pending is None and not self._flash_due()):
            return False
        if self.end_reason in ('serviced', 'Orcish Town', 'not started', 'prayer failed') or agent.prayer_failed:
            return False
        if level.dungeon_number != Level.GNOMISH_MINES or level.level_number not in (3, 4) or self.orcish(level):
            return False
        if agent.get_visible_monsters():
            return False
        job = self._next_job()
        if job is None or job[0] not in ('altar', 'pickup', 'flash'):
            return False
        kind, target = job
        before = agent.step_count
        dive._task(f'minetown (passing): {kind}')
        if kind == 'pickup':
            self._pickup(target)
        elif kind == 'flash':
            self._flash(target)
        else:
            self._altar(target)
        if self.altar_tested and self.pending is None and not self._flash_due():
            self.end_reason = 'serviced'
            self.log('altar test done in passing: serviced')
        if agent.step_count == before:
            agent.search()
        return True

    def _climb(self):
        """Below the town (a fall took us past it): up the stairs, as the dive's own way back does."""
        dive = self.dive
        agent = self.agent
        dive._task('minetown trip: back up to the town')
        before = agent.step_count
        if self.tunnel_up() or self.unblock(G.STAIR_UP):
            if agent.step_count == before:
                agent.search()
            return True
        dive.return_to_main_dungeon()
        if agent.step_count == before:
            agent.search()
        return True

    def _kick_out(self):
        """TRIP_KICK_OUT: shut in behind a locked door on the town level. The town maps built from rooms (Town
        Square, Alley Town, College Town) put each staircase in a room of its own, joined to the town through doors
        that may be locked, and explore1 never kicks a door in the Mines (the Watch): the trip searched the stair
        room's walls until its town budget ran out. The Watch only minds a door kicked where a watchman sees it
        (dokick.c: is_watchman && couldsee), so: only a stair room and its surroundings are in reach (KICK_OUT_REACH
        squares; the town is ~450), a closed door next to them did not open, nobody of the town is in view, we are
        not in a shop -- kick it. (Ported from /refs/history #6, where it was one part of a larger change.)"""
        agent = self.agent
        dive = self.dive
        bl = agent.blstats
        level = agent.current_level()
        now = int(bl.time)
        if level.dungeon_number != Level.GNOMISH_MINES or now < getattr(agent, '_no_kick_until', -1):
            return False
        y0, x0 = int(bl.y), int(bl.x)
        if level.shop[y0, x0] or level.shop_interior[y0, x0]:
            return False
        prop = agent.character.prop
        if prop.polymorph or prop.blind or prop.hallu or prop.confusion or prop.stun:
            return False
        if utils.isin(agent.glyphs, dive._town_glyphs()).any():
            return False
        dis = agent.bfs()
        reach = int((dis != -1).sum())
        if reach > KICK_OUT_REACH:
            return False
        best = None
        for y, x in zip(*utils.isin(agent.glyphs, G.DOOR_CLOSED).nonzero()):
            y, x = int(y), int(x)
            if level.door_open_count[y, x] < 1 or self._kicks.get((level.key(), (y, x)), 0) >= KICK_OUT_TRIES:
                continue
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < dis.shape[0] and 0 <= nx < dis.shape[1] and dis[ny, nx] != -1 and \
                        (best is None or dis[ny, nx] < best[0]):
                    best = (int(dis[ny, nx]), (ny, nx), (y, x))
        if best is None:
            return False
        _, spot, door = best
        dive._task('minetown trip: kick the locked door')
        before = agent.step_count
        if (y0, x0) != spot:
            agent.go_to(*spot, max_steps=10, callback=lambda: bool(self._hostiles_within(2)))
            if agent.step_count == before:
                agent.search()
            return True
        if self._hostiles_within(2):
            return False
        k = (level.key(), door)
        sign = ''.join(c for c in (agent.inventory.engraving_below_me or '').lower() if c.isalpha())
        if sign and sign != 'elbereth':
            # "Closed for inventory" lies in front of a shut shop (worn or not): its keeper kills for a broken door
            self._kicks[k] = KICK_OUT_TRIES
            self.log(f'door at {door}: a sign {sign!r} lies before it, not kicked')
            return False
        self._kicks[k] = self._kicks.get(k, 0) + 1
        if self._kicks[k] == 1:
            self.log(f'shut in ({reach} squares in reach) behind the door at {door}: kicking it')
        agent.kick(*door)
        if agent.glyphs[door] not in G.DOOR_CLOSED:
            self.log(f'door at {door} is open after {self._kicks[k]} kicks: {(agent.message or "")[:80]!r}')
        agent.last_bfs_step = -1
        if agent.step_count == before:
            agent.search()
        return True

    def unblock(self, stairs):
        """A Mines level whose wanted staircase (G.STAIR_DOWN / G.STAIR_UP) has stayed out of reach: the two things
        that hide a way on from AutoAscend's BFS. (1) A diagonal step between two rock corners needs an inventory of
        600 or less (hack.c test_move / cant_squeeze_thru), and the Mines' caves are full of them: when squeezing
        would reach more of the level, drop to 550 (agent.unsqueeze's cap). (2) Every known trap is a wall to the BFS:
        walk through the safe kinds (never a trap door or hole, never the polymorph/fire/sleep/magic kinds). Used by
        the trip on its way down and back up, and by the dive's own return to the main dungeon after the trip."""
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        key = level.key()
        now = int(bl.time)
        if level.dungeon_number != Level.GNOMISH_MINES or dive.turns_on_level() < UNBLOCK_AFTER_TURNS:
            return False
        if now - self._unblock_turn.get(key, -10 ** 9) < 80:
            return False
        dis = agent.bfs()
        if any(dis[p] != -1 for p in zip(*utils.isin(level.objects, stairs).nonzero())):
            return False
        self._unblock_turn[key] = now
        reach = int((dis != -1).sum())
        items = agent.inventory.items
        if items.total_weight > 600 and now >= getattr(agent, '_squeeze_cap_until', -1):
            wide = int((agent.bfs(force_squeeze=True) != -1).sum())
            agent.last_bfs_step = -1
            tool = dive.digging_tool()
            essential = sum(i.weight() for i in items.all_items if i.equipped or i is tool)
            if wide >= reach + 15 and essential <= 540:
                self.log(f'unblock on {key}: carrying {items.total_weight:.0f}, a squeeze reaches {wide} squares '
                         f'instead of {reach}: dropping to 550')
                agent._squeeze_cap_until = now + 400
                agent.inventory.arrange_items().run()
                agent.inventory.unreachable_items_until[agent.inventory._here()] = now + 5000
                return True
        if dive.turns_on_level() >= TRAPS_AFTER_TURNS and utils.isin(level.objects, G.TRAPS).any() and \
                agent._last_turn - agent._allow_walking_through_traps_turn > 50:
            self.log(f'unblock on {key}: {reach} squares in reach, walking through the safe known traps')
            dive._walk_through_traps(climbing=True)
            return True
        return False

    def _orc_altar_reach(self):
        agent = self.agent
        dis = agent.bfs()
        here = (int(agent.blstats.y), int(agent.blstats.x))
        return any(p == here or dis[p] != -1 for p in self._altars())

    def _orc_go(self, level):
        """ORCISH_ALTAR: is Orcish Town's altar worth going for? (See the fifth-iteration notes at the top.)"""
        agent = self.agent
        bl = agent.blstats
        if not jf_config.ORCISH_ALTAR:
            return False
        if self.pending is not None:
            return True   # our things lie on the altar
        now = int(bl.time)
        if self._orc_since is None:
            self._orc_since = now
        if now - self._orc_since > ORC_TURNS:
            return False
        if self._orc_altar_reach():
            return True   # the wall is open already (a dwarf dug through it): the altar is a walk away
        tool = self.dive.digging_tool()
        if self._orc_ok is None:
            last = agent.last_prayer_turn
            self._orc_ok = tool is not None and bl.experience_level >= max(ORC_MIN_XL, int(bl.depth)) and \
                bl.armor_class <= ORC_MAX_AC and not agent.character.prop.polymorph and \
                bl.hunger_state < Hunger.WEAK and (last is None or now - last >= ORC_PRAYER_GAP)
            self.log(f'Orcish Town: tool {None if tool is None else tool.text!r}, XL {bl.experience_level}, '
                     f'AC {bl.armor_class}, hp {bl.hitpoints}/{bl.max_hitpoints}, hunger {int(bl.hunger_state)}, '
                     f'last prayer {None if last is None else now - last} turns ago: '
                     f'{"breaching the wall for the altar" if self._orc_ok else "left alone"}')
        return self._orc_ok and tool is not None and bl.hunger_state < Hunger.WEAK

    def _orc_step(self):
        """ORCISH_ALTAR: one step of the walk-and-dig route to Orcish Town's altar (its place is known from the
        map before it is seen). False: nothing done here (no tool, or the tunnel has no route)."""
        agent = self.agent
        dive = self.dive
        level = agent.current_level()
        if not jf_config.ORCISH_ALTAR or not self.orcish(level) or dive.digging_tool() is None:
            return False
        near = 3
        if self._active_hostiles_within(3):
            # what comes for us is fought first, at the breach (the fight strategy does that); what only stands
            # off behind the wall or the bars is not waited for for ever
            self._orc_wait += 1
            if self._orc_wait <= ORC_WAIT or self._active_hostiles_within(1):
                dive._task('minetown trip: Orcish Town, the fight first')
                agent.search(1)
                return True
            near = 1
        else:
            self._orc_wait = 0
        seen = self._altars()
        targets = seen if seen else [ORC_ALTAR]
        bl = agent.blstats
        y0, y1, x0, x1 = ORC_RECT
        overlay = None
        if not (y0 <= bl.y <= y1 and x0 <= bl.x <= x1):
            gap = ORC_ENTRY[0]
            if not self._orc_held and level.walkable[gap] and (int(bl.y), int(bl.x)) == (gap[0] + 1, gap[1]):
                # the wall is open and we stand outside in front of it: what comes out comes one at a time, and
                # only the lane square behind the gap has a line of fire to us -- the breach is held here until
                # the town has stopped sending orcs (then _rest brings the HP back before the walk in)
                now = int(bl.time)
                if self._orc_hold is None:
                    self._orc_hold = [now, now]
                    self.log(f'Orcish Town: the wall is open at {gap}, holding the breach from outside')
                if self._active_hostiles_within(100):
                    self._orc_hold[1] = now
                if now - self._orc_hold[1] < ORC_HOLD_QUIET and now - self._orc_hold[0] < ORC_HOLD_MAX:
                    dive._task('minetown trip: Orcish Town, holding the breach')
                    agent.search(1)
                    return True
                self._orc_held = True
                self.log(f'Orcish Town: breach held for {now - self._orc_hold[0]} turns, hp '
                         f'{bl.hitpoints}/{bl.max_hitpoints}: going in')
                if bl.hitpoints < REST_BELOW * bl.max_hitpoints:
                    return True   # plan_step's rest comes first
            # outside the wall: the route is the one a player would take with the map in her head -- round the town
            # on the strip of floor outside the wall to the point south of the temple, in through the wall there
            # (two walls and four steps to the altar; the west and east sides are 15 squares of shops and orcs)
            extra = np.zeros(level.walkable.shape, dtype=bool)
            extra[y0 - 1, x0 - 1:x1 + 2] = True
            extra[y1 + 1, x0 - 1:x1 + 2] = True
            extra[y0 - 1:y1 + 2, x0 - 1] = True
            extra[y0 - 1:y1 + 2, x1 + 1] = True
            forbid = np.zeros(level.walkable.shape, dtype=bool)
            forbid[y0:y1 + 1, x0:x1 + 1] = True
            for p in ORC_ENTRY + (ORC_ALTAR,):
                forbid[p] = False
            for p in (ORC_ENTRY[1], ORC_ENTRY[3], ORC_ALTAR):
                extra[p] = True
            overlay = (extra, forbid)
        return self._tunnel_step(targets, 'the altar of Orcish Town', town=True, near=near, overlay=overlay)

    def post_hold(self):
        """Back in the main dungeon after the trip: the dive proper starts with an emergency prayer in hand, as the
        grind's DIVE_PRAYER_GAP hold arranged before the trip (the trip's hunger and HP prayers reset the timeout:
        dev seed 386144 prayed 158 turns before its first hole and died on Dlvl 11 with no prayer to answer). Rest on
        an Elbereth until POST_HOLD_GAP turns have passed since the last prayer, POST_HOLD_MAX at most."""
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        if self._hold_over or not self.done or self.start_turn is None or not jf_config.MINETOWN_TRIP:
            self.holding = False
            return False
        now = int(bl.time)
        last = agent.last_prayer_turn
        over = None
        if level.dungeon_number != Level.DUNGEONS_OF_DOOM or bl.depth > 4:
            over = 'off the upper levels'
        elif agent.prayer_failed or dive.digging_tool() is None:
            over = 'no prayer / no tool'
        elif last is None or now - last >= POST_HOLD_GAP:
            over = f'prayer gap {None if last is None else now - last}'
        elif self._hold_start is not None and now - self._hold_start > POST_HOLD_MAX:
            over = 'max wait'
        elif bl.hunger_state >= Hunger.WEAK:
            over = 'weak'
        if over is not None:
            if self._hold_start is not None or self.end_reason == 'serviced':
                self.log(f'post-trip hold over ({over}) after '
                         f'{0 if self._hold_start is None else now - self._hold_start} turns')
            self._hold_over = True
            self.holding = False
            return False
        if self._hold_start is None:
            self._hold_start = now
            self.log(f'post-trip hold: {now - last} turns since the last prayer, waiting for {POST_HOLD_GAP}')
        self.holding = True
        dive._task('minetown trip: prayer hold before the dive')
        before = agent.step_count
        if agent.get_visible_monsters():
            agent.search(1)
            return True
        try:
            if dive._rest_elbereth():
                return True
        except Exception:
            if agent.step_count != before:
                raise
        agent.search(20)
        return True

    def _look_for_town(self):
        """Mines level 3 or 4, undecided: look at the level's middle (the town map is centred) before taking any
        way off it."""
        dive = self.dive
        agent = self.agent
        level = agent.current_level()
        key = level.key()
        dive._task('minetown trip: is this the town?')
        before = agent.step_count
        decided = lambda: self.is_town_level(agent.current_level()) or \
            self._middle_seen(agent.current_level()) >= MIDDLE_SEEN or agent.current_level().key() != key
        explored = dive.exploration(0).until(agent, dive._budgeted(decided)).run(return_condition=True)
        if not explored and agent.current_level().key() == key and not decided():
            self._filler.add(key)
            self.log(f'{key} is a filler level (explored, no town sign)')
        if agent.step_count == before:
            agent.search()
        return True

    CROWD_REST_BELOW = 0.6

    def crowd_alert(self):
        """During the trip and on the way back from it, in the Mines: two or more hostiles within two squares. The
        dive's Elbereth rest waits for 40% HP (or a fast loss), which is the right call against one monster deep
        down; against the Mines' packs (soldier ants, killer bees, giant ants, wolves, hill orcs: 2-4 attackers, most
        of them faster than the hero) 40% of 65 HP is two rounds from death and the engraving itself costs one:
        the trip's deaths on the way down came from exactly these packs (dev seeds 2, 67292, 23099: 'ELBERETH rest
        start' at 23/66 with four attackers around). With a pack next to her she writes at 60% instead. All of them
        respect the engraving (only @ and minotaurs do not; the rest's own checks still skip those)."""
        agent = self.agent
        if self.start_turn is None or not jf_config.MINETOWN_TRIP:
            return False
        if agent.current_level().dungeon_number != Level.GNOMISH_MINES:
            return False
        return len(self.dive._near_hostiles(2)) >= 2

    def escape_dig_due(self):
        """dig_first's question during the trip: above the town (Mines level 1-2, a hole from there lands on the town
        level or the filler above it), at or below ESCAPE_HP with something hostile next to us and a digging tool --
        the fight is being lost, the hole is the way out (and the way on)."""
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        if not self.active or level.dungeon_number != Level.GNOMISH_MINES or level.level_number > 2:
            return False
        if bl.hitpoints > ESCAPE_HP * bl.max_hitpoints or level.key() in dive.undiggable:
            return False
        if agent.character.prop.polymorph or not self._hostiles_within(2):
            return False
        y, x = int(bl.y), int(bl.x)
        if dive.digging_tool() is None or not dive._diggable_spot(y, x) or (y, x) in level.stair_destination:
            return False
        return True

    def escape_dig(self):
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        self._escapes += 1
        self.log(f'escape dig at hp {bl.hitpoints}/{bl.max_hitpoints} on {agent.current_level().key()}, hostiles '
                 f'{[(m[3].mname, int(m[0])) for m in agent.get_visible_monsters()[:4]]}')
        dive.dig_with_tool(dive.digging_tool())

    def _wear(self):
        """The altar has shown what is cursed: put on the best armor carried that is not (the tour's
        wear_best_stuff, which the dive never runs)."""
        agent = self.agent
        if self._hostiles_within(6) or agent.character.prop.polymorph:
            return
        if int(agent.blstats.time) - self._wear_turn < 20:
            return
        self._wear_turn = int(agent.blstats.time)
        ac = int(agent.blstats.armor_class)
        agent.inventory.wear_best_stuff().run()
        if int(agent.blstats.armor_class) != ac:
            self.log(f'armor put on: AC {ac} -> {int(agent.blstats.armor_class)}')

    def _rest(self):
        """The trip is a walk among the Mines' packs: below REST_BELOW of max HP with nothing hostile in view it
        waits (on an Elbereth where one can be written) instead of walking on into the next fight."""
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        if bl.hitpoints >= REST_BELOW * bl.max_hitpoints or bl.hunger_state >= Hunger.WEAK:
            return False
        if agent.get_visible_monsters() or dive.starving():
            return False
        dive._task('minetown trip: rest')
        before = agent.step_count
        try:
            if dive._rest_elbereth():
                return True
        except Exception:
            if agent.step_count != before:
                raise
        agent.search(10)
        return True

    def _dig_fallback(self):
        """A Mines level above the town whose '>' has stayed out of reach for DIG_AFTER_TURNS (a diagonal squeeze the
        pack is too heavy for, a trap in the only passage, a boulder): the pick-axe makes the way down. Never on the
        town level (plan_step sends that to _town_step), never without a tool."""
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        if not DIG_AFTER_TURNS or int(bl.time) - self._level_since < DIG_AFTER_TURNS or \
                level.key() in dive.undiggable:
            return False
        tool = dive.digging_tool()
        if tool is None or agent.character.prop.polymorph:
            return False
        dis = agent.bfs()
        if any(dis[p] != -1 for p in dive._stairs_down(level)):
            return False
        y, x = int(bl.y), int(bl.x)
        if not dive._diggable_spot(y, x) or (y, x) in level.stair_destination:
            spots = [(dis[p], p) for p in zip(*(dis > 0).nonzero()) if dive._diggable_spot(*p) and
                     p not in level.stair_destination]
            if not spots:
                return False
            dive._task('minetown trip: to a dig spot')
            agent.go_to(*min(spots)[1])
            return True
        dive._task('minetown trip: dig down (stairs cut off)')
        if self._hostiles_within(2):
            return False   # the fight first
        if ('hole', level.key()) not in self._tunnel_logged:
            self._tunnel_logged.add(('hole', level.key()))
            self.holes += 1
            self.log(f"the '>' of {level.key()} is still cut off after {int(bl.time) - self._level_since} turns: "
                     f'digging down with {tool.text!r}')
        dive.dig_with_tool(tool)
        return True

    # ------------------------------------------------------------------ PICK_TUNNEL

    def _tunnel_masks(self):
        """(walk, dig): the squares a tunnel route may walk over, and those it may dig into (rock, cave wall, a
        boulder). Known traps are neither (the tunnel goes round them); the map's outer ring does not dig."""
        agent = self.agent
        level = agent.current_level()
        key = level.key()
        boulders = utils.isin(agent.glyphs, G.BOULDER)
        traps = utils.isin(level.objects, G.TRAPS)
        mons = agent.monster_tracker.monster_mask | agent.monster_tracker.peaceful_monster_mask
        walk = level.walkable & ~boulders & ~traps & ~level.forbidden & ~agent.monster_tracker.peaceful_monster_mask
        dig = (~level.walkable | boulders) & ~traps & ~mons
        dig &= ~utils.isin(level.objects, G.BARS, G.TREE, G.DOORS, agent._wet_glyphs)
        inner = np.zeros_like(dig)
        inner[2:20, 1:78] = True
        dig &= inner
        for k, y, x in self._tunnel_blocked:
            if k == key:
                dig[y, x] = False
                walk[y, x] = False
        return walk, dig

    def _tunnel_route(self, targets, overlay=None, skip_passive=False):
        """The cheapest way from here to the nearest of `targets`, walking over open squares (1 a step; no
        diagonal between two rock corners: hack.c test_move, it needs 600 or less carried) and digging into rock
        (TUNNEL_DIG_COST a square, orthogonally only -- a dug square is entered straight). Returns (path, walk
        mask) or None."""
        agent = self.agent
        bl = agent.blstats
        walk, dig = self._tunnel_masks()
        if skip_passive:
            walk = walk & ~self._passive_mask()   # ORCISH_ALTAR: round a floating eye, never into it
        if overlay is not None:
            # ORCISH_ALTAR: floor known from the level's map though not yet seen, and squares the route keeps off
            extra, forbid = overlay
            level = agent.current_level()
            unseen = extra & ~level.seen & dig
            walk = (walk | unseen) & ~forbid
            dig = dig & ~unseen & ~forbid
        start = (int(bl.y), int(bl.x))
        targets = set((int(y), int(x)) for y, x in targets) - {start}
        if not targets:
            return None
        height, width = walk.shape
        dist = {start: 0}
        prev = {}
        heap = [(0, start)]
        found = None
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist.get(u, 10 ** 9):
                continue
            if u in targets:
                found = u
                break
            uy, ux = u
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if not dy and not dx:
                        continue
                    vy, vx = uy + dy, ux + dx
                    if not (0 <= vy < height and 0 <= vx < width):
                        continue
                    if walk[vy, vx]:
                        if dy and dx and not (walk[uy, vx] or walk[vy, ux]):
                            continue
                        c = 1
                    elif dig[vy, vx] and not (dy and dx):
                        c = TUNNEL_DIG_COST
                    else:
                        continue
                    if d + c < dist.get((vy, vx), 10 ** 9):
                        dist[(vy, vx)] = d + c
                        prev[(vy, vx)] = u
                        heapq.heappush(heap, (d + c, (vy, vx)))
        if found is None:
            return None
        path = [found]
        while path[-1] != start:
            path.append(prev[path[-1]])
        path.reverse()
        return path, walk

    def _tunnel_step(self, targets, what, town=False, near=3, overlay=None):
        """PICK_TUNNEL: one step of a walk-and-dig route to the nearest of `targets` with the carried pick-axe or
        mattock (the way back up from the temple: tunnel_up). True: the tunnel acted."""
        # hypothesis: the way back from the temple is where the trip stalls without anything to gain: on 26% of the
        # development trips it took more than 500 turns (the median is 150) and on some 4000+, the hero standing on
        # a filler level whose '<' she knows -- she came down by it -- but cannot walk to, because a trap door, an
        # escape hole or a squeeze she no longer fits through had put her on the far side of a trap, a boulder or a
        # diagonal gap that AutoAscend's BFS takes for a wall. Every such turn is a turn among the Mines' packs with
        # the hunger clock running (the prayer is the trip's food and its lifeline). Two heroes in three carry a
        # pick-axe or mattock there, and the Mines' rock and cave walls all dig (about seven turns a square for a
        # St 18 Valkyrie; only Minetown's and Mines' End's walls do not): once the known '<' has stayed out of reach
        # for TUNNEL_UP_AFTER_TURNS she walks and digs the cheapest route straight to it (round the trap, through the
        # rock, through the boulder); with no '<' known for TUNNEL_AFTER_TURNS she tunnels to known floor she cannot
        # walk to and looks on from there. Never on the town level (the Watch minds digging there), never toward a
        # monster (a pick applied at one attacks it), never with a hostile within three squares.
        # Measured (parent -> this, same seeds; the tunnel fired in 14 of 70 development trips and 11 of 48
        # held-out ones): turns from the end of the trip to the main dungeon, summed over the trips that got back
        # in both runs: 32496 -> 22926 on the development games, 65178 -> 41472 on the held-out block; with the
        # '<' known the tunnel was faster in 13 trips of 14 (4308 -> 264, 2281 -> 479, 1597 -> 291 turns).
        # (The same tunnel on the way DOWN is TUNNEL_DOWN_AFTER, switched on in the fourth iteration; the dug hole,
        # DIG_AFTER_TURNS, stays off.)
        # sources: NetHack 3.6.6 src/dig.c (dig(): effort += 10 + rn2(5) + abon + uwep->spe - greatest erosion +
        # udaminc + dbon, doubled for dwarves; rock and walls give way at effort > 100 -- "you succeed in cutting
        # away some rock", on a cavernous level outside a town a dug wall becomes a corridor; a boulder "falls apart";
        # "the <wall> here is too hard to dig in" for W_NONDIGGABLE; use_pick_axe2: a monster on the square is
        # attacked instead; watch_dig: only walls and doors in_town() are the Watch's business) and src/hack.c
        # (test_move: "You are carrying too much to get through" above 600) ;
        # https://nethackwiki.com/wiki/Pick-axe ("tunnel through solid rock walls ... smash apart boulders"; the
        # Watch "will warn a hero that they see trying to dig through doors or walls") ;
        # https://nethackwiki.com/wiki/Staircase ("It is usually a good idea to locate the up staircase before
        # proceeding further"; a boulder may cover the way; the pick-axe as the last resort when a staircase stays
        # out of reach) ; https://nethackwiki.com/wiki/Gnomish_Mines (filler levels are "simple caverns" with 6
        # random traps: "the mines are loaded with them"; "trap doors can cut you off from your ... escape path") ;
        # player discussions: https://nethackwiki.com/wiki/Talk:Minetown ("I fell through a trapdoor to the
        # 'Bustling town' but I couldn't find the stairs up") and
        # https://groups.google.com/g/rec.games.roguelike.nethack/c/AQkz3Jm1NZU ("stuck in gnomish mines": the way
        # out is back up; only Mines' End refuses the pick) ; the task brief ("digging sideways is a good tactic") ;
        # /refs/history.md #2 (its replays named the same walls -- squeezes, traps, boulders -- on the way down and
        # walked the unsafe traps; discarded on the held-out seeds. This change leaves the way down alone.) ;
        # /refs/top/README.md (the 54 top programs are dive-first engines of this lineage: none goes to Minetown).
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        key = level.key()
        if not jf_config.PICK_TUNNEL or level.dungeon_number != Level.GNOMISH_MINES or \
                (self.is_town_level(level) and not (town and self.orcish(level))):
            return False   # (Orcish Town has no Watch: ORCISH_ALTAR digs there)
        tool = dive.digging_tool()
        if tool is None or agent.character.prop.polymorph or int(bl.time) < dive._dig_blocked_until:
            return False
        prop = agent.character.prop
        if prop.stun or prop.confusion or prop.hallu or prop.blind:
            return False
        if self._tunnel_digs.get(key, 0) >= TUNNEL_MAX_DIGS or \
                (self._active_hostiles_within(near) if town else self._hostiles_within(near)):
            return False
        if int(bl.time) < self._tunnel_quiet.get(key, -1):
            return False
        route = self._tunnel_route(targets, overlay, skip_passive=town)
        if route is None:
            self._tunnel_quiet[key] = int(bl.time) + 15   # nothing to tunnel to right now: not asked every step
            return False
        path, walk = route
        digs = [p for p in path[1:] if not walk[p]]
        if len(digs) > TUNNEL_MAX_DIGS - self._tunnel_digs.get(key, 0):
            return False
        here, nxt = path[0], path[1]
        dive._task(f'minetown trip: tunnel to {what}')
        if (key, what) not in self._tunnel_logged:
            self._tunnel_logged.add((key, what))
            self.log(f'tunnel on {key} to {what} at {path[-1]}: {len(path) - 1} steps, {len(digs)} squares to dig '
                     f'{digs[:12]}, from {here}, with {tool.text!r}')
        tkey = (key, nxt[0], nxt[1])
        if not walk[nxt]:
            tries = self._tunnel_tries.get(tkey, 0) + 1
            self._tunnel_tries[tkey] = tries
            if tries == 1:
                self._tunnel_digs[key] = self._tunnel_digs.get(key, 0) + 1
            if tries > TUNNEL_SQUARE_TRIES:
                self.log(f'tunnel: {nxt} on {key} does not give way: closed')
                self._tunnel_blocked.add(tkey)
                agent.search()
                return True
            before = agent.step_count
            dive.dig_toward(tool, *nxt)
            msg = agent.message or ''
            if 'too hard to' in msg or 'cannot reach' in msg or 'Clash!' in msg:
                self.log(f'tunnel: {nxt} on {key} is too hard to dig: {msg[:80]!r}')
                self._tunnel_blocked.add(tkey)
            elif 'thin air' in msg:
                level.walkable[nxt] = True
                agent.last_bfs_step = -1
            if agent.step_count == before:
                agent.search()
            return True
        # walk: up to the last open square before the next rock
        k = next((i for i, p in enumerate(path) if i and not walk[p]), len(path))
        goal = path[k - 1]
        dis = agent.bfs()
        if goal != here and dis[goal] != -1:
            agent.go_to(*goal, max_steps=12, callback=lambda: bool(self._hostiles_within(3)))
            return True
        # the bot's own BFS does not know this step (a freshly dug square, a squeeze it misjudges): one step by hand
        tries = self._tunnel_tries.get(tkey, 0) + 1
        self._tunnel_tries[tkey] = tries
        if tries > TUNNEL_SQUARE_TRIES or agent.monster_tracker.monster_mask[nxt]:
            if tries > TUNNEL_SQUARE_TRIES:
                self._tunnel_blocked.add(tkey)
            agent.search()
            return True
        agent.move(*nxt)
        return True

    def _cut_off_floor(self):
        """Known open squares of this level that the BFS cannot reach from here."""
        agent = self.agent
        level = agent.current_level()
        dis = agent.bfs()
        walk, _ = self._tunnel_masks()
        cut = walk & level.seen & (dis == -1)
        cut[int(agent.blstats.y), int(agent.blstats.x)] = False
        return list(zip(*cut.nonzero()))

    def _tunnel_down(self):
        """The way down: the '>' has stayed out of reach for TUNNEL_DOWN_AFTER turns -- tunnel to known floor that
        cannot be walked to (see _tunnel_step and the fourth-iteration notes at the top)."""
        agent = self.agent
        level = agent.current_level()
        if not jf_config.PICK_TUNNEL or not TUNNEL_DOWN_AFTER or \
                int(agent.blstats.time) - self._level_since < TUNNEL_DOWN_AFTER:
            return False
        dis = agent.bfs()
        if any(dis[p] != -1 for p in self.dive._stairs_down(level)):
            return False
        cut = self._cut_off_floor()
        if not cut:
            return False
        return self._tunnel_step(cut, 'cut-off floor')

    def _known_ups(self, level):
        """The level's '<' squares: those on the map and those known from the stairs we came down by."""
        ups = set((int(y), int(x)) for y, x in zip(*utils.isin(level.objects, G.STAIR_UP).nonzero()))
        here = level.level_number
        for p, d in level.stair_destination.items():
            if d is None:
                continue
            if (d[0][0] == level.dungeon_number and d[0][1] == here - 1) or \
                    (here == 1 and d[0][0] == Level.DUNGEONS_OF_DOOM):
                ups.add((int(p[0]), int(p[1])))
        return ups

    def tunnel_up(self):
        """The way back up (during the trip and after it): the known '<' of a filler level is out of reach from
        where we arrived (a hole had taken us past the obstacle) -- tunnel straight to it; no '<' known for long:
        tunnel to cut-off floor. See _tunnel_step."""
        agent = self.agent
        level = agent.current_level()
        key = level.key()
        now = int(agent.blstats.time)
        if not jf_config.PICK_TUNNEL or self.start_turn is None or level.dungeon_number != Level.GNOMISH_MINES:
            return False
        if key != self._up_key:
            self._up_key = key
            self._up_since = now
        if self.is_town_level(level) or self.dive.digging_tool() is None:
            return False
        dis = agent.bfs()
        ups = self._known_ups(level)
        here = (int(agent.blstats.y), int(agent.blstats.x))
        if ups:
            if here in ups or any(dis[p] != -1 for p in ups) or now - self._up_since < TUNNEL_UP_AFTER_TURNS:
                return False
            return self._tunnel_step(ups, "the '<'")
        if now - self._up_since < TUNNEL_AFTER_TURNS:
            return False
        cut = self._cut_off_floor()
        if not cut:
            return False
        return self._tunnel_step(cut, 'cut-off floor')

    def _to_the_mines(self):
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        from . import dive_logic
        dive._task('minetown trip: to the Mines')
        before = agent.step_count
        if dive.go_to_mines():
            if agent.step_count == before:
                agent.search()
            return True
        if dive.mines_done:
            self._end('no Mines branch')
            return False
        if bl.depth > dive_logic.MINES_BRANCH_MAX_DEPTH:
            if dive._climb_back_for_branch():
                return True
            self._end('no Mines branch above')
            return False
        # this level has no branch: on down the main stairs to the next candidate (Dlvl 2-4)
        downs = [p for p in dive._stairs_down(level) if dive._stairs_ok(level, *p)]
        if downs and dive._take_stairs(downs, '>'):
            return True
        reach = lambda: any(agent.bfs()[p] != -1 for p in dive._stairs_down(agent.current_level()))
        dive.exploration(None).until(agent, dive._budgeted(reach)).run()
        if agent.step_count == before:
            agent.search()
        return True

    def _town_step(self):
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        before = agent.step_count
        job = self._next_job()
        if job is not None:
            kind, target = job
            dive._task(f'minetown trip: {kind}')
            if kind == 'pickup':
                self._pickup(target)
            elif kind == 'altar':
                self._altar(target)
            elif kind == 'flash':
                self._flash(target)
            elif kind == 'gather':
                self._gather(target)
            elif kind == 'more':
                self._gather_drop(target)
            elif kind == 'priest':
                self._donate(target)
            else:
                self._wait_for_priest(target)
            if agent.step_count == before:
                agent.search()
            return True
        if self.business_done():
            self._end('serviced')
            return False
        if self.altar_tested and self.pending is None:
            # gold for the priest, but no priest to be found
            self._priest_off = True
            return True
        here = (int(bl.y), int(bl.x))
        dis = agent.bfs()
        targets = [self.pending[0]] if self.pending is not None else self._altars()
        if targets:
            # the altar is known but cut off: a peaceful stands on it or in the doorway -- wait next to it
            near = [(dive._neighbour_distance(dis, *p), p) for p in targets]
            near = [(d, p) for d, p in near if d is not None]
            if near:
                d, p = min(near)
                dive._task('minetown trip: wait at the altar')
                if not utils.adjacent(here, p):
                    self._walk(p, one_before=True)
                else:
                    agent.search(2)
                if agent.step_count == before:
                    agent.search()
                return True
        if self._orc_step():
            if agent.step_count == before:
                agent.search()
            return True
        if jf_config.TRIP_KICK_OUT and self._town_since is not None and \
                int(bl.time) - self._town_since >= KICK_OUT_AFTER and self._kick_out():
            return True
        dive._task('minetown trip: find the temple')
        found = lambda: any(agent.bfs()[p] != -1 or dive._neighbour_distance(agent.bfs(), *p) is not None
                            for p in self._altars())
        if not dive.exploration(0).until(agent, dive._budgeted(found)).run(return_condition=True):
            dive.exploration(None).until(agent, dive._budgeted(found)).run()
        if agent.step_count == before:
            agent.search()
        return True

    # ------------------------------------------------------------------ the town's business

    def _next_job(self):
        """('pickup' | 'altar' | 'flash' | 'priest' | 'wait', target) or None."""
        agent = self.agent
        bl = agent.blstats
        prop = agent.character.prop
        if prop.hallu or prop.blind or prop.confusion or prop.stun or prop.polymorph:
            return None
        here = (int(bl.y), int(bl.x))
        dis = agent.bfs()
        if self.pending is not None:
            pos = self.pending[0]
            if here == pos or dis[pos] != -1:
                return 'pickup', pos
            return None
        if not self.altar_tested:
            alts = [p for p in self._altars() if p == here or dis[p] != -1]
            if alts:
                return 'altar', min(alts, key=lambda p: 0 if p == here else dis[p])
            return None
        if self._flash_due():
            alts = [p for p in self._altars() if p == here or dis[p] != -1]
            if alts:
                return 'flash', min(alts, key=lambda p: 0 if p == here else dis[p])
            return None
        if self._gather_due():
            job = self._gather_job(here, dis)
            if job is not None:
                return job
        if self.can_donate() and self.in_town():
            priests = self._priests()
            near = [p for p in priests if utils.adjacent(here, p) or
                    any(dis[ny, nx] != -1 for ny, nx in agent.neighbors(*p, shuffle=False))]
            if near:
                return 'priest', min(near, key=lambda p: max(abs(p[0] - here[0]), abs(p[1] - here[1])))
            # the priest is out of view: wait for him next to the altar
            alts = [p for p in self._altars() if p == here or dis[p] != -1]
            if alts:
                return 'wait', min(alts, key=lambda p: 0 if p == here else dis[p])
        return None

    def _walk(self, pos, one_before=False):
        agent = self.agent
        t0 = agent.step_count
        agent.go_to(*pos, stop_one_before=one_before, max_steps=8,
                    callback=lambda: bool(self._hostiles_within(3)))
        if agent.step_count == t0:
            agent.search()

    def _altar(self, pos):
        agent = self.agent
        bl = agent.blstats
        if (int(bl.y), int(bl.x)) != tuple(pos):
            self._walk(pos)
            return
        items = self.altar_items()
        if not items:
            fb = self._fallback_item()
            items = [fb] if fb is not None else []
        if not items:
            self.altar_tested = True
            self.log('nothing to drop on the altar')
            agent.search()
            return
        free = agent.inventory.items.free_slots() if hasattr(agent.inventory.items, 'free_slots') else None
        self.log(f'on the altar at {tuple(pos)}: BUC test of {len(items)} items: {[i.text for i in items][:40]}')
        self.pending = (tuple(int(v) for v in pos), frozenset(_glyph(i) for i in items), int(bl.time))
        self._pickup_tries = 0
        self.altar_drops += 1
        seen = self._flash_count()
        ok = agent.inventory.drop(items)
        msg = ' '.join([agent.message or ''] + list(agent.popup or []))
        self.flashes += self._flash_count() - seen
        self.log(f'altar answer (drop ok={ok}, free slots before {free}, flashes {self.flashes}): {msg[:400]!r}')
        if ok is False:
            self.pending = None
        self.altar_tested = True

    def _flash(self, pos):
        """ALTAR_FLASH: the temple altar has not flashed for anything we dropped -- put something on it that is
        known to be cursed or blessed."""
        # hypothesis: an altar answers a dropped object with a flash only when it is cursed or blessed ("There is a
        # black flash as ... hits the altar" / "an amber flash"), and that message is what shows -- to the player and
        # to this run's scorer -- that the curse status was checked: 5 of the 48 development trips that dropped
        # their pack on the temple altar saw no flash at all (3-11 stacks, all uncursed: weapons and armor are
        # uncursed 78% of the time, wands 94%, food and most tools always), so the game had walked to Minetown and
        # used its temple with nothing to show for it. The flash does not depend on what the hero already knows --
        # do.c doaltarobj() prints it for every blessed or cursed object -- and every one of the five carried such
        # an object with its status already known (a cursed scroll and blessed daggers from an earlier altar, a
        # cursed ring of adornment; twice only Excalibur in hand, which the fountain always blesses): the trip had
        # left exactly those in the pack as "nothing to learn". So when the altar has stayed dark, one such object
        # goes on it and comes straight back: something from the pack, else the blessed weapon in hand (two turns
        # in the temple, only with nothing hostile in view, wielded again at once). An altar that has flashed
        # already (the trip's own drop, or power_route's test of the potions and scrolls) is left alone.
        # Measured (parent -> this, same seeds): all five dark altars flashed; games that reached and used the
        # temple with a flash: 44 -> 50 of 79 development games; the held-out block had no dark altar (31 of 60
        # both ways).
        # sources: NetHack 3.6.6 src/do.c doaltarobj() ("There is %s flash as %s %s the altar" when obj->blessed ||
        # obj->cursed, whatever bknown says; "%s %s on the altar" otherwise; nothing when blind) and
        # src/fountain.c dipfountain() (Excalibur: bless, erodeproof) ; https://nethackwiki.com/wiki/Altar ("A
        # black flash marks a cursed item, while an amber flash marks a blessed one", none for uncursed; a thrown
        # object gives no answer) ; https://nethackwiki.com/wiki/Curse (the generation table: weapons 8.6% blessed /
        # 78.2% uncursed / 13.2% cursed, wands 94% uncursed, comestibles and "other tools" 100% uncursed) ;
        # https://nethackwiki.com/wiki/Excalibur ("the sword will be blessed and made rustproof") ; player
        # discussion: https://nethackwiki.com/wiki/Talk:Minetown (the temple as the town's point; "Minetown is the
        # only fixed layout level ... to have coaligned temples at all") ; /refs/parent-eval-extra.json (the
        # scorer's altar_tests equals the number of flash messages in the game: 0 for seed 386149, whose four
        # stacks were all uncursed, although its Excalibur would have flashed).
        agent = self.agent
        bl = agent.blstats
        if (int(bl.y), int(bl.x)) != tuple(pos):
            self._walk(pos)
            return
        items = self._flash_items()
        if not items:
            agent.search()
            return
        wielded = items[0].equipped
        if wielded and self._hostiles_within(8):
            agent.search(2)   # the weapon stays in hand while anything hostile is near
            return
        self._flash_tries += 1
        self._rewield = _glyph(items[0]) if wielded else None
        self.log(f'no flash so far: {items[0].text!r} (known cursed / blessed'
                 f'{", in hand" if wielded else ""}) goes on the altar at {tuple(pos)}')
        self.pending = (tuple(int(v) for v in pos), frozenset(_glyph(i) for i in items), int(bl.time))
        self._pickup_tries = 0
        self.altar_drops += 1
        seen = self._flash_count()
        ok = agent.inventory.drop(items)
        self.flashes += self._flash_count() - seen
        self.log(f'altar answer to the second drop (ok={ok}): flashes {self.flashes}')
        if ok is False:
            self.pending = None
            self._rewield = None

    def _pickup(self, pos):
        agent = self.agent
        bl = agent.blstats
        if (int(bl.y), int(bl.x)) != tuple(pos):
            self._walk(pos)
            return
        inv = agent.inventory
        self._pickup_tries += 1
        glyphs = self.pending[1]
        try:
            below = inv.get_items_below_me()
            mine = [it for it in below if _glyph(it) in glyphs]
            if mine:
                inv.pickup(mine)
            left = [it for it in (inv.items_below_me or []) if _glyph(it) in glyphs]
        except Exception:
            if self._pickup_tries >= ALTAR_PICKUP_TRIES * (4 if self._rewield is not None else 1):
                self.log('altar pickup given up after errors')
                self.pending = None
            raise
        self.log(f'altar pickup: took {len(mine) - len(left)} of {len(mine)} stacks back'
                 f'{"" if not left else f"; left {[it.text for it in left][:20]}"}')
        if not left or self._pickup_tries >= ALTAR_PICKUP_TRIES * (4 if self._rewield is not None else 1):
            self.pending = None
        if not mine:
            agent.search()
        if self.pending is None and self._rewield is not None:
            # ALTAR_FLASH: the weapon that lay on the altar goes back in hand
            glyph, self._rewield = self._rewield, None
            weapon = next((it for it in inv.items if _glyph(it) == glyph and not it.equipped and
                           ' blessed ' in _words(it)), None)
            if weapon is not None:
                ok = inv.wield(weapon)
                self.log(f'{weapon.text!r} wielded again: {ok}')
            else:
                self.log('the weapon that lay on the altar is not in the pack')
        if self.pending is None:
            self._wear()   # the altar has spoken: what is not cursed and better than what is worn goes on

    def _wait_for_priest(self, altar):
        agent = self.agent
        bl = agent.blstats
        self._priest_wait += 1
        if self._priest_wait > 30:
            self._priest_off = True
            self.log('no priest serves this altar')
        if max(abs(altar[0] - bl.y), abs(altar[1] - bl.x)) > 2:
            self._walk(altar, one_before=True)
            return
        agent.search(3)

    def _donate(self, priest):
        agent = self.agent
        bl = agent.blstats
        here = (int(bl.y), int(bl.x))
        if not utils.adjacent(here, priest):
            self._walk(priest, one_before=True)
            return
        amount = self.price()
        self._donate_tries += 1
        direction = agent.calc_direction(here[0], here[1], priest[0], priest[1])
        action = {
            'n': A.CompassDirection.N, 's': A.CompassDirection.S,
            'e': A.CompassDirection.E, 'w': A.CompassDirection.W,
            'ne': A.CompassDirection.NE, 'se': A.CompassDirection.SE,
            'nw': A.CompassDirection.NW, 'sw': A.CompassDirection.SW,
        }.get(direction, direction)
        asked = [False]

        def gen():
            if 'Talk to whom?' not in agent.message:
                yield A.Command.ESC
                return
            yield action
            n = 0
            while 'How much will you offer?' not in agent.message and agent._observation['misc'][2] and n < 10:
                n += 1
                yield ' '
            if 'How much will you offer?' not in agent.message:
                return
            asked[0] = True
            yield from str(amount)
            yield '\r'

        gold_before = int(bl.gold)
        with agent.atom_operation():
            agent.step(A.Command.CHAT, gen())
        message = ' '.join([agent.message or ''] + list(agent.popup or []))
        self.log(f'donated {amount} of {gold_before} gold at XL {bl.experience_level} (asked={asked[0]}): '
                 f'{message[:300]!r}')
        if 'rewarded for thy devotion' in message or 'devotion has been rewarded' in message:
            self.donations += 1
            self.protection += 1
            return
        if asked[0] and int(agent.blstats.gold) < gold_before:
            self.donations += 1
        if 'selfless generosity' in message or \
                any(t in message for t in ('words, eh?', 'Here is what I have to say', 'speak no longer',
                                           'anything to do with you', 'Begone!', 'cheapskate', 'Cheapskate')):
            self._priest_off = True
            return
        if not asked[0] and self._donate_tries >= 3:
            self._priest_off = True
