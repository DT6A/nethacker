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
"""
import nle.nethack as nh
from nle.nethack import actions as A

from . import jf_config, utils
from .character import Character
from .glyph import G, MON, Hunger
from .level import Level
from .strategy import Strategy

TRIP_MIN_XL = 6                 # Minetown wants XL 6-8 (the dive trigger is XL 7 with a pick-axe, XL 8 without)
TRIP_TOTAL_TURNS = 9000         # the whole trip, from its start to the hand-over
BRANCH_TURNS = 3000             # looking for the Mines branch on Dlvl 2-4
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
# the level's '<' and the way back up took 500+ turns instead of ~120: 5 deaths on the way back against 0-1
ALTAR_PICKUP_TRIES = 4
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
        self._pickup_tries = 0
        self.donations = 0
        self.protection = 0
        self._donate_tries = 0
        self._priest_off = False       # no priest to talk to / he refused / protection capped
        self._priest_wait = 0
        self.end_reason = None
        self._filler = set()           # Mines level 3/4 keys judged not to be the town
        self._unblock_turn = {}        # level key -> last turn unblock() acted there
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
        if self.in_town() and self.orcish(level):
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
        if self.unblock(G.STAIR_UP):
            if agent.step_count == before:
                agent.search()
            return True
        dive.return_to_main_dungeon()
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
        if not dive.exploration(0).until(agent, dive._budgeted(found)).run(return_condition=True):
            dive.exploration(None).until(agent, dive._budgeted(found)).run()
        if agent.step_count == before:
            agent.search()
        return True

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
