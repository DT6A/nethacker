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
# ---- second iteration: THE TRIP NEVER STAYS STUCK (TRIP_UNBLOCK_LADDER, TRIP_FAST_EXPLORE, ORCISH_TOWN_BREACH) ----
# hypothesis: the trip above used the temple in 56% of 61 fresh games and 4 of 10 trips that failed also died,
# because the hero stood for 1500-6000 turns behind something AutoAscend's BFS calls a wall, praying for food
# every ~900 turns (each prayer fails 2-8% of the time, rnz(350)) until a pack or a failed prayer ended it. Replays
# of every such game named the walls; each got its own rung, measured on its own and then together (same seeds as
# the parent; "est" = progress x the run's multiplier rebuilt from XL, AC, temple use, holes and starvation):
#   1. the unblock ladder (unblock): a squeeze counts when it reaches ANY new square (what lies behind it is the
#      unexplored half of the level), a carried pick-axe digs out one rock corner of the squeeze instead of dropping
#      the pack (plate mail can never get under 600), an anti-magic field is walked (it only drains Pw), and when
#      the safe traps open nothing -- or the hero is boxed in -- every trap but polymorph is. 61 games: temple
#      56% -> 61%, games reaching the dive 43 -> 46, est 0.379 -> 0.392;
#   2. the frontier walk (seek, _fast_explore): explore1 without its searching (mkmap caves have no secret
#      passages; explore1 searches every dead-end nook 15 times and once per new square for traps), and the ladder's
#      next rung the moment that walk has nothing left in reach; a locked door between the hero and the town is
#      kicked when no watchman is in view (_kick_out: the room-built towns put the stairs in rooms of their own;
#      never a door inside the town). Trips took 300-1400 turns instead of 1500-3000. With 1.: temple 70%, dive
#      49 of 61, est 0.416;
#   3. Orcish Town (_orc_step, _break_boulder): its altar tests curses as well as any, but the town has no gate.
#      A ready hero (AC <= 3, XL 7+, a pick-axe) digs in through the wall below the temple and breaks the rubble
#      on the way: 4 of 4 eligible towns entered and their altars used in 142 development games, but 2 of the 4
#      heroes died within 1000 turns afterwards (a poisoned spiked pit on the way back, a leocrotta): temple +3
#      points, est unchanged within noise;
#   4. rules from deaths and stalls seen on the way: spiked pits and dart traps are not "safe" traps without
#      poison resistance (trap.c: 1 in 6 poisoned; fatal 1 in 8 / 1 in 30 -- both ended a game at full HP), no
#      trip with AC above 7 or as a lycanthrope (a were shape change had dropped all the armor), no ring wear test
#      in town (power_route RING_TEST_TOWN_GUARD: a ring of conflict set the temple's priestess on the hero), and
#      a hero boxed in by boulders breaks one (_boxed_by_boulders: a scroll of earth read in a corridor).
# All together, parent -> this version (both rerun here; a game's result moves a little between two runs of the
# same program -- the parent's wand-of-wishing game on public seed 1 came once in two runs): development games
# 0-14 + 386141-386150: temple 64% -> 76%, est 0.457 -> 0.452 (public 0-14 alone: raw 0.523 -> 0.497, the dive's
# lottery); 13026-13061: temple 50% -> 78%, est 0.325 -> 0.402; 31502-31537 (drawn as held-out, read after the
# first comparison, so development seeds since): temple 56% -> 75%, est 0.416 -> 0.470. HELD-OUT, never read,
# 108 games (46044-46079, 42647-42682, 21466-21501): temple 50% -> 62%, games reaching the dive 73% -> 80%, games
# ending on level <= 4: 24 -> 20, raw progress 0.377 -> 0.409, est 0.367 -> 0.400 (each block: +0.024, +0.040,
# +0.034 raw). What is left: deaths in the grind before the trip (10-15% of games), Orcish Town without a
# pick-axe or with a weak hero (5%), poison on Mines levels 3-4 (soldier ants, orcish arrows: 2-3%), a Mines
# branch hidden on Dlvl 2-4 (2%), a trap door in the temple's doorway, a gas spore in a shop's door.
# Not built: a trip at XL 6 (the dive framework has no way back to the grind), a hole when the '>' stays hidden
# (the first iteration measured its way back: 5 deaths), gold for the priest (400*XL: no game came near).
# sources: read for this change -- NetHack 3.6.6 source (github.com/NetHack/NetHack, tag NetHack-3.6.6_Released):
# src/hack.c (test_move: "You are carrying too much to get through", invent weight > 600; in_town(): the room
# with subrooms), src/trap.c (ANTI_MAGIC: "hero without magic resistance loses spell energy"; SPIKED_PIT:
# !rn2(6) -> poisoned(..., fatal 8); DART_TRAP: !rn2(6) -> poisoned(..., 10, thrown)) and src/attrib.c
# (poisoned(): dead when rn2(fatal + (thrown ? 20 : 0)) == 0), src/dokick.c (a kicked door, broken or not: only a watchman with
# couldsee() minds), src/mkmap.c (join_map joins the cave's regions; it makes no secret doors or corridors),
# src/dig.c ("The boulder falls apart."; a dug wall becomes a corridor on a cavernous level, a doorway in
# town); NLE's dat/mines.des (minetn-1 Orcish Town: map, iron bars, ALTAR:(20,13) "useful for BUC
# but never coaligned", 9+2d5 boulders, the orc army inside; minetn-2/3/4/7: each staircase in a ROOM of its
# own; minefill: no doors) ; https://nethackwiki.com/wiki/Minetown (Orcish Town: "need a digging tool ... to
# breach the walls", orcs are slow -> "funnel them through corridors", poisoned arrows through the bars; what
# the Watch minds and that sight matters; the four room-built towns) ; https://nethackwiki.com/wiki/Gnomish_Mines
# (filler levels are "simple caverns" with 6 traps; "run upstairs to heal", back off and try later; poison
# resistance for the lower Mines) ; https://nethackwiki.com/wiki/Movement_tactics ("can only move southwest if
# his or her total inventory weight is 600 or less ... applies to all tight gaps") ;
# https://nethackwiki.com/wiki/Trap ; https://nethackwiki.com/wiki/Door (kicks and the Watch) ; player
# discussions: https://nethackwiki.com/wiki/Forum:OrcTown ("break in with a wand of digging right into the
# temple"; the altar is the town's silver lining), https://nethackwiki.com/wiki/
# Forum:Have_a_good_strategy_for_descension%3F (Mines "with about 50 HP and AC 0", "don't be afraid to run away
# and heal", fight in a corridor one enemy at a time, trap doors that drop several levels),
# https://nethackwiki.com/wiki/Forum:Post-mines_strategy_for_intermediate_player%3F (the altar or a pet for the
# curse status of the Mines' armor; protection from the priest) ; the task brief ("digging sideways is a good
# tactic"); /refs/past_runs.md idea #195 (kick a Mines door only when boxed in: a locked stair room) and
# reference run 20261102-161819 #862 (Orcish Town among the seven maps); /refs/top/README.md (the 54 top
# programs are dive-first engines of this lineage: none goes to Minetown, nothing to port for this stage).
"""
import difflib

import nle.nethack as nh
from nle.nethack import actions as A

from . import jf_config, utils
from .character import Character
from .glyph import G, MON, Hunger, SS
from .level import Level
from .strategy import Strategy

TRIP_MIN_XL = 6                 # Minetown wants XL 6-8 (the dive trigger is XL 7 with a pick-axe, XL 8 without)
TRIP_MAX_AC = 7                 # ... and an armor class no worse than this (a Valkyrie starts with AC 6)
TRIP_TOTAL_TURNS = 9000         # the whole trip, from its start to the hand-over
BRANCH_TURNS = 3000             # looking for the Mines branch on Dlvl 2-4
TRIP_LEVEL_TURNS = 1500         # on one Mines level without the trip moving on
TOWN_TURNS = 3000               # in the town itself (a locked temple, a priest on the altar)
REST_BELOW = 0.8                # the trip walks on only above this fraction of max HP (nothing hostile in view)
MIDDLE_SEEN = 90                # squares of a level's middle band seen without a town sign: a filler level
ESCAPE_HP = 0.5                 # above the town, a losing fight at or below this fraction of max HP is dug away from
UNBLOCK_AFTER_TURNS = 150       # a staircase still out of reach this long on a Mines level: squeezes and traps
TRAPS_AFTER_TURNS = 350         # ... and only this late through known traps
SQUEEZE_ANY_AFTER = 300         # TRIP_UNBLOCK_LADDER: from here on a squeeze that reaches any new square is opened
NO_SEARCH = 10 ** 9              # TRIP_FAST_EXPLORE: explore1's search priority limit that nothing reaches
# ORCISH_TOWN_BREACH (mines.des minetn-1, GEOMETRY:center,center: the 37x19 map always lies with its (0, 0) at glyph
# row 1, column 20 -- read off two games' iron bars): the temple is x 18-22, y 11-14, its altar (20, 13); below it the
# temple's own wall (y 15), a one-square street (y 16), the town wall (y 17) and the ring of floor outside (y 18)
ORC_ORIGIN = (1, 20)
ORC_BARS = frozenset({(1, 17), (5, 1), (6, 35), (16, 35), (17, 12), (17, 25)})   # (y, x) on the map
ORC_COLUMNS = (20, 19, 21, 18, 22)   # map x of the breach, the altar's own column first
ORC_TURNS = 1500                # the breach's budget from the arrival in the town
ORC_MAX_AC = 3                  # the readiness gate: AC, XL and max HP for 6-15 orc-captains / Uruk-hai one at a time
ORC_MIN_XL = 7
ORC_MIN_HP = 55
ORC_REACH_TURNS = 300            # ... and for the square below the temple to come into reach
ORC_HOLD_RADIUS = 6             # hostiles in view this close: hold the square (the fight comes to the breach)
KICK_OUT_REACH = 200            # _kick_out: this few squares in reach -- the town is still behind the door
KICK_OUT_TRIES = 60
BOXED_REACH = 12                # ... and at once when this few squares are in reach (boxed in)
POST_HOLD_GAP = 800             # the dive proper starts this long after the last prayer (dive_logic.DIVE_PRAYER_GAP)
POST_HOLD_MAX = 1200            # ... or after this many turns of waiting for it
DIG_AFTER_TURNS = 0             # (off) a '>' above the town still cut off after this many turns: dig down. Measured on
# 79 development games: with 600 the trip used the temple in 75% of games instead of 63%, but a hole lands away from
# the level's '<' and the way back up took 500+ turns instead of ~120: 5 deaths on the way back against 0-1
ALTAR_PICKUP_TRIES = 4
DONATE_TRIES = 6


_CORRIDOR = frozenset({SS.S_corr, SS.S_litcorr})


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
        self._pickup_tries = 0
        self.donations = 0
        self.protection = 0
        self._donate_tries = 0
        self._priest_off = False       # no priest to talk to / he refused / protection capped
        self._priest_wait = 0
        self.end_reason = None
        self._filler = set()           # Mines level 3/4 keys judged not to be the town
        self._unblock_turn = {}        # level key -> last turn unblock() acted there
        self._trap_reach = {}          # level key -> squares in reach when the safe traps were last opened
        self._corner_dig = None        # (level key, from, corner, beyond, since turn, tries): a squeeze being dug out
        self._corner_failed = set()    # (level key, corner) that did not dig
        self._corner_dig_off = set()   # level keys where rock does not dig
        self._kicks = {}               # (level key, door) -> kicks given (_kick_out)
        self._orc_off = False          # ORCISH_TOWN_BREACH given up (or never eligible)
        self._orc_col = None           # glyph column of the breach
        self._orc_logged = False
        self._orc_digs = 0
        self._orc_wait = None
        self._boulders = {}            # boulder square -> digs at it (_break_boulder)
        self._wear_turn = -10 ** 9
        self.holding = False           # the post-trip prayer hold (dig_first stays quiet meanwhile)
        self._hold_start = None
        self._hold_over = False
        self._escapes = 0

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
        if jf_config.TRIP_UNBLOCK_LADDER and (bl.armor_class > TRIP_MAX_AC or agent.character.is_lycanthrope):
            # the readiness gate: a hero who lost her armor (dev 386146: a werejackal's shape change dropped it all,
            # AC 10) or who may change shape again among the Mines' packs does not make the trip
            self.done = True
            self.end_reason = 'not started'
            self.log(f'no trip: AC {bl.armor_class}, lycanthrope={agent.character.is_lycanthrope}')
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

    def business_done(self):
        """The altar has answered and nothing is left to do with the priest."""
        if not self.altar_tested or self.pending is not None:
            return False
        if self.can_donate() and self.in_town():
            return False
        return True

    def _over(self):
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        now = int(bl.time)
        if level.key() != self._level_key:
            self._level_key = level.key()
            self._level_since = now
        if self.in_town() and self._town_since is None:
            self._town_since = now
            self.log(f'in town at turn {now} (trip turn {now - self.start_turn}), XL {bl.experience_level}, '
                     f'gold {bl.gold}, altars {self._altars()}')
        if agent.prayer_failed:
            return 'prayer failed'
        if self.business_done():
            return 'serviced'
        if self.in_town() and self.orcish(level) and not self.altar_tested and not self._orc_go(level):
            return 'Orcish Town'
        if level.dungeon_number not in (Level.DUNGEONS_OF_DOOM, Level.GNOMISH_MINES):
            return 'off the route'
        if now - self.start_turn > TRIP_TOTAL_TURNS:
            return 'budget'
        if self.pending is not None:
            return None
        if level.dungeon_number == Level.DUNGEONS_OF_DOOM:
            if now - self.start_turn > BRANCH_TURNS:
                return 'branch budget'
        elif self._town_since is not None:
            if now - self._town_since > TOWN_TURNS and (self.altar_tested or self._next_job() is None):
                return 'town budget'
        elif now - self._level_since > TRIP_LEVEL_TURNS and level.level_number <= 4:
            return 'level budget'   # (below the town the climb is the dive's own way back anyway)
        return None

    def _end(self, why):
        agent = self.agent
        gl = agent.global_logic
        bl = agent.blstats
        self.active = False
        self.done = True
        self.end_reason = why
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
        if jf_config.TRIP_UNBLOCK_LADDER and self._boxed_by_boulders():
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
        if self.seek(G.STAIR_DOWN, reachable):
            return
        if not dive.exploration(0).until(agent, dive._budgeted(reachable)).run(return_condition=True):
            dive.exploration(None).until(agent, dive._budgeted(reachable)).run()

    def passing(self):
        """After a trip that ended without the altar (a budget, a fall past the town), the dive's own way back up
        still leads through the town: with its altar in reach, the test is done in passing (no searching for it)."""
        agent = self.agent
        dive = self.dive
        level = agent.current_level()
        if not self.done or self.start_turn is None or self.altar_tested and self.pending is None:
            return False
        if self.end_reason in ('serviced', 'Orcish Town', 'not started', 'prayer failed') or agent.prayer_failed:
            return False
        if level.dungeon_number != Level.GNOMISH_MINES or level.level_number not in (3, 4) or self.orcish(level):
            return False
        if agent.get_visible_monsters():
            return False
        job = self._next_job()
        if job is None or job[0] not in ('altar', 'pickup'):
            return False
        kind, target = job
        before = agent.step_count
        dive._task(f'minetown (passing): {kind}')
        if kind == 'pickup':
            self._pickup(target)
        else:
            self._altar(target)
        if self.altar_tested and self.pending is None:
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
        if self.unblock(G.STAIR_UP) or self.way_back():
            if agent.step_count == before:
                agent.search()
            return True
        dive.return_to_main_dungeon()
        if agent.step_count == before:
            agent.search()
        return True

    def unblock(self, stairs, force=False):
        """A Mines level whose wanted staircase (G.STAIR_DOWN / G.STAIR_UP) has stayed out of reach: what hides a
        way on from AutoAscend's BFS, opened one rung at a time (TRIP_UNBLOCK_LADDER, see the hypothesis below).
        (1) A diagonal step between two rock corners needs an inventory of 600 or less (hack.c test_move /
        cant_squeeze_thru), and the Mines' caves are full of them: with a pick-axe the corner is dug out (nothing
        is lost), else the pack drops to 550 (agent.unsqueeze's cap). (2) Every known trap is a wall to the BFS:
        walk through the safe kinds (never a trap door or hole), and when that opens nothing -- or we are boxed in
        on a handful of squares -- through the rest but a polymorph trap. Used by the trip on its way down and back
        up, and by the dive's own return to the main dungeon after the trip."""
        # hypothesis: the trip's failures and most of its deaths are one thing -- the hero stays on a Mines level
        # for thousands of turns behind an obstacle the BFS calls a wall, praying for food every ~900 turns until a
        # prayer fails or a pack finds her (parent, 61 games: 5 trips ended on the level budget and 3 more were
        # stuck 3500-6000 turns on the way back; 4 of those 8 games died there). Read off the replays:
        #   - the squeeze rule wanted 15 more squares behind the squeeze, but behind it lies the unexplored half of
        #     the level (dev 386142: +1 square, 386148: +6): any gain counts once the level has been walked for
        #     SQUEEZE_ANY_AFTER turns;
        #   - a hero in plate mail (450) can never get under 600: she sat 6000 turns on one square (seed 13061).
        #     A carried pick-axe digs out one rock corner of the squeeze instead (a sideways dig, never on the
        #     town level: the Watch) -- which also keeps the pack for the altar;
        #   - the one passage is an "unsafe" trap: an anti-magic field only drains Pw from a hero without magic
        #     resistance (trap.c ANTI_MAGIC -> drain_en; dev 13: the level's west half lay behind one), and a
        #     magic trap, sleeping gas, rust or fire trap is a far smaller risk than starving behind it (13061
        #     stepped over a then-unknown magic trap into a dead end and never came out).
        # Expected: fewer level-budget ends, shorter trips, fewer deaths in the Mines.
        # sources: see the module header (hack.c test_move, trap.c ANTI_MAGIC / SPIKED_PIT, dokick.c, mines.des,
        # the wiki's Minetown / Gnomish_Mines / Movement_tactics pages, Forum:OrcTown and the descension forum thread).
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        key = level.key()
        now = int(bl.time)
        # force (seek, TRIP_FAST_EXPLORE): the frontier walk has nothing left in reach, so the staircase is cut off
        # for certain -- no waiting for UNBLOCK_AFTER_TURNS / TRAPS_AFTER_TURNS, any squeeze gain counts
        if level.dungeon_number != Level.GNOMISH_MINES or \
                (not force and dive.turns_on_level() < UNBLOCK_AFTER_TURNS):
            return False
        ladder = jf_config.TRIP_UNBLOCK_LADDER
        if ladder and self._corner_dig is not None and self._corner_dig[0] == key:
            return self._dig_corner()
        if now - self._unblock_turn.get(key, -10 ** 9) < (12 if force else 80):
            return False
        dis = agent.bfs()
        if any(dis[p] != -1 for p in zip(*utils.isin(level.objects, stairs).nonzero())):
            return False
        self._unblock_turn[key] = now
        reach = int((dis != -1).sum())
        items = agent.inventory.items
        boxed = ladder and reach <= BOXED_REACH
        if items.total_weight > 600:
            wide_dis = agent.bfs(force_squeeze=True)
            wide = int((wide_dis != -1).sum())
            agent.last_bfs_step = -1
            tool = dive.digging_tool()
            gain = wide >= reach + 15 or (ladder and wide > reach and
                                          (force or boxed or dive.turns_on_level() >= SQUEEZE_ANY_AFTER))
            if gain and ladder and self._corner_dig_ok(tool, level) and self._plan_corner_dig(dis, wide_dis, key):
                self.log(f'unblock on {key}: carrying {items.total_weight:.0f}, a squeeze reaches {wide} squares '
                         f'instead of {reach}: digging out the corner {self._corner_dig[2]} from '
                         f'{self._corner_dig[1]}')
                return self._dig_corner()
            essential = sum(i.weight() for i in items.all_items if i.equipped or i is tool)
            if gain and essential <= 540 and now >= getattr(agent, '_squeeze_cap_until', -1):
                self.log(f'unblock on {key}: carrying {items.total_weight:.0f}, a squeeze reaches {wide} squares '
                         f'instead of {reach}: dropping to 550')
                agent._squeeze_cap_until = now + 400
                agent.inventory.arrange_items().run()
                agent.inventory.unreachable_items_until[agent.inventory._here()] = now + 5000
                return True
        traps = utils.isin(level.objects, G.TRAPS)
        if force and traps.any() and agent._last_turn - agent._allow_walking_through_traps_turn <= 50 and \
                agent._last_turn - getattr(agent, '_allow_unsafe_traps_turn', -float('inf')) > 50 and \
                utils.isin(level.objects, agent.UNSAFE_TRAPS - agent.NEVER_TRAPS).any():
            # the safe traps are open and still nothing is left to walk to: the rest but polymorph
            agent._allow_unsafe_traps_turn = agent._last_turn
            agent._allow_walking_through_traps_turn = agent._last_turn
            agent.last_bfs_step = -1
            self.log(f'unblock on {key}: {reach} squares in reach, nothing behind the safe traps: walking through '
                     f'the known traps (all but polymorph)')
            return True
        if (force or dive.turns_on_level() >= TRAPS_AFTER_TURNS or boxed) and traps.any() and \
                agent._last_turn - agent._allow_walking_through_traps_turn > 50:
            # the second rung: the safe kinds opened nothing new last time (or we are boxed in) -> the rest too
            last = self._trap_reach.get(key)
            risky = ladder and utils.isin(level.objects, agent.UNSAFE_TRAPS - agent.NEVER_TRAPS).any() and \
                (boxed or (last is not None and reach <= last + 10))
            self._trap_reach[key] = reach
            if risky:
                agent._allow_unsafe_traps_turn = agent._last_turn
            self.log(f'unblock on {key}: {reach} squares in reach, walking through the '
                     f'{"known traps (all but polymorph)" if risky else "safe known traps"}')
            dive._walk_through_traps(climbing=True)
            return True
        return False

    def _fast_explore(self, found):
        """TRIP_FAST_EXPLORE: the frontier walk -- AutoAscend's explore1 without its searching. The Mines' filler
        levels are mkmap caves: no secret doors or corridors (mkmap.c joins every region), so the 15 searches
        explore1 spends on each dead-end nook and the one search per new square for traps (found 1 time in 8)
        only make the walk through the Mines' packs twice as long. Loot is still picked up (gather_items).
        True: it walked; False: no unexplored square is left in reach."""
        agent = self.agent
        dive = self.dive
        strat = Strategy(lambda: agent.exploration.explore1(
            NO_SEARCH, trap_search_offset=0, kick_doors=False, check_altar_alignment=False).strategy())
        return bool(strat.until(agent, dive._budgeted(found)).run(return_condition=True))

    def seek(self, stairs, found=None):
        """Look for a staircase kind on a Mines level: the frontier walk first; with nothing left to walk to, the
        staircase is cut off, and unblock() opens the next rung at once. False: neither had anything to do (the
        caller's old search-everything exploration takes over)."""
        agent = self.agent
        level = agent.current_level()
        if not jf_config.TRIP_FAST_EXPLORE or level.dungeon_number != Level.GNOMISH_MINES:
            return False
        if found is None:
            found = lambda: any(agent.bfs()[p] != -1 for p in
                                zip(*utils.isin(agent.current_level().objects, stairs).nonzero()))
        if found():
            return False
        before = agent.step_count
        if self._fast_explore(found):
            return True
        if agent.step_count != before:
            return True
        if agent.current_level().key() != level.key():
            return False
        return bool(self.unblock(stairs, force=True) or self._kick_out())

    def _kick_out(self):
        """Shut in behind a locked door on a Mines level: the town maps built from rooms (mines.des minetn-2/3/4/7)
        put each staircase in a room of its own, joined by corridors through doors that may be locked, and explore1
        never kicks in the Mines (the Watch). The Watch only minds a door broken where a watchman can see it
        (dokick.c: is_watchman && couldsee), and those stair rooms are not part of the town (hack.c in_town: the
        room with subrooms). So: a handful of squares in reach, a closed door next to them that did not open, no
        watchman in view, not in a shop -- kick it."""
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
        # called when the frontier walk has nothing left in reach: a door that did not open is the way on. Only
        # while the town itself is not in reach (a stair room, the corridors and rooms around the town: at most
        # KICK_OUT_REACH squares; the town room alone is ~450) or from a corridor square: never the doors inside
        # the town (shops, the temple, houses), and a shop's sign is read below all the same.
        boxed = int((dis != -1).sum()) <= KICK_OUT_REACH
        best = None
        for y, x in zip(*utils.isin(agent.glyphs, G.DOOR_CLOSED).nonzero()):
            y, x = int(y), int(x)
            if level.door_open_count[y, x] < 1 or self._kicks.get((level.key(), (y, x)), 0) >= KICK_OUT_TRIES:
                continue
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < dis.shape[0] and 0 <= nx < dis.shape[1] and dis[ny, nx] != -1 and \
                        (boxed or level.objects[ny, nx] in _CORRIDOR) and \
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
        if sign and (difflib.SequenceMatcher(None, sign, 'closedforinventory').ratio() >= 0.55 or len(sign) >= 12):
            # "Closed for inventory" in front of a shut shop (worn or not): its keeper kills for a broken door
            self._kicks[k] = KICK_OUT_TRIES
            self.log(f'door at {door}: a sign {sign!r} lies before it, not kicked')
            return False
        self._kicks[k] = self._kicks.get(k, 0) + 1
        if self._kicks[k] == 1:
            self.log(f'shut in ({int((dis != -1).sum())} squares in reach) behind the door at {door}: kicking it')
        agent.kick(*door)
        if agent.glyphs[door] not in G.DOOR_CLOSED:
            self.log(f'door at {door} is open after {self._kicks[k]} kicks: {(agent.message or "")[:80]!r}')
        agent.last_bfs_step = -1
        return True

    def way_back(self):
        """The dive's return to the main dungeon after the trip (and the trip's own climb back to the town): with
        no '<' in reach, the frontier walk and the ladder instead of return_to_main_dungeon's searching."""
        agent = self.agent
        level = agent.current_level()
        if not jf_config.TRIP_FAST_EXPLORE or level.dungeon_number != Level.GNOMISH_MINES:
            return False
        dis = agent.bfs()
        ups = set((int(y), int(x)) for y, x in zip(*utils.isin(level.objects, G.STAIR_UP).nonzero()))
        here = level.level_number
        for p, d in level.stair_destination.items():   # as DiveLogic.return_to_main_dungeon (RETURN_FIX)
            if d is not None and ((d[0][0] == level.dungeon_number and d[0][1] == here - 1) or
                                  (here == 1 and d[0][0] == Level.DUNGEONS_OF_DOOM)):
                ups.add((int(p[0]), int(p[1])))
        if any(dis[p] != -1 or self.dive._neighbour_distance(dis, *p) is not None for p in ups):
            return False
        before = agent.step_count
        self.dive._task('minetown: looking for the way up')
        if not self.seek(G.STAIR_UP):
            return False
        if agent.step_count == before:
            agent.search()
        return True

    def _corner_dig_ok(self, tool, level):
        """A sideways dig is allowed: a pick-axe (a mattock only with the shield hand free), in our own form, and
        not on the town level (digging there angers the Watch)."""
        agent = self.agent
        if tool is None or agent.character.prop.polymorph or level.key() in self._corner_dig_off:
            return False
        if level.key() == agent.global_logic.minetown_level or self.is_town_level(level):
            return False
        if ' mattock' in _words(tool) and agent.inventory.items.off_hand is not None:
            return False
        return True

    def _plan_corner_dig(self, dis, wide_dis, key):
        """The nearest squeeze: a reachable square p with a diagonal neighbour q that only a squeeze reaches; one of
        the two corners between them (rock or wall, inside the map, nobody standing there) is dug out."""
        agent = self.agent
        level = agent.current_level()
        h, w = dis.shape
        best = None
        for qy, qx in zip(*((wide_dis != -1) & (dis == -1)).nonzero()):
            for dy in (-1, 1):
                for dx in (-1, 1):
                    py, px = int(qy) + dy, int(qx) + dx
                    if not (0 <= py < h and 0 <= px < w) or dis[py, px] == -1:
                        continue
                    for cy, cx in ((py, int(qx)), (int(qy), px)):
                        if not (1 <= cy < h - 1 and 1 <= cx < w - 2) or level.walkable[cy, cx]:
                            continue
                        if (key, (cy, cx)) in self._corner_failed or agent.monster_tracker.monster_mask[cy, cx] or \
                                utils.isin(agent.glyphs[cy:cy + 1, cx:cx + 1], G.BOULDER, G.TRAPS, G.BARS).any():
                            continue
                        if best is None or dis[py, px] < best[0]:
                            best = (int(dis[py, px]), (py, px), (cy, cx), (int(qy), int(qx)))
        if best is None:
            return False
        self._corner_dig = (key, best[1], best[2], best[3], int(agent.blstats.time), 0)
        return True

    def _dig_corner(self):
        """Walk to the squeeze and apply the pick-axe into the rock corner until it is floor."""
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        key, p, c, q, since, tries = self._corner_dig
        level = agent.current_level()
        tool = dive.digging_tool()
        dis = agent.bfs()
        now = int(bl.time)
        if level.walkable[c] or dis[q] != -1 or agent.inventory.items.total_weight <= 600:
            self.log(f'corner {c} is open' if level.walkable[c] else f'corner dig at {c} no longer needed')
            self._corner_dig = None
            agent.last_bfs_step = -1
            return False
        if not self._corner_dig_ok(tool, level) or now - since > 300 or tries >= 12 or dis[p] == -1:
            self.log(f'corner dig at {c} given up (tries {tries}, {now - since} turns)')
            self._corner_failed.add((key, c))
            self._corner_dig = None
            return False
        if self._hostiles_within(2):
            return False   # the fight first
        dive._task('minetown trip: dig out a squeeze')
        before = agent.step_count
        if (int(bl.y), int(bl.x)) != p:
            agent.go_to(*p, max_steps=10, callback=lambda: bool(self._hostiles_within(2)))
            if agent.step_count == before:
                agent.search()
            return True
        self._corner_dig = (key, p, c, q, since, tries + 1)
        direction = agent.calc_direction(p[0], p[1], c[0], c[1])
        with agent.atom_operation():
            tool = agent.inventory.move_to_inventory(tool)
            agent.step(A.Command.APPLY)
            agent.type_text(agent.inventory.items.get_letter(tool))
            prompted = 'In what direction do you want to dig?' in agent.single_message
            if prompted:
                agent.direction(direction)
            elif agent.single_message.startswith('In what direction'):
                agent.step(A.Command.ESC)
        msg = agent.message or ''
        self.log(f'corner dig {direction} into {c}: {msg[:120]!r}')
        agent.last_bfs_step = -1
        if not prompted or 'too hard to' in msg or 'cannot' in msg or "can't" in msg:
            self._corner_failed.add((key, c))
            self._corner_dig = None
            if 'too hard to' in msg:
                self._corner_dig_off.add(key)   # an undiggable level
        if agent.step_count == before:
            agent.search()
        return True

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
        explored = (jf_config.TRIP_FAST_EXPLORE and self._fast_explore(decided)) or \
            dive.exploration(0).until(agent, dive._budgeted(decided)).run(return_condition=True)
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
        dive.dig_with_tool(tool)
        return True

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
        if self.pending is None and self.orcish(agent.current_level()):
            return self._orc_step()
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
        dive._task('minetown trip: find the temple')
        found = lambda: any(agent.bfs()[p] != -1 or dive._neighbour_distance(agent.bfs(), *p) is not None
                            for p in self._altars())
        if jf_config.TRIP_FAST_EXPLORE:
            if self._fast_explore(found) or agent.step_count != before:
                return True
            # nothing left to walk to and no altar: shut in (a locked stair room, a squeeze, a trap)
            if self.unblock(G.ALTAR, force=True) or self._kick_out():
                if agent.step_count == before:
                    agent.search()
                return True
        if not dive.exploration(0).until(agent, dive._budgeted(found)).run(return_condition=True):
            dive.exploration(None).until(agent, dive._budgeted(found)).run()
        if agent.step_count == before:
            agent.search()
        return True

    # ------------------------------------------------------------------ Orcish Town

    def _orc_go(self, level):
        """ORCISH_TOWN_BREACH: Orcish Town's altar is as good for the curse test as any (mines.des: "the altar's
        defiled; useful for BUC but never coaligned"), but the town has no gate: "you must dig through the walls"
        (wiki). With a pick-axe, a hero ready for its orcs (AC, XL, HP gate) and the map where it always lies,
        the trip goes in through the wall below the temple; anything else ends the trip as before."""
        agent = self.agent
        bl = agent.blstats
        if not jf_config.ORCISH_TOWN_BREACH or self._orc_off:
            return False
        why = None
        tool = self.dive.digging_tool()
        bars = set((int(y) - ORC_ORIGIN[0], int(x) - ORC_ORIGIN[1])
                   for y, x in zip(*utils.isin(level.objects, G.BARS).nonzero()))
        if tool is None or (' mattock' in _words(tool) and agent.inventory.items.off_hand is not None):
            why = f'no pick-axe ({tool!r})'
        elif not bars or not bars <= ORC_BARS:
            why = f'the bars {sorted(bars)} are not where the map puts them'
        elif self._town_since is not None and int(bl.time) - self._town_since > ORC_TURNS:
            why = 'budget'
        elif self._orc_col is None and (bl.armor_class > ORC_MAX_AC or bl.experience_level < ORC_MIN_XL or
                                        bl.max_hitpoints < ORC_MIN_HP):
            why = f'not ready (AC {bl.armor_class}, XL {bl.experience_level}, max HP {bl.max_hitpoints})'
        if why is not None:
            self._orc_off = True
            self.log(f'Orcish Town: no breach -- {why}')
            return False
        if not self._orc_logged:
            self._orc_logged = True
            self.log(f'Orcish Town: going in through the wall below the temple (AC {bl.armor_class}, XL '
                     f'{bl.experience_level}, hp {bl.hitpoints}/{bl.max_hitpoints}, tool {tool.text!r})')
        return True

    def _orc_line(self, col):
        """Glyph squares of the breach in column col: (outside, town wall, street, temple wall, temple floor)."""
        r0 = ORC_ORIGIN[0]
        return tuple((r0 + y, col) for y in (18, 17, 16, 15, 14))

    def _orc_step(self):
        """One step of the breach: to the ring of floor below the temple, dig north through the town wall, cross
        the one-square street, dig north through the temple's wall. Whenever something hostile is in view nearby the
        hero holds her square: on the ring only the breach leads to her, in the street only its two ends do."""
        dive = self.dive
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        prop = agent.character.prop
        before = agent.step_count
        dive._task('minetown trip: Orcish Town breach')
        if prop.hallu or prop.blind or prop.confusion or prop.stun or prop.polymorph or \
                self._hostiles_within(ORC_HOLD_RADIUS):
            agent.search()
            return True
        if dive.rest_if_hurt():
            return True
        here = (int(bl.y), int(bl.x))
        if self._orc_col is None:
            for x in ORC_COLUMNS:
                col = ORC_ORIGIN[1] + x
                line = self._orc_line(col)
                if not any(agent.glyphs[p] in G.BOULDER for p in line):
                    self._orc_col = col
                    break
            else:
                self._orc_off = True
                self.log('Orcish Town: rubble on every way in')
                return True
        outside, wall1, street, wall2, inside = self._orc_line(self._orc_col)
        dis = agent.bfs()
        if not level.walkable[wall1]:
            stand, target = outside, wall1
        elif not level.walkable[wall2]:
            stand, target = street, wall2
        else:
            stand, target = inside, None
        if here != stand:
            if dis[stand] == -1:
                # the ring has not been walked yet: the frontier walk until the square is in reach
                reach = lambda: agent.bfs()[stand] != -1
                if not (self._fast_explore(reach) or agent.step_count != before or
                        self.unblock(G.ALTAR, force=True) or self._break_boulder()):
                    # rubble (the level's 10-19 boulders) or an unlit stretch: the old explorer for a while
                    if self._orc_wait is None:
                        self._orc_wait = int(bl.time)
                    if int(bl.time) - self._orc_wait > ORC_REACH_TURNS:
                        self._orc_off = True
                        self.log(f'Orcish Town: {stand} cannot be reached')
                    else:
                        dive.exploration(None).until(agent, dive._budgeted(reach)).run()
                if agent.step_count == before:
                    agent.search()
                return True
            agent.go_to(*stand, max_steps=12, callback=lambda: bool(self._hostiles_within(ORC_HOLD_RADIUS)))
            if agent.step_count == before:
                agent.search()
            return True
        if target is None:
            agent.search(3)   # in the temple: the altar job takes over as soon as the altar shows
            self._orc_digs += 1
            if self._orc_digs > 60:
                self._orc_off = True
                self.log('Orcish Town: no altar behind the wall')
            return True
        self._orc_digs += 1
        if self._orc_digs > 40:
            self._orc_off = True
            self.log(f'Orcish Town: the wall at {target} does not give way')
            return True
        msg, prompted = self._apply_dig(target)
        self.log(f'Orcish Town: digging into {target}: {msg[:100]!r}')
        if not prompted or 'too hard to' in msg:
            self._orc_off = True
        if agent.step_count == before:
            agent.search()
        return True

    def _boxed_by_boulders(self):
        """Boulders are walls to the BFS: a hero with only a handful of squares in reach and a boulder beside them
        (dev 71016 read-tested a scroll of earth in a corridor and stood between its boulders for 3350 turns,
        fainting, with a pick-axe in the pack) breaks one."""
        agent = self.agent
        if self._hostiles_within(2) or agent.character.prop.polymorph:
            return False
        tool = self.dive.digging_tool()
        if tool is None or (' mattock' in _words(tool) and agent.inventory.items.off_hand is not None):
            return False
        if not utils.isin(agent.glyphs, G.BOULDER).any():
            return False
        if int((agent.bfs() != -1).sum()) > BOXED_REACH:
            return False
        self.dive._task('minetown trip: break a boulder')
        return self._break_boulder()

    def _break_boulder(self):
        """Orcish Town's rubble (mines.des: 9 + 2d5 times a 90% boulder, anywhere) on the ring of floor around the
        walls: a boulder next to a square in reach is broken with the pick-axe (dig.c: a boulder dug at falls
        apart; no Luck is lost outside Sokoban)."""
        agent = self.agent
        bl = agent.blstats
        level = agent.current_level()
        dis = agent.bfs()
        best = None
        for y, x in zip(*utils.isin(agent.glyphs, G.BOULDER).nonzero()):
            y, x = int(y), int(x)
            if self._boulders.get((y, x), 0) >= 6:
                continue
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < dis.shape[0] and 0 <= nx < dis.shape[1] and dis[ny, nx] != -1 and \
                        (best is None or dis[ny, nx] < best[0]):
                    best = (int(dis[ny, nx]), (ny, nx), (y, x))
        if best is None:
            return False
        _, spot, boulder = best
        before = agent.step_count
        if (int(bl.y), int(bl.x)) != spot:
            agent.go_to(*spot, max_steps=12, callback=lambda: bool(self._hostiles_within(ORC_HOLD_RADIUS)))
            if agent.step_count == before:
                agent.search()
            return True
        self._boulders[boulder] = self._boulders.get(boulder, 0) + 1
        msg, prompted = self._apply_dig(boulder)
        self.log(f'breaking the boulder at {boulder}: {msg[:100]!r}')
        if not prompted:
            self._boulders[boulder] = 99
        if agent.step_count == before:
            agent.search()
        return True

    def _apply_dig(self, target):
        """Apply the digging tool sideways into the square next to us. (message, direction was asked)."""
        agent = self.agent
        bl = agent.blstats
        tool = self.dive.digging_tool()
        direction = agent.calc_direction(int(bl.y), int(bl.x), target[0], target[1])
        with agent.atom_operation():
            tool = agent.inventory.move_to_inventory(tool)
            agent.step(A.Command.APPLY)
            agent.type_text(agent.inventory.items.get_letter(tool))
            prompted = 'In what direction do you want to dig?' in agent.single_message
            if prompted:
                agent.direction(direction)
            elif agent.single_message.startswith('In what direction'):
                agent.step(A.Command.ESC)
        agent.last_bfs_step = -1
        return agent.message or '', prompted

    # ------------------------------------------------------------------ the town's business

    def _next_job(self):
        """('pickup' | 'altar' | 'priest' | 'wait', target) or None."""
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
        ok = agent.inventory.drop(items)
        msg = ' '.join([agent.message or ''] + list(agent.popup or []))
        self.flashes += msg.count(' flash as ')
        self.log(f'altar answer (drop ok={ok}, free slots before {free}): {msg[:400]!r}')
        if ok is False:
            self.pending = None
        self.altar_tested = True

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
            if self._pickup_tries >= ALTAR_PICKUP_TRIES:
                self.log('altar pickup given up after errors')
                self.pending = None
            raise
        self.log(f'altar pickup: took {len(mine) - len(left)} of {len(mine)} stacks back'
                 f'{"" if not left else f"; left {[it.text for it in left][:20]}"}')
        if not left or self._pickup_tries >= ALTAR_PICKUP_TRIES:
            self.pending = None
        if not mine:
            agent.search()
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
