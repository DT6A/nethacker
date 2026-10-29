# hypothesis: combination 2 of round 5 -- the strongest individual ideas of the round, which fix independent failures:
#   #140 (recover from an agent-thread exception instead of idling on ESC to the no-progress cutoff), #139 (detect a
#   refused kick instead of a zero-time door-kick loop), #152 (answer the controlled-teleport prompt once), #156 (a
#   Sokoban push blocked by a monster -- usually the pet -- waits / re-syncs instead of breaking the solver) and #171
#   (retreat up a nearby '<' at low HP once prayer is spent). The first four keep the strong XL 10+ games alive and
#   progressing through Sokoban; #171 attacks the early melee losses. They touch different code paths, so they stack.
# sources: round ideas #139, #140, #152, #156, #171 (/board/round_ideas/node-<n>.diff)
# hypothesis: combination of the round's best chain (#45 armour, #48 Elbereth vs @/minotaur, #56 blind/confused fight-back) with #78 (Sokoban map indent), #58 (pray.c critically_low_hp), #77 (no Sokoban pick-axe) and #70 (WEAK_MONSTERS name test): each touches its own code path, so together they add armour use, survival in early fights and a Sokoban solver that replays.
# sources: round ideas #45, #48, #56 (chain to node #56), #78, #58, #77, #70 (/board/round_ideas/node-<n>.diff); each change keeps its own hypothesis and sources comment.
from enum import IntEnum, auto

import nle.nethack as nh
import numpy as np
from nle.nethack import actions as A

from . import objects as O
from . import soko_solver
from . import utils
from .character import Character
from .combat.monster_utils import WEAK_MONSTERS, ONLY_RANGED_SLOW_MONSTERS
from .exceptions import AgentPanic
from .glyph import Hunger, C, G, MON
from .item import Item, flatten_items
from .item.item_priority_base import ItemPriorityBase
from .level import Level
from .strategy import Strategy


class ItemPriority(ItemPriorityBase):
    MAX_NUMBER_OF_ITEMS = 26 * 2 - 1  # + coin slot, one slot should be left for item arranging
    def __init__(self, agent):
        self.agent = agent
        self._take_sacrificial_corpses = False
        self._drop_gold_till_turn = -float('inf')

    def _split(self, items, forced_items, weight_capacity):
        remaining_weight = weight_capacity
        ret_inv = {}
        for item in forced_items:
            remaining_weight -= item.weight()
            ret_inv[item] = item.count

        ret_bag = {}
        bag = None

        def add_item(item, count=None, to_bag=False):
            nonlocal ret_inv, ret_bag, remaining_weight
            assert isinstance(item, Item)
            if to_bag and bag is not None and item is not bag:
                ret = ret_bag
            else:
                ret = ret_inv

            if remaining_weight < 0 or \
                    (ret is ret_inv and len(ret) >= ItemPriority.MAX_NUMBER_OF_ITEMS):  # TODO: coin slot
                return

            how_many_already_total = ret_inv.get(item, 0) + ret_bag.get(item, 0)
            how_many_already = ret.get(item, 0)
            max_to_add = int(remaining_weight // item.unit_weight(with_content=False))
            if count is not None:
                max_to_add = min(max_to_add, count)
            ret[item] = min(item.count, how_many_already_total + max_to_add) - (how_many_already_total - how_many_already)
            remaining_weight -= item.unit_weight(with_content=False) * (ret[item] - how_many_already)

        for item in items:
            if item.is_container() and item.status in [Item.UNCURSED, Item.BLESSED] and item.objs[0].desc == 'bag':
                bag = item  # TODO: select the best
                add_item(bag)

        # the Sokoban prize may be a bag of holding of unknown (or cursed) status; nothing is ever put in a bag (to_bag is
        # always False), so carrying it is safe, and picking it up is what records the prize (see sokoban_top_done)
        if self.agent.current_level().dungeon_number == Level.SOKOBAN:
            for item in items:
                if item is not bag and item.is_container() and item.objs[0].desc == 'bag':
                    add_item(item)
            # the other half of the Sokoban prize: no random amulet is generated on a Sokoban level (sokoban.des lists
            # only '%', '=' and '/' random objects), so an amulet here is the amulet of reflection and is taken first,
            # before weight limits fill up (a heavy hero declined it in a traced parent game).
            # sources: NetHack 3.6.6 dat/sokoban.des (soko1-1/soko1-2 prize: bag of holding or amulet of reflection);
            #   src/invent.c addinv_core1() (the Sokoban prize achievement is recorded on pickup);
            #   https://nethackwiki.com/wiki/Sokoban#Prize
            for item in items:
                if item.category == nh.AMULET_CLASS:
                    add_item(item)
        # the prize amulet (or any amulet known to be reflection / life saving) is kept first everywhere else too, so a
        # heavy hero does not drop it for heavier loot before wear_good_amulet puts it on
        for item in items:
            if self.agent.current_level().dungeon_number != Level.SOKOBAN and \
                    self.agent.global_logic.is_good_amulet(item):
                add_item(item)

        if self._drop_gold_till_turn < self.agent.blstats.time:
            for item in items:
                if item.category == nh.COIN_CLASS:
                    add_item(item)

        for allow_unknown_status in [False, True]:
            item = self.agent.inventory.get_best_melee_weapon(items=forced_items + items,
                                                              allow_unknown_status=allow_unknown_status)
            if item is not None:
                add_item(item)

            for item in self.agent.inventory.get_best_armorset(items=forced_items + items,
                                                               allow_unknown_status=allow_unknown_status):
                if item is not None:
                    add_item(item)

        for item in items:
            if item.is_unambiguous():
                if item.object in [
                        O.from_name('healing', nh.POTION_CLASS),
                        O.from_name('extra healing', nh.POTION_CLASS),
                        O.from_name('full healing', nh.POTION_CLASS)]:
                    add_item(item)

                if self.agent.character.role in [Character.RANGER, Character.ROGUE,
                                                 Character.SAMURAI, Character.TOURIST] and \
                        (item.is_launcher() or item.is_fired_projectile()):
                    add_item(item)

        if self.agent.character.alignment == Character.LAWFUL:
            for item in sorted(filter(lambda i: i.objs[0].name == 'long sword', items),
                               key=lambda i: -utils.calc_dps(*self.agent.character.get_melee_bonus(i))):
                add_item(item)
                break

        for item in sorted(filter(lambda i: i.is_thrown_projectile(), items),
                           key=lambda i: -utils.calc_dps(*self.agent.character.get_ranged_bonus(None, i))):
            add_item(item)

        for item in sorted(filter(lambda i: i.is_food() and not i.is_corpse(), items),
                           key=lambda x: -x.nutrition_per_weight() - 1000 * (x.objs[0].name == 'sprig of wolfsbane')):
            add_item(item)

        # keep one lizard corpse (weight 10, never rots): the bite that cures stoning (agent.cure_stoning)
        lizard_id = MON.from_name('lizard') - nh.GLYPH_MON_OFF
        if not any(i.is_corpse() and i.monster_id == lizard_id for i in forced_items):
            for item in filter(lambda i: i.is_corpse() and i.monster_id == lizard_id, items):
                add_item(item, count=1)
                break

        # gray stones: only ones already held or proven light by kick_test_gray_stones (never an unknown one, it may be
        # a cursed 500-weight loadstone that cannot be dropped); they weigh 10, not the 500 unit_weight() assumes
        held = flatten_items(self.agent.inventory.items)
        for item in items:
            if item.is_gray_stone() and item.status != Item.CURSED and \
                    not (item.is_unambiguous() and item.object.name == 'loadstone') and \
                    (any(i is item for i in held) or self.agent.global_logic.is_kicked_gray_stone(item)) and \
                    remaining_weight >= 10 * item.count and len(ret_inv) < ItemPriority.MAX_NUMBER_OF_ITEMS:
                ret_inv[item] = item.count
                remaining_weight -= 10 * item.count

        if self._take_sacrificial_corpses:
            for item in filter(self.agent.global_logic.can_sacrify, items):
                add_item(item)

        # TODO: take nh.COIN_CLASS once shopping is implemented.
        # You have to drop all coins not to be attacked by a vault guard

        for item in sorted(items, key=lambda i: i.unit_weight(with_content=False)):
            if item.category in [nh.POTION_CLASS, nh.RING_CLASS, nh.AMULET_CLASS, nh.WAND_CLASS, nh.SCROLL_CLASS, nh.TOOL_CLASS]:
                if (not isinstance(item.objs[0], O.Container) or not item.is_chest()) and \
                        not item.is_possible_container():
                    to_bag = O.from_name('cancellation', nh.WAND_CLASS) not in item.objs and \
                             not item.is_offensive_usable_wand()
                    to_bag = False
                    if not item.is_container():  # remove condition to pick up bags
                        add_item(item, to_bag=to_bag)

        categories = [nh.WEAPON_CLASS, nh.ARMOR_CLASS, nh.TOOL_CLASS, nh.FOOD_CLASS, nh.GEM_CLASS, nh.AMULET_CLASS,
                      nh.RING_CLASS, nh.POTION_CLASS, nh.SCROLL_CLASS, nh.SPBOOK_CLASS, nh.WAND_CLASS]
        for item in sorted(items, key=lambda i: i.unit_weight(with_content=False)):
            if item.category in categories and not isinstance(item.objs[0], O.Container) and not item.is_corpse() \
                    and not item.is_gray_stone():
                if item.status == Item.UNKNOWN:
                    to_bag = O.from_name('cancellation', nh.WAND_CLASS) not in item.objs and \
                             not item.is_offensive_usable_wand()
                    to_bag = False
                    if not item.is_container():  # remove condition to pick up bags
                        add_item(item, to_bag=to_bag)

        r = {None: [ret_inv.get(item, 0) for item in items]}
        if bag is not None:
            r[bag] = [ret_bag.get(item, 0) for item in items]
        for item in items:
            if item.is_container() and item is not bag and ret_inv.get(item, 0) != 0:
                r[item] = [0 for _ in items]
        return r


class Milestone(IntEnum):
    BE_ON_FIRST_LEVEL = auto()
    FIND_GNOMISH_MINES = auto()
    # FIND_LIGHT_GNOMISH_MINES = auto()
    # FARM_LIGHT_GNOMISH_MINES = auto()
    FIND_MINETOWN = auto()
    FIND_SOKOBAN = auto()
    SOLVE_SOKOBAN = auto()
    FIND_MINES_END = auto()
    GO_DOWN = auto() # TODO


class GlobalLogic:
    def __init__(self, agent):
        self.agent = agent
        self.milestone = Milestone(1)
        self._sokoban_stalls = {}
        self.step_completion_log = {}  # Milestone -> (step, turn)

        self.item_priority = ItemPriority(self.agent)

        self.oracle_level = None
        self.minetown_level = None

        self._got_artifact = False

        self._retreat_rest_level = None
        self._retreat_cooldown_until = 0

        self._soko_top_arrival_turn = None
        self._soko_top_traps_seen = False
        self._soko_top_items_check = (None, True)  # (turn, items left)
        self._soko_checked_boulders = {}  # level key -> set of (y, x) boulders already searched next to
        self._soko_progress = {}  # level key -> (index of the matched map, number of answer moves already done)
        self._soko_unreachable_waits = {}  # (level key, answer move index) -> rounds waited for its push square
        self._soko_throws = {}  # level key -> missiles thrown over a boulder at a monster blocking the push

        self._amulets_carried_off_soko_top = set()  # appearances (glyph tuples) of amulets held off the top level
        self._soko_top_new_amulets = set()  # appearances first obtained on the Sokoban top level
        self._amulet_rejected = set()  # appearances that could not be put on or strangled the hero
        self._strangle_prayer_turn = -float('inf')

        self._mines_grind = False  # the XL-8 grind has moved from the main dungeon to the upper Mines (see grind_level)
        self._grind_xl = None
        self._grind_xl_turn = 0  # turn when the hero reached its current experience level

    # hypothesis: SOLVE_SOKOBAN ends on arrival at the top level, because its only test is "no closed door in view" and
    # the premapped top level shows no closed door from the stairs until the solver has run, so the 3/15 public games
    # that reach it (seeds 6, 11, 14) leave it unsolved and never take the prize (+0.05 level, +0.25 prize). Ending the
    # milestone only once its holes are filled, no reachable closed door or unseen area is left (closets opened, zoo
    # cleared), no boulder-shaped giant mimic is left unchecked and nothing wanted lies on the floor makes the bot solve
    # the top level, clear the zoo and pick up the bag of holding / amulet of reflection; a 4000-turn cap and the stall
    # escalation in on_stall keep it from getting stuck there.
    # sources: /refs/history/153.diff + /refs/history/144.diff (#153/#144: this completion test, neutral in their chains
    # because no game reached the top level; here 3 public games do); https://nethackwiki.com/wiki/Sokoban (prize in a
    # top-level closet on a burnt Elbereth and a cursed scroll of scare monster, status random);
    # https://nethackwiki.com/wiki/Sokoban_Level_4a (zoo behind a locked door, closets on the left);
    # NetHack 3.6.6 dat/sokoban.des (soko1-1/soko1-2 are premapped and place two 'giant mimic' with m_object "boulder");
    # NetHack 3.6.6 src/invent.c addinv_core1 (the prize achievement is recorded when it enters the inventory)
    def sokoban_top_done(self):
        level = self.agent.current_level()
        if level.key() != (Level.SOKOBAN, 1):
            return False

        turn = self.agent.blstats.time
        if self._soko_top_arrival_turn is None:
            self._soko_top_arrival_turn = turn
        if turn - self._soko_top_arrival_turn > 4000:
            return True

        if utils.isin(level.objects, G.TRAPS).any():
            self._soko_top_traps_seen = True
            return False
        if not self._soko_top_traps_seen and turn - self._soko_top_arrival_turn < 200:
            return False

        # the same frontier explore1 visits: unseen stone and closed (not given up) doors next to a reachable square
        reachable = self.agent.bfs() != -1
        stone = ~level.seen & utils.isin(self.agent.glyphs, G.STONE)
        doors = utils.isin(self.agent.glyphs, G.DOOR_CLOSED) & (level.door_open_count < 4)
        to_visit = np.zeros_like(stone)
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy != 0 or dx != 0:
                    to_visit |= utils.translate(stone, dy, dx)
                    if dx == 0 or dy == 0:
                        to_visit |= utils.translate(doors, dy, dx)
        if (to_visit & reachable).any():
            return False

        if self._soko_mimic_targets():
            return False

        if self._soko_top_items_check[0] != turn:
            inventory = self.agent.inventory
            items_left = inventory.go_to_unchecked_containers().check_condition() or \
                         inventory.check_items().check_condition() or \
                         inventory.go_to_item_to_pickup().check_condition()
            self._soko_top_items_check = (turn, items_left)
        return not self._soko_top_items_check[1]

    def _soko_mimic_targets(self):
        # boulders on the solved top level that were not searched next to yet and have a reachable neighbour
        level = self.agent.current_level()
        if level.key() != (Level.SOKOBAN, 1) or utils.isin(level.objects, G.TRAPS).any():
            return []
        checked = self._soko_checked_boulders.setdefault(level.key(), set())
        dis = self.agent.bfs()
        targets = []
        for y, x in zip(*utils.isin(self.agent.glyphs, G.BOULDER).nonzero()):
            if (y, x) in checked:
                continue
            if any(dis[ny, nx] != -1 for ny, nx in self.agent.neighbors(y, x, shuffle=False)):
                targets.append((y, x, dis))
        return targets

    # hypothesis: both top Sokoban levels hide two giant mimics disguised as boulders; once the holes are filled the
    # solver no longer touches boulders, so a mimic left in the corridor to the zoo blocks it (the bot will not push a
    # "boulder" off the solved map) and one met by bumping it sticks to a level-10ish hero for 3d6/3d6 per turn. Searching
    # next to every reachable leftover boulder always reveals a disguised mimic (dosearch0 calls seemimic without a luck
    # roll), so fight2 fights it on the bot's terms and the path to the closets opens.
    # sources: NetHack 3.6.6 dat/sokoban.des (soko1-1/soko1-2: MONSTER 'giant mimic', random, m_object "boulder") and
    # src/detect.c dosearch0 (adjacent M_AP_OBJECT mimic -> seemimic, unconditional);
    # https://groups.google.com/g/rec.games.roguelike.nethack/c/WKAs-c0J7hg ("LEAVE the GIANT mimics ALONE!!!", player
    # discussion of Sokoban boulder mimics killing heroes); https://nethackwiki.com/wiki/Talk:Mimic (player discussion:
    # search to reveal boulder mimics in Sokoban); https://github.com/NetHack/NetHack/commit/13abd42d6ae674e9c2a079bf03066f59b9dfbfb8
    # and https://github.com/NetHack/NetHack/commit/e379b245d4ebd613957a1ddf1124d892041c0cb0 (mimic boulder disguise rules)
    @utils.debug_log('revealing sokoban mimics')
    @Strategy.wrap
    def reveal_sokoban_mimics_strategy(self):
        targets = self._soko_mimic_targets()
        if not targets:
            yield False
        yield True
        level = self.agent.current_level()
        checked = self._soko_checked_boulders.setdefault(level.key(), set())
        y, x, dis = min(targets, key=lambda t: min(t[2][ny, nx] for ny, nx in self.agent.neighbors(t[0], t[1], shuffle=False)
                                                   if t[2][ny, nx] != -1))
        checked.add((y, x))
        if not utils.adjacent((self.agent.blstats.y, self.agent.blstats.x), (y, x)):
            self.agent.go_to(y, x, stop_one_before=True)
        if utils.adjacent((self.agent.blstats.y, self.agent.blstats.x), (y, x)):
            self.agent.search(3)

    # hypothesis: a Sokoban push blocked by a monster the hero cannot see ("You hear a monster behind the boulder.") was
    #   only waited out: 15 searches per try, 5 tries, then the whole level was dropped. A hostile on the far side keeps
    #   the square behind the boulder because it is the closest it can get to the hero (it cannot pass the boulder),
    #   and a giant mimic (two on each top level) never moves at all, so the wait never ends: in 2 of 4 traced parent
    #   games that reached the top level (soko1-2, the x=10 corridor to the zoo) the bot dropped it this way and never
    #   got the prize (+0.05 level, +0.25 prize). Boulders stop no thrown object (only a heavy iron ball), so a missile
    #   thrown in the push direction flies over the boulder and hits the blocker: it dies, flees or is revealed, and the
    #   push goes through. Never thrown when the hero's pet may be the blocker (a pet was seen on this level and is not
    #   in view elsewhere), at a peaceful or tame monster in view, or while confused, stunned or hallucinating.
    # sources: NetHack 3.6.6 src/zap.c bhit() (range loop: only a HEAVY_IRON_BALL "hits a boulder" and stops) and
    #   src/hack.c moverock() ("You hear a monster behind %s." / "Perhaps that's why you cannot move it.", no time
    #   passes); src/monmove.c m_move() (an approaching monster only steps nearer to the hero);
    #   NetHack 3.6.6 dat/sokoban.des (soko1-1/soko1-2: two MONSTER 'giant mimic' m_object "boulder", zoo, prize);
    #   https://nethackwiki.com/wiki/Sokoban ("a monster may be standing behind the boulder"); https://nethackwiki.com/wiki/Boulder ;
    #   https://nethackwiki.com/wiki/Giant_mimic ; parent seed traces (diagnostic logging of
    #   the top level: 75x "You hear a monster behind the boulder" at the same square, then the level was dropped)
    def _throw_over_boulder(self, ty, tx, dy, dx, message):
        prop = self.agent.character.prop
        if prop.confusion or prop.stun or prop.hallu or prop.polymorph:
            return False
        level = self.agent.current_level()
        if level.dungeon_number != Level.SOKOBAN:
            return False
        by, bx = ty + 2 * dy, tx + 2 * dx
        if not (0 <= by < C.SIZE_Y and 0 <= bx < C.SIZE_X):
            return False
        pet_in_view = utils.isin(self.agent.glyphs, G.PETS)
        if pet_in_view[by, bx] or self.agent.monster_tracker.peaceful_monster_mask[by, bx]:
            return False
        if 'a monster behind' in message and level.key() in self.agent.pet_seen_levels and not pet_in_view.any():
            return False  # the unseen blocker may be the hero's own pet
        throws = self._soko_throws.get(level.key(), 0)
        if throws >= 40:
            return False
        inventory = self.agent.inventory
        ammo_list = [ammo for launcher, ammo in inventory.get_ranged_combinations() if launcher is None]
        if not ammo_list:
            return False
        ammo = max(ammo_list, key=lambda i: utils.calc_dps(*self.agent.character.get_ranged_bonus(None, i)))
        self._soko_throws[level.key()] = throws + 1
        direction = self.agent.calc_direction(ty, tx, ty + dy, tx + dx)
        return self.agent.fire(ammo, direction)

    def update(self):
        self._track_sokoban_prize_amulet()
        self._update_mines_grind()
        if not self.agent.character.prop.hallu:
            if utils.isin(self.agent.glyphs, G.ORACLE).any():
                if self.oracle_level is None:
                    self.oracle_level = self.agent.current_level().key()
                else:
                    assert self.oracle_level == self.agent.current_level().key()

            if self.agent.current_level().dungeon_number == Level.GNOMISH_MINES and \
                    utils.isin(self.agent.glyphs, G.SHOPKEEPER).any():
                if self.minetown_level is None:
                    self.minetown_level = self.agent.current_level().key()
                else:
                    assert self.minetown_level == self.agent.current_level().key()

    @utils.debug_log('solving sokoban')
    @Strategy.wrap
    def solve_sokoban_strategy(self):
        # TODO: refactor
        if not utils.isin(self.agent.current_level().objects, G.TRAPS).any():
            yield False
        yield True

        # hypothesis: the strongest games (XL 10+) freeze alive in Sokoban (parent #141 public seeds 0, 4, 6 end at
        # end_status -1) because a push blocked by a monster on the far side of the boulder -- most often the hero's
        # own pet, which follows it through the corridors -- broke the solver: the visible case ("There's a kitten on
        # the other side. Perhaps that's why you cannot move it.") failed the message assert and killed the agent
        # thread, and the hidden case desynced the model and retried a zero-time push until the 'turn inactivity'
        # assert did. Waiting a few turns for the monster to step away, replaying the answer from the real boulders
        # after a failed push, and waiting (not dropping the level) while the next push square is only occupied by a
        # monster lets the bot solve the levels (+0.05 each, the prize, the zoo's XP) and keep growing; a level whose
        # pushes keep failing is dropped cleanly instead of freezing the game.
        # sources: NetHack 3.6.6 src/hack.c moverock() ("There's %s on the other side." / "You hear a monster behind
        # %s." + "Perhaps that's why you cannot move it.", and "You try to move %s, but in vain."; all goto cannot_push,
        # which takes no game time); https://nethackwiki.com/wiki/Sokoban (in 3.6.6 a pet may stand opposite a boulder;
        # pets avoid that square only from 3.7.0); https://nethackwiki.com/wiki/Boulder ;
        # https://groups.google.com/d/topic/rec.games.roguelike.nethack/WKAs-c0J7hg (pet stuck behind a Sokoban boulder:
        # wait for it); /refs/history/137.diff and /refs/history/154.diff (#137 / #154, same fix on other chains)
        def push_bolder(ty, tx, dy, dx):
            blocked = 0
            other = 0
            while 1:
                if self.agent.bfs()[ty, tx] == -1:
                    return False
                self.agent.go_to(ty, tx, debug_tiles_args=dict(color=(255, 255, 255), is_path=True))
                with self.agent.atom_operation():
                    direction = self.agent.calc_direction(ty, tx, ty + dy, tx + dx)
                    self.agent.direction(direction)
                    message = self.agent.message

                if (self.agent.blstats.y, self.agent.blstats.x) == (ty, tx):
                    if 'Perhaps that\'s why' in message or 'on the other side' in message or \
                            'a monster behind' in message:
                        # a monster stands where the boulder has to go: let it move away (a pet wanders off,
                        # a hostile walks around and fight2 takes it)
                        blocked += 1
                        if blocked > 15:
                            return False
                        if blocked >= 3 and self._throw_over_boulder(ty, tx, dy, dx, message):
                            continue
                        self.agent.search()
                        continue
                    if 'You try to move the boulder, but in vain.' not in message and other < 3:
                        # no push happened at all (interrupted on the way): try again
                        other += 1
                        continue
                    if self.agent.bfs()[ty + dy, tx + dx] != -1 and other < 3:
                        other += 1
                        self.agent.go_to(ty + dy, tx + dx, debug_tiles_args=dict(color=(255, 255, 255), is_path=True))
                        continue
                    # hypothesis: a blocked Sokoban push must not be solved by breaking the boulder with a pick-axe: that is forbidden, and it costs -1 Luck until the level is solved, which blocks successful prayer.
                    # sources: https://nethackwiki.com/wiki/Sokoban (Luck penalties: breaking a boulder; stuck boulders: destroy a boulder with a pick-axe, force bolt or wand of striking is a luck penalty); https://nethackwiki.com/wiki/Luck (negative Luck blocks prayer results); https://nethackwiki.com/wiki/Pick-axe (applying a pick-axe to a stuck boulder costs -1 Luck in Sokoban); https://nethack.fandom.com/wiki/Sokoban
                    return False
                else:
                    return True

        def drop_level():
            self.agent.stats_logger.log_event('sokoban_dropped')
            self.milestone = Milestone(int(self.milestone) + 1)
            raise AgentPanic('sokomap unsolvable')

        # hypothesis: the solver forgot where it was in the answer: every preemption (fight2, eating, a panic) restarts
        # this strategy, which replayed the answer from move 0 and executed the first move whose boulder "looked"
        # present -- a subset test that is almost always true once boulders have dropped into holes -- so it pushed
        # boulders back along their path and deadlocked the level (parent public seed 8: after a fight in soko4-2 it
        # pushed the corridor boulder back left, packed two boulders in the row-2 corridor and dropped the level;
        # 4 of the 8 public games that enter Sokoban never finish its first level). Keeping the answer index per
        # level and fast-forwarding the model to it on every restart makes the replay resume where it stopped; a
        # needed push whose square is out of reach (a monster in the corridor) is waited for instead of skipped,
        # because a skipped push leaves its boulder behind for good. Expected: more Sokoban levels solved (+0.05
        # each), more games at the top level for #180's prize logic (+0.25), and the zoo's experience.
        # sources: offline replay of all 8 answers in soko_solver/maps.py against NetHack 3.6.6 dat/sokoban.des
        # (real boulders, pits and holes; https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/dat/sokoban.des):
        # restarting from move 0 after every push leaves 6/8 levels unsolved (soko4-2 even when restarting every 10
        # pushes), resuming from the saved index solves 8/8 with every push square reachable; parent seed 8 trace
        # (pushes logged per move); https://nethackwiki.com/wiki/Sokoban (boulders fill pits/holes and vanish);
        # https://nethackwiki.com/wiki/Sokoban_Level_1a / Sokoban_Level_1b
        level_key = self.agent.current_level().key()
        failed_pushes = 0
        blocked_rounds = 0
        while 1:
            wall_map = utils.isin(self.agent.current_level().objects, G.WALL)
            for map_index, (smap, answer) in enumerate(soko_solver.maps.items()):
                sokomap = soko_solver.convert_map(smap)
                offset = np.array(min(zip(*wall_map.nonzero()))) - \
                         np.array(min(zip(*(sokomap.sokomap == soko_solver.WALL).nonzero())))
                mask = wall_map[offset[0] : offset[0] + sokomap.sokomap.shape[0],
                                offset[1] : offset[1] + sokomap.sokomap.shape[1]]
                if (mask & (sokomap.sokomap == soko_solver.WALL) == mask).all():
                    break
            else:
                assert 0, 'sokomap not found'

            saved_map, done_moves = self._soko_progress.get(level_key, (map_index, 0))
            if saved_map != map_index:
                done_moves = 0

            possible_mimics = set()
            last_resort_move = None
            resync = False
            step_blocked = False
            push_unreachable = False
            for move_index, ((y, x), (dy, dx)) in enumerate(answer):
                if move_index < done_moves:
                    # already made (or its boulder already dropped into a hole) before this restart
                    sokomap.move(y, x, dy, dx)
                    continue
                boulder_map = utils.isin(self.agent.glyphs, G.BOULDER)
                mask = boulder_map[offset[0] : offset[0] + sokomap.sokomap.shape[0],
                                   offset[1] : offset[1] + sokomap.sokomap.shape[1]]
                ty, tx = offset[0] + y - dy, offset[1] + x - dx,
                soko_boulder_mask = sokomap.sokomap == soko_solver.BOULDER
                if self.agent.bfs()[ty, tx] != -1 and \
                        ((soko_boulder_mask | mask) == soko_boulder_mask).all() and \
                        self.agent.glyphs[ty + dy, tx + dx] in G.BOULDER:

                    soko_dis1 = sokomap.bfs()
                    sokomap.move(y, x, dy, dx)
                    soko_dis2 = sokomap.bfs()

                    # see points that will no longer be accessible
                    with self.agent.env.debug_log('checking for monsters'):
                        to_visit_mask = self.agent.bfs() != -1
                        to_visit_mask[offset[0] : offset[0] + sokomap.sokomap.shape[0],
                                      offset[1] : offset[1] + sokomap.sokomap.shape[1]] &= \
                                              (soko_dis1 != -1) & (soko_dis2 == -1)

                        with self.agent.env.debug_tiles(to_visit_mask, color=(255, 0, 0, 128)):
                            while to_visit_mask.any():
                                vy, vx = list(zip(*to_visit_mask.nonzero()))[0]
                                to_visit_mask[vy, vx] = 0

                                def clear_neighbors():
                                    to_visit_mask[self.agent.blstats.y, self.agent.blstats.x] = 0
                                    to_visit_mask[utils.isin(self.agent.glyphs, G.VISIBLE_FLOOR)] = 0
                                    return not to_visit_mask[vy, vx]

                                self.agent.go_to(vy, vx, callback=clear_neighbors)

                    if not push_bolder(ty, tx, dy, dx):
                        # the model already made this push: replay the answer again from the real boulders
                        # instead of walking on with a desynced model (and give up after repeated failures)
                        failed_pushes += 1
                        if failed_pushes >= 5:
                            drop_level()
                        resync = True
                        break

                    failed_pushes = 0
                    blocked_rounds = 0
                    possible_mimics = set()
                    last_resort_move = None
                    self._soko_progress[level_key] = (map_index, move_index + 1)

                    if not utils.isin(self.agent.current_level().objects, G.TRAPS).any():
                        return

                else:
                    if ((soko_boulder_mask | mask) == soko_boulder_mask).all() and \
                            self.agent.glyphs[ty + dy, tx + dx] in G.BOULDER and \
                            self.agent.bfs()[ty, tx] == -1 and \
                            (self.agent.glyphs[ty, tx] in G.MONS or self.agent.glyphs[ty, tx] in G.PETS):
                        # this is the push to make now, but a monster stands on its square
                        step_blocked = True
                    if ((soko_boulder_mask | mask) == soko_boulder_mask).all() and \
                            self.agent.glyphs[ty + dy, tx + dx] in G.BOULDER and \
                            self.agent.bfs()[ty, tx] == -1 and \
                            self._soko_unreachable_waits.get((level_key, move_index), 0) < 10:
                        # the boulder of the next move is still there but its push square is out of reach (a monster
                        # in the corridor): skipping it would leave this boulder behind for good, so wait
                        push_unreachable = True
                        self._soko_unreachable_waits[(level_key, move_index)] = \
                            self._soko_unreachable_waits.get((level_key, move_index), 0) + 1
                        break
                    sokomap.move(y, x, dy, dx)

                if (~soko_boulder_mask | mask).all():
                    if self.agent.bfs()[ty, tx] != -1 and \
                            self.agent.glyphs[ty + dy, tx + dx] in G.BOULDER and \
                            last_resort_move is None:
                        last_resort_move = (ty, tx, dy, dx, move_index)

                    if not possible_mimics:
                        for mim_y, mim_x in zip(*(~soko_boulder_mask & mask).nonzero()):
                            possible_mimics.add((mim_y + offset[0], mim_x + offset[1]))

            if resync:
                continue

            if push_unreachable:
                for _ in range(3):
                    self.agent.search()
                continue

            if step_blocked and blocked_rounds < 20:
                # wait for the monster to move off the push square instead of dropping the level
                blocked_rounds += 1
                for _ in range(3):
                    self.agent.search()
                continue

            # sokoban configuration is not in the list. Check for mimics
            with self.agent.env.debug_log('mimics'):
                with self.agent.env.debug_tiles(possible_mimics, color=(255, 0, 0, 128)):
                    for mim_y, mim_x in sorted(possible_mimics):
                        if (self.agent.bfs()[max(0, mim_y - 1) : mim_y + 2, max(0, mim_x - 1) : mim_x + 2] != -1).any():
                            self.agent.go_to(mim_y, mim_x, stop_one_before=True,
                                             debug_tiles_args=dict(color=(255, 0, 0), is_path=True))
                            for _ in range(3):
                                self.agent.search()

            # last resort move (sometimes we can see a mimic diagonally but cannot reach it)
            with self.agent.env.debug_log('last_resort'):
                if last_resort_move is not None:
                    ty, tx, dy, dx, move_index = last_resort_move
                    if push_bolder(ty, tx, dy, dx):
                        failed_pushes = 0
                        self._soko_progress[level_key] = (map_index, move_index + 1)
                        continue
                    failed_pushes += 1
                    if failed_pushes < 5:
                        continue

            drop_level()

    def on_stall(self):
        # called by Agent.handle_exception after an unexpected error was recovered (see the hypothesis there):
        # a stall that comes back on the same Sokoban level is a push the solver cannot make, so drop Sokoban
        # the way the 'sokomap unsolvable' path does instead of looping at zero game time
        level = self.agent.current_level()
        if self.milestone != Milestone.SOLVE_SOKOBAN or level.dungeon_number != Level.SOKOBAN:
            return
        key = level.key()
        self._sokoban_stalls[key] = self._sokoban_stalls.get(key, 0) + 1
        if self._sokoban_stalls[key] >= 3:
            self.agent.stats_logger.log_event('sokoban_dropped')
            self.milestone = Milestone(int(self.milestone) + 1)

    def _track_sokoban_prize_amulet(self):
        amulets = {tuple(item.glyphs) for item in flatten_items(self.agent.inventory.items)
                   if item.category == nh.AMULET_CLASS}
        if self.agent.current_level().key() == (Level.SOKOBAN, 1):
            self._soko_top_new_amulets |= amulets - self._amulets_carried_off_soko_top
        else:
            self._amulets_carried_off_soko_top |= amulets

    def _worn_amulet(self):
        return next((item for item in flatten_items(self.agent.inventory.items)
                     if item.category == nh.AMULET_CLASS and item.equipped), None)

    def is_good_amulet(self, item):
        if item.category != nh.AMULET_CLASS or tuple(item.glyphs) in self._amulet_rejected:
            return False
        if item.is_unambiguous():
            return item.object.name in ('amulet of reflection', 'amulet of life saving')
        # the one appearance first obtained on the Sokoban top level is the prize (an amulet of reflection); two
        # different new appearances there (a zoo monster's random drop) leave it unknown
        return len(self._soko_top_new_amulets) == 1 and tuple(item.glyphs) in self._soko_top_new_amulets and \
            O.from_name('amulet of reflection', nh.AMULET_CLASS) in item.objs

    # hypothesis: my parent takes the Sokoban prize amulet first but the bot never puts an amulet on, so the prize
    # amulet of reflection rides in the pack while the strongest heroes die to rays and wand bolts (parent: "killed by a
    # bolt of fire" at XL 11 on public seed 12, "killed by a death ray" at XL 10 on dev seed 917616). The prize is
    # always reflection, stays unidentified until it reflects something, and still reflects when cursed, so the hero
    # puts on the one amulet appearance first obtained on the Sokoban top level (and any amulet identified as
    # reflection or life saving) as soon as no hostile is adjacent; random unknown amulets stay off (13.5% are
    # strangulation). Reflection is the wiki's must-have before Dlvl 15, Medusa and the Castle.
    # sources: REUSES #337 (/refs/history/337.diff, the wear half; +0.008 over its root there) and #312;
    #   https://nethackwiki.com/wiki/Amulet_of_reflection (3.6: the soko1 prize is 50% an amulet of reflection; rays
    #   bounce off with no damage; breath and wand defence) ; https://nethackwiki.com/wiki/Amulet (the Sokoban prize
    #   identifies it; once strangulation/restful sleep are ruled out even a cursed amulet is safe to wear) ;
    #   https://www.alt.org/nethack/mirror/www.steelypips.org/nethack/id_faq.html (the Sokoban prize is fixed) ;
    #   https://nethackwiki.com/wiki/Wand_of_death (only magic resistance or reflection stops a death ray) ;
    #   NetHack 3.6.6 dat/sokoban.des (soko1-2 "amulet of reflection"), src/do_wear.c Amulet_on
    @utils.debug_log('wear_good_amulet')
    @Strategy.wrap
    def wear_good_amulet(self):
        if self._worn_amulet() is not None or self._hostile_adjacent() or self.agent.character.prop.polymorph:
            yield False
        candidates = [item for item in flatten_items(self.agent.inventory.items) if self.is_good_amulet(item)]
        if not candidates:
            yield False
        yield True
        item = max(candidates, key=lambda i: i.is_unambiguous() and i.object.name == 'amulet of reflection')
        key = tuple(item.glyphs)
        if not self.agent.inventory.put_on(item):
            self._amulet_rejected.add(key)
        else:
            self.agent.stats_logger.log_event('wear_amulet')

    # hypothesis: if a worn amulet turns out to be strangulation ("It constricts your throat!", status Strngl: death in
    # six turns) it comes off at once; a cursed one leaves prayer (strangulation is a major trouble) as the only cure.
    # sources: https://nethackwiki.com/wiki/Amulet_of_strangulation ; https://nethackwiki.com/wiki/Prayer (major
    #   trouble) ; NetHack 3.6.6 src/pray.c in_trouble() TROUBLE_STRANGLED ; /refs/history/337.diff (#337)
    @utils.debug_log('remove_strangling_amulet')
    @Strategy.wrap
    def remove_strangling_amulet(self):
        worn = self._worn_amulet()
        cond = int(self.agent.last_observation['blstats'][nh.NLE_BL_CONDITION])
        if worn is None or not (cond & nh.BL_MASK_STRNGL):
            yield False
        if worn.status == Item.CURSED and self.agent.blstats.time - self._strangle_prayer_turn < 10:
            yield False  # prayed already: removing a cursed amulet takes no time, so do not loop on it
        yield True
        self._amulet_rejected.add(tuple(worn.glyphs))
        if not self.agent.inventory.remove_accessory(worn):
            # cursed: the hero dies in six turns anyway, so pray even if the timeout looks too high
            self._strangle_prayer_turn = self.agent.blstats.time
            self.agent.pray()

    def _hostile_adjacent(self):
        y, x = self.agent.blstats.y, self.agent.blstats.x
        return any(utils.adjacent((y, x), (my, mx)) for _, my, mx, *_ in self.agent.get_visible_monsters())

    # hypothesis: a blind, confused, stunned, hallucinating or polymorphed hero that is being hit searches in place until the status ends (a yellow light blinds for 10d20 turns), so the adjacent monster kills it without a blow back or a prayer; yielding to fight2 and emergency_strategy as soon as a hostile is adjacent (and waiting again once none is) stops that passive death.
    # sources: https://nethackwiki.com/wiki/Blindness (monsters that attack a blind hero are marked with an I; moving into or searching next to an I attacks it) ; https://nethackwiki.com/wiki/Yellow_light (explosion blinds for 10d20 turns) ; https://nethackwiki.com/wiki/Talk:Blindness (player discussion: moving into an I marker attacks it without confirmation) ; https://www.quartertothree.com/fp/2011/05/23/nethack-dead-again/ (player blinded by a yellow light, killed while wandering blind) ; /refs/history/32 (same yield-out-of-the-wait fix, +0.014 on its own parent)
    @Strategy.wrap
    def wait_out_unexpected_state_strategy(self):
        yielded = False
        while (
                self.agent.character.prop.blind or
                self.agent.character.prop.confusion or
                self.agent.character.prop.stun or
                self.agent.character.prop.hallu or
                self.agent.character.prop.polymorph):
            if self._hostile_adjacent():
                break
            if not yielded:
                yield True
                yielded = True

            self.agent.direction('.')

        if not yielded:
            yield False

    @utils.debug_log('identify_items_on_altar')
    @Strategy.wrap
    def identify_items_on_altar(self):
        mask = utils.isin(self.agent.current_level().objects, G.ALTAR)
        if not mask.any():
            yield False

        dis = self.agent.bfs()
        mask &= dis != -1
        if not mask.any():
            yield False

        yield any((item.status == Item.UNKNOWN for item in flatten_items(self.agent.inventory.items)
                   if item.can_be_dropped_from_inventory()))

        (ty, tx), *_ = zip(*(mask & (dis == dis[mask].min())).nonzero())
        self.agent.go_to(ty, tx)
        items_to_drop = [item for item in flatten_items(self.agent.inventory.items)
                         if item.can_be_dropped_from_inventory() and item.status == Item.UNKNOWN]
        if not items_to_drop:
            raise AgentPanic('items to drop on altar vanished')

        # TODO: move chunking to inventory.drop
        items_to_drop = items_to_drop[:self.agent.inventory.items.free_slots()]

        self.agent.inventory.drop(items_to_drop)

    def may_kick_doors_here(self):
        # Mines' End (and every Mines level below Minetown, which is Mines level 3 or 4) has no watch, so its locked
        # doors -- the Mimic of the Mines luckstone niches -- may be kicked open like Dungeons ones
        level = self.agent.current_level()
        return level.dungeon_number != Level.GNOMISH_MINES or \
            (level.level_number >= 5 and level.key() != self.minetown_level)

    GRAY_STONE_GLYPHS = frozenset(O.desc_to_glyphs('gray', nh.GEM_CLASS))  # one look ("gray stone") for all four

    def is_kicked_gray_stone(self, item):
        level = self.agent.current_level()
        for y, x in level.light_gray_stones:
            here = list(level.items[y, x])
            if (y, x) == (self.agent.blstats.y, self.agent.blstats.x) and self.agent.inventory.items_below_me:
                here += list(self.agent.inventory.items_below_me)
            if any(i is item for i in flatten_items(here)):
                return True
        return False

    # hypothesis: Mines' End always holds the uncursed Mines prize luckstone (Luck +3 while carried: to-hit, prayer
    #   success and a buffer against bad Luck, plus the luckstone loot bonus), but the bot never gets it (mines_prize in
    #   0/20 parent games and 0 tree games, although 15/20 finish the Sokoban leg before FIND_MINES_END, and with an
    #   8-level Mines the bot keeps exploring and searching Mines' End for a '>' it never finds): the Mimic of the Mines niches
    #   are behind locked doors it never kicks in the Mines, and a floor gray stone looks the same whether it is the
    #   luckstone or the cursed, undroppable 500-weight loadstone beside it. Players tell them apart without touching
    #   them: kick the stone with free floor behind it -- a loadstone gives "Thump!" (STR/2 - weight/40 < 2), any
    #   other gray stone slides away; then pick up only the stone that moved.
    # sources: https://nethackwiki.com/wiki/Loadstone ; https://nethackwiki.com/wiki/Gray_stone ;
    #   https://nethackwiki.com/wiki/Mines%27_End ; https://nethackwiki.com/wiki/Luckstone ;
    #   player discussions https://nethackwiki.com/wiki/Forum:Mine's_end and GameFAQs "How to get past the level
    #   teleport traps in Mine's End?" (gamefaqs.gamespot.com/boards/582497-nethack/60864842, search excerpts:
    #   "if the gray stone was the topmost object on the pile, then yes, it is a loadstone", kicking it into a wall
    #   also thumps); NetHack 3.6 dokick.c really_kick_object(), dat/mines.des minend-1..3, dat/dungeon.def
    @utils.debug_log('kick_test_gray_stones')
    @Strategy.wrap
    def kick_test_gray_stones(self):
        level = self.agent.current_level()
        if level.dungeon_number != Level.GNOMISH_MINES or level.level_number < 8:
            yield False

        def ray(y, x, dy, dx):
            for k in range(1, 15):
                y, x = y + dy, x + dx
                if not (0 <= y < C.SIZE_Y and 0 <= x < C.SIZE_X) or not level.walkable[y, x]:
                    return
                yield y, x

        if level.gray_stone_ray is not None:
            # follow the kicked stone: it slid along the kick direction (often into the dark) and stopped somewhere
            (sy, sx), (dy, dx), older, tries = level.gray_stone_ray
            if tries >= 3:
                level.gray_stone_ray = None
                yield False
            yield True
            level.gray_stone_ray = ((sy, sx), (dy, dx), older, tries + 1)
            for y, x in ray(sy, sx, dy, dx):
                if self.agent.bfs()[y, x] == -1:
                    break
                self.agent.go_to(y, x)
                if (y, x) not in older and \
                        any(i.is_gray_stone() for i in flatten_items(self.agent.inventory.items_below_me)):
                    level.light_gray_stones.add((y, x))
                    break
            level.gray_stone_ray = None
            return

        if self.agent.blstats.time < self.agent._no_kick_until:
            yield False

        dis = self.agent.bfs()
        best = None
        for y, x in zip(*utils.isin(self.agent.glyphs, self.GRAY_STONE_GLYPHS).nonzero()):
            if (y, x) in level.light_gray_stones or level.shop[y, x] or level.shop_interior[y, x] or \
                    level.gray_stone_kicks[y, x] >= 3:
                continue
            # orthogonal kicks only, from a reachable square, with plain floor behind the stone: a stone with no room
            # to move thumps like a loadstone; no visible monster in the way (a kicked stone angers a peaceful)
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                py, px, by, bx = y - dy, x - dx, y + dy, x + dx
                if not (0 <= py < C.SIZE_Y and 0 <= px < C.SIZE_X and 0 <= by < C.SIZE_Y and 0 <= bx < C.SIZE_X):
                    continue
                if dis[py, px] == -1 or level.objects[by, bx] not in G.FLOOR or \
                        self.agent.glyphs[by, bx] in G.BOULDER or \
                        any(self.agent.glyphs[ry, rx] in G.MONS or self.agent.glyphs[ry, rx] in G.PETS
                            for ry, rx in ray(y, x, dy, dx)):
                    continue
                if best is None or dis[py, px] < dis[best[0]]:
                    best = ((py, px), (y, x), (dy, dx))
        if best is None:
            yield False
        yield True

        (py, px), (y, x), (dy, dx) = best
        self.agent.go_to(py, px)
        if (self.agent.blstats.y, self.agent.blstats.x) != (py, px) or \
                self.agent.glyphs[y, x] not in self.GRAY_STONE_GLYPHS:
            return
        level.gray_stone_kicks[y, x] += 1
        older = {(ry, rx) for ry, rx in ray(y, x, dy, dx)
                 if self.agent.glyphs[ry, rx] in self.GRAY_STONE_GLYPHS or
                 any(i.is_gray_stone() for i in flatten_items(level.items[ry, rx]))}
        if not self.agent.kick(y, x):
            return
        if 'Thump' in self.agent.message or self.agent.glyphs[y, x] in G.MONS:
            # a loadstone (or a mimic posing as a stone): leave it be
            level.gray_stone_kicks[y, x] = 3
            return
        if self.agent.glyphs[y, x] not in self.GRAY_STONE_GLYPHS:
            level.gray_stone_ray = ((y, x), (dy, dx), older, 0)

    @utils.debug_log('dip_for_excalibur')
    @Strategy.wrap
    def dip_for_excalibur(self):
        if self.agent.character.alignment != Character.LAWFUL or self.agent.blstats.experience_level < 5:
            yield False
        if self.agent.current_level().dungeon_number == Level.GNOMISH_MINES and \
                (self.minetown_level is None or self.agent.current_level().key() == self.minetown_level):
            yield False

        dis = self.agent.bfs()
        mask = utils.isin(self.agent.current_level().objects, G.FOUNTAIN) & (dis != -1)
        if not mask.any():
            yield False

        def excalibur_candidate():
            candidate = None
            for item in flatten_items(self.agent.inventory.items):
                if item.is_unambiguous() and item.object == O.from_name('long sword'):
                    if item.dmg_bonus is not None: # TODO: better condition for excalibur existance
                        return None
                    candidate = item
            return candidate

        if excalibur_candidate() is None:
            yield False
        yield True

        self.agent.go_to(*list(zip(*mask.nonzero()))[0])

        candidate = excalibur_candidate()
        if candidate is None:
            return

        # TODO: refactor
        with self.agent.atom_operation():
            candidate = self.agent.inventory.move_to_inventory(candidate)
            self.agent.step(A.Command.DIP)
            self.agent.type_text(self.agent.inventory.items.get_letter(candidate))
            if 'What do you want to dip ' in self.agent.message and 'into?' in self.agent.message:
                raise AgentPanic('no fountain here')

    def can_sacrify(self, item):
        if not item.is_corpse() or item.comment == 'old':
            return False

        mname = MON.permonst(item.monster_id + nh.GLYPH_MON_OFF).mname
        # hypothesis: picking up or offering a cockatrice/chickatrice corpse without worn gloves stones the hero at once,
        # so such corpses are never taken for sacrifice.
        # sources: NetHack 3.6.6 src/pickup.c fatal_corpse_mistake() ; https://nethackwiki.com/wiki/Cockatrice_corpse ;
        # /refs/history.md #182/#94 (same guard)
        if mname in ('cockatrice', 'chickatrice') and self.agent.inventory.items.gloves is None:
            return False
        if (mname == 'pony' and self.agent.character.role in [Character.KNIGHT, Character.BARBARIAN]) or \
                (mname == 'kitten' and self.agent.character.role == [Character.BARBARIAN, Character.WIZARD]) or \
                (mname == 'little dog' and item.naming):  # little dogs are always named
            # sufficient condition for being an initial pet
            return False

        if self.agent.character.alignment != Character.CHAOTIC:
            mapping = {
                Character.HUMAN: MON.M2_HUMAN | MON.M2_WERE,
                Character.DWARF: MON.M2_DWARF,
                Character.ELF: MON.M2_ELF,
                Character.GNOME: MON.M2_GNOME,
                Character.ORC: MON.M2_ORC,
            }
            f2 = MON.permonst(item.monster_id + nh.GLYPH_MON_OFF).mflags2
            if (f2 & mapping[self.agent.character.race]) > 0:
                return False

        return True

    @utils.debug_log('offer_corpses')
    @Strategy.wrap
    def offer_corpses(self):
        self.item_priority._take_sacrificial_corpses = False

        if self._got_artifact:
            yield False

        altars = [p for p, alignment in self.agent.current_level().altars.items()
                  if alignment == self.agent.character.alignment]

        if not altars:
            yield False

        dis = self.agent.bfs()
        altars = [(y, x) for y, x in altars if dis[y, x] != -1]

        if not altars:
            yield False

        self.item_priority._take_sacrificial_corpses = True

        if not any((self.can_sacrify(item) for item in flatten_items(self.agent.inventory.items))):
            yield False

        yield True

        y, x = min(altars, key=lambda p: dis[p])
        self.agent.go_to(y, x)
        with self.agent.panic_if_position_changes():
            while 1:
                for item in flatten_items(self.agent.inventory.items):
                    if self.can_sacrify(item):
                        with self.agent.atom_operation():
                            item = self.agent.inventory.move_to_inventory(item)
                            assert self.can_sacrify(item)
                            self.agent.step(A.Command.OFFER)
                            while ('There is ' in self.agent.message or 'There are ' in self.agent.message) and \
                                    ('sacrifice it?' in self.agent.message or 'sacrifice one?' in self.agent.message):
                                self.agent.type_text('n')
                            assert 'What do you want to sacrifice?' in self.agent.message, self.agent.message
                            self.agent.type_text(self.agent.inventory.items.get_letter(item))
                            if 'Nothing happens.' in self.agent.message:
                                self.agent.inventory.call_item(item, 'old')
                                return
                            if 'Use my gift wisely' in self.agent.message:
                                self._got_artifact = True
                                self.agent.inventory.get_items_below_me()
                                return
                            if 'So this is how you repay loyalty?' in self.agent.message:
                                raise AgentPanic('pet sacrified')
                            assert 'Your sacrifice is consumed in a flash of light' in self.agent.message or \
                                'Your sacrifice is consumed in a burst of flame' in self.agent.message or \
                                ('The blood covers the altar!' in self.agent.message and \
                                 'You have summoned ' in self.agent.message), \
                                self.agent.message
                            break
                else:
                    break

    @utils.debug_log('follow_guard')
    @Strategy.wrap
    def follow_guard(self):
        if not utils.isin(self.agent.glyphs, G.GUARD).any():
            yield False

        if any(item.category == nh.COIN_CLASS for item in flatten_items(self.agent.inventory.items)):
            yield True
            # if 'Please drop that gold and follow me.' in self.message:
            self.agent.stats_logger.log_event('drop_gold')
            self.item_priority._drop_gold_till_turn = self.agent.blstats.time + 100
            self.agent.inventory.arrange_items().run()
            return

        ys, xs = utils.isin(self.agent.glyphs, G.GUARD).nonzero()
        y, x = ys[0], xs[0]

        if utils.adjacent((y, x), (self.agent.blstats.y, self.agent.blstats.x)):
            yield False

        yield True

        self.agent.go_to(y, x, stop_one_before=True)

    # hypothesis: prayer is the bot's only emergency heal; once it is spent (timeout ~500-1000 turns) the early losses
    # (7/20 by Dlvl 4 / XL 7: giant ants, gnome mummy, elf zombie, Mordor orc, kitten) die in melee because fight2 keeps
    # trading blows at low HP. Climbing a nearby '<' ends the fight: only monsters adjacent at that moment AND able to
    # follow (pets, angry shopkeepers, M2_STALK monsters such as Z/@ soldiers) come along, everything else stays below.
    # Walking there only when no hostile nearby is faster than the hero (adjacent ones strictly slower) means the walk
    # costs no free hits; on the level above the hero rests to 80% HP (monsters generated there are easier, since
    # difficulty averages XL and depth) before the normal grind takes it back down.
    # sources: https://nethackwiki.com/wiki/Follower (mondata.c levl_follower: only adjacent pets/shopkeepers/M2_STALK follow) ;
    # https://nethackwiki.com/wiki/Stairs ; https://nethackwiki.com/wiki/Valkyrie (intrinsic Fast at XL 7, "retreat wisely") ;
    # https://nethackwiki.com/wiki/Speed ; NetHack 3.6.6 src/do.c doup() (Stressed or worse cannot climb) and mon.c mcalcmove() ;
    # player discussions: https://stuff.mit.edu/afs/sipb/project/nethackserver/src/slashem-0.0.7E7F2/doc/strategy.txt
    # ("fight battles in an area where if it goes badly you can retreat upstairs ... the vast majority of monsters will NOT
    # follow you ... keep on retreating upwards until you get your health back") ;
    # https://gamefaqs.gamespot.com/boards/582497-nethack/48576033 (learn the upstairs so you can retreat) ;
    # https://lparchive.org/Nethack-(by-Lobster-Maneuver)/Update%202/ (break off and rest 20 turns to regain HP) ;
    # REUSES #4 (/refs/history/4.diff: retreat upstairs at HP < 40%), re-designed: only while prayer is on cooldown,
    # no walk away from faster monsters, Mines allowed, never Dlvl 1 or Sokoban, climb failures handled without asserts.
    def _hero_speed(self):
        role, xl = self.agent.character.role, self.agent.blstats.experience_level
        fast = role in [Character.ARCHEOLOGIST, Character.MONK, Character.SAMURAI] or \
               (role in [Character.VALKYRIE, Character.BARBARIAN, Character.CAVEMAN, Character.KNIGHT] and xl >= 7)
        speed = 16 if fast else 12  # intrinsic Fast: an extra move on 1/3 of the turns
        if self.agent.blstats.carrying_capacity == 1:  # Burdened
            speed = speed * 3 // 4
        return speed

    def _retreat_threats(self):
        threats = []
        for dis, y, x, mon, _ in self.agent.get_visible_monsters():
            if mon.mname in WEAK_MONSTERS or mon.mname in ONLY_RANGED_SLOW_MONSTERS or mon.mmove == 0:
                continue
            if max(abs(y - self.agent.blstats.y), abs(x - self.agent.blstats.x)) > 7:
                continue
            threats.append((y, x, mon))
        return threats

    @utils.debug_log('retreat_upstairs')
    @Strategy.wrap
    def retreat_upstairs_strategy(self):
        agent = self.agent
        level = agent.current_level()
        hp, max_hp = agent.blstats.hitpoints, agent.blstats.max_hitpoints
        pos = (agent.blstats.y, agent.blstats.x)

        if self._retreat_rest_level is not None and \
                (self._retreat_rest_level != level.key() or hp * 10 >= max_hp * 8):
            self._retreat_rest_level = None

        # rest on the level we escaped to
        if self._retreat_rest_level is not None:
            if agent.get_visible_monsters() or agent.blstats.hunger_state > Hunger.NOT_HUNGRY or \
                    agent.character.prop.blind or agent.character.prop.hallu:
                yield False
            yield True
            agent.search(20)
            return

        # hypothesis: against a crowd of four or more melee hostiles (Big Room, soldier or jackal packs) the hero climbs a nearby '<' while still above 40% HP, before the crowd can finish it, instead of waiting for the low-HP trigger.
        # sources: https://nethackwiki.com/wiki/Big_Room ("Start on the stairs ... leave the level quickly and heal") ; https://nethackwiki.com/wiki/Stairs
        threats = self._retreat_threats()
        outnumbered = len(threats) >= 4 and hp * 10 < max_hp * 7
        if (hp * 10 >= max_hp * 4 and not outnumbered) or agent.is_safe_to_pray(500) or \
                agent.blstats.time < self._retreat_cooldown_until or \
                level.dungeon_number == Level.SOKOBAN or agent.blstats.depth <= 1 or \
                agent.blstats.carrying_capacity >= 2 or level.shop_interior[pos] or \
                agent.character.prop.confusion or agent.character.prop.stun or agent.character.prop.hallu or \
                agent.is_held():  # held: each step is "You cannot escape" (see Agent._update_held_state)
            yield False

        if not threats:
            yield False

        dis = agent.bfs()
        target = None
        for (y, x), dest in level.get_stairs(up=True).items():
            if dest is not None and dest[0][0] == Level.SOKOBAN:
                continue
            if (y, x) != pos and agent.monster_tracker.monster_mask[y, x]:
                continue
            if dis[y, x] == -1 or dis[y, x] > 20:
                continue
            if target is None or dis[y, x] < dis[target]:
                target = (y, x)
        if target is None:
            yield False

        if dis[target] > 1:
            speed = self._hero_speed()
            for y, x, mon in threats:
                if mon.mmove > speed or (utils.adjacent((y, x), pos) and mon.mmove == speed):
                    yield False

        # hypothesis: the bfs path to '<' can run through a square a monster stands on, and move() raises "Monster on a
        # next tile" without passing game time when the next square is occupied; this strategy outranks fight2, so it
        # fires again at once and main() sees 5 zero-time panics ("Cyclic Panic"). A blocked first step means the way
        # up is not free: leave the square to fight2 and the rest.
        # sources: /refs/history/191.diff (#191) and /refs/history/138.diff ; NetHack 3.6.6 src/hack.c domove() (the
        # hero cannot walk through a monster) ; https://nethackwiki.com/wiki/Stairs
        if target != pos:
            path = agent.path(pos[0], pos[1], *target, dis=dis)
            if len(path) < 2 or agent.monster_tracker.monster_mask[path[1]]:
                yield False

        yield True

        if target != pos:
            agent.go_to(*target, max_steps=1)
            return

        with agent.atom_operation():
            agent.direction('<')
        if agent.current_level().key() == level.key():
            # e.g. "You are carrying too much to climb" or held by a monster -- let the fight go on
            self._retreat_cooldown_until = agent.blstats.time + 30
            return
        agent.stats_logger.log_event('retreat_upstairs')
        level.stair_destination[pos] = (agent.current_level().key(), (agent.blstats.y, agent.blstats.x))
        agent.current_level().stair_destination[(agent.blstats.y, agent.blstats.x)] = (level.key(), pos)
        self._retreat_rest_level = agent.current_level().key()

    # hypothesis: grinding on the depth whose monster difficulty tracks the hero's XL gives far more XP per turn than wall-searching Dlvl 1 until XL 8, which stalls 5-14k turns, starves or dies to weak monsters on the first level.
    # sources: https://nethackwiki.com/wiki/Monster_difficulty ; https://nethackwiki.com/wiki/Experience_level ; https://nethackwiki.com/wiki/Forum:Have_a_good_strategy_for_descension%3F ; https://nethackwiki.com/wiki/Monster_creation
    def grind_depth(self):
        return min(4, max(1, self.agent.blstats.experience_level - 1))

    # hypothesis: the XL-8 grind wall-searches a picked-clean Dlvl 3-4 for thousands of turns: only one random monster
    #   per ~70 turns arrives, with no corpses and no loot, so the hero lives on hunger prayers until one comes too soon
    #   and the fainting hero is killed (parent public seeds 1, 9, 12 and dev 917618 die at XL 6-9 on Dlvl 4-5 after
    #   11-20k turns). The progression schedule (and the wiki/players) put the Gnomish Mines at XL 4-5: its upper
    #   filler levels are populated with gnomes, gnome lords, dwarves and hill orcs -- XP, safe corpses (gnome 100,
    #   dwarf 300, hill orc 200 nutrition), daggers and dwarvish helms/mithril -- and Minetown is never above Mines
    #   level 3. So once the hero is XL 5+ and its main-dungeon grind stalls (1500 turns without a new experience level)
    #   or it is Hungry with no food in the pack, the rest of the XL-8 grind happens on Mines level 1 (XL 5) / 2 (XL 6+)
    #   instead; at XL 8 the usual tour (Mines -> Minetown -> Sokoban ...) continues from there.
    # sources: NetHack 3.6.6 dat/dungeon.def (Mines branch on Dlvl 2-4, "minetn" @ (3, 2) = Mines level 3-4);
    #   https://nethackwiki.com/wiki/Gnomish_Mines (first-level raid for helm/boots/daggers/mithril, gnome and dwarf
    #   corpses); https://nethackwiki.com/wiki/Valkyrie (human Valkyrie: hostile gnomes/dwarves give XP and gear);
    #   https://nethackwiki.com/wiki/Forum:Have_a_good_strategy_for_descension%3F ("head for Minetown as soon as I was
    #   maybe level 4 or 5", "upper mines" vs below Minetown); https://nethackwiki.com/wiki/Nutrition (gnome/dwarf
    #   corpses as early food; hunger comes from wandering empty levels); round-13 claim #501 (diagnosis, never built)
    MINES_GRIND_MIN_XL = 5

    # hypothesis: the stall trigger above (1500 turns without a new experience level) fires in almost every game, since
    #   XL 5 -> 6 -> 7 on Dlvl 3-4 normally takes longer than that, so XL 5-6 Valkyries with ~40 HP grind among the
    #   Mines' gnome-lord/dwarf/hill-orc packs on wide-open levels and wander on into Minetown at XL 8 (#513: public
    #   0.53 -> 0.20, held-out 0.40 -> 0.28; 8 of 15 public games now die on Dlvl 3-4 at XL 5-8 to killer bees, wolves,
    #   a shopkeeper, a watchman ...). What #513 was meant to fix is starvation on a picked-clean grind level (the
    #   hero lives on hunger prayers until one comes too soon), so the Mines trip becomes a food raid: it starts only
    #   when the hero is Hungry, carries no food and could not safely pray before it turns Weak, it goes to Mines level
    #   1 (the shallowest and nearest; gnome/dwarf/hill-orc corpses 100-300 nutrition), and it ends -- the grind goes
    #   back to the main-dungeon grind depth -- once the hero is fed and either carries food or may pray again. All
    #   other games grind on Dlvl 1-4 to XL 8 exactly as the root did.
    # sources: /board/nodes/node-513.json and node-446.json (per-seed results of parent and root);
    #   https://nethackwiki.com/wiki/Gnomish_Mines (more monsters per level than the main dungeon, wide open areas;
    #   gnomes/dwarves hostile to humans); https://nethackwiki.com/wiki/Dwarf_(monster) (a mattock swing does up to ~20,
    #   "a serious danger for very early or under-prepared heroes" in an unfriendly Mines);
    #   https://nethackwiki.com/wiki/Lessons_learned_the_hard_way ("skip the Gnomish Mines and come back when you're
    #   more powerful"); https://nethackwiki.com/wiki/User:Furey/Furey's_NetHack_Tips (dying in the upper Mines: prepare
    #   longer first); Maniac's Ascension Guide (alt.org mirror, mag-r2.html: Mines hard for non-dwarf/gnome races);
    #   https://nethackwiki.com/wiki/Nutrition (Hungry 50-149, Weak 0-49, 1 per turn: ~100 turns Hungry -> Weak);
    #   https://nethackwiki.com/wiki/Prayer (Weak from hunger is a major trouble, fixed when the timeout is < 200)
    def _update_mines_grind(self):
        xl = self.agent.blstats.experience_level
        turn = self.agent.blstats.time
        if xl != self._grind_xl:
            self._grind_xl, self._grind_xl_turn = xl, turn
        if self.milestone != Milestone.BE_ON_FIRST_LEVEL:
            return
        hunger = self.agent.blstats.hunger_state
        has_food = self.agent.inventory.items.total_nutrition() > 0
        if self._mines_grind:
            # fed again, and the next hunger is covered by carried food or by a safe prayer
            if hunger < Hunger.HUNGRY and (has_food or self.agent.is_safe_to_pray(500)):
                self._mines_grind = False
            return
        if xl < self.MINES_GRIND_MIN_XL:
            return
        # Weak comes ~100 turns after Hungry; the hunger prayer (at Weak) needs ~400 turns since the last one
        if hunger >= Hunger.HUNGRY and not has_food and not self.agent.is_safe_to_pray(300):
            self._mines_grind = True

    def grind_level(self):
        if self._mines_grind:
            return (Level.GNOMISH_MINES, 1)
        return (Level.DUNGEONS_OF_DOOM, self.grind_depth())

    @Strategy.wrap
    def current_strategy(self):
        yield True
        while 1:
            explore_stairs_condition = lambda: False
            if self.milestone == Milestone.BE_ON_FIRST_LEVEL:
                condition = lambda: self.agent.blstats.experience_level >= 8
                # explore_stairs_condition = lambda: self.agent.inventory.items.total_nutrition() == 0 and \
                #                                    self.agent.blstats.hunger_state >= Hunger.NOT_HUNGRY
                level = self.grind_level()

            elif self.milestone == Milestone.FIND_SOKOBAN:
                condition = lambda: self.agent.current_level().dungeon_number == Level.SOKOBAN
                level = (Level.SOKOBAN, 4)

            elif self.milestone == Milestone.FIND_GNOMISH_MINES:
                condition = lambda: self.agent.current_level().dungeon_number == Level.GNOMISH_MINES
                level = (Level.GNOMISH_MINES, 1)

            # elif self.milestone == Milestone.FIND_LIGHT_GNOMISH_MINES:
            #     condition = lambda: self.agent.current_level().dungeon_number == Level.GNOMISH_MINES \
            #             and self.agent.current_level().is_light_level()
            #     level = (Level.GNOMISH_MINES, 9)

            # elif self.milestone == Milestone.FARM_LIGHT_GNOMISH_MINES:
            #     condition = lambda: self.agent.blstats.experience_level >= 11
            #     level = (Level.GNOMISH_MINES, self.agent.current_level().level_number)

            elif self.milestone == Milestone.FIND_MINETOWN:
                condition = lambda: self.minetown_level is not None
                level = (Level.GNOMISH_MINES, 4)  # TODO

            elif self.milestone == Milestone.SOLVE_SOKOBAN:
                condition = self.sokoban_top_done
                level = (Level.SOKOBAN, 1)

            elif self.milestone == Milestone.FIND_MINES_END:
                condition = lambda: self.agent.current_level().key() == (Level.GNOMISH_MINES, 9)  # TODO
                level = (Level.GNOMISH_MINES, 9)  # TODO

            else:
                # TODO
                condition = lambda: False
                level = (Level.DUNGEONS_OF_DOOM, 100)

            if condition():
                self.milestone = Milestone(int(self.milestone) + 1)
                continue


            def exploration_strategy(level, **kwargs):
                return (
                    Strategy(lambda: self.agent.exploration.explore1(level, trap_search_offset=1,
                        kick_doors=self.may_kick_doors_here(), **kwargs).strategy())
                    .preempt(self.agent, [
                        self.kick_test_gray_stones(),
                        self.identify_items_on_altar().every(100),
                        self.identify_items_on_altar().condition(
                            lambda: self.agent.current_level().objects[self.agent.blstats.y,
                                                                       self.agent.blstats.x] in G.ALTAR),
                        self.dip_for_excalibur().condition(
                            lambda: self.agent.blstats.experience_level >= 7).every(10),
                    ])
                )

            def go_to_strategy(y, x):
                return (
                    exploration_strategy(None)
                    .preempt(self.agent, [
                        self.agent.exploration.go_to_strategy(y, x).preempt(self.agent, [
                            self.agent.inventory.gather_items(),
                            self.identify_items_on_altar(),
                            self.dip_for_excalibur().condition(lambda: self.agent.blstats.experience_level >= 7),
                        ])
                        .condition(lambda: self._got_artifact or
                                           not any([alignment == self.agent.character.alignment
                                                    for _, alignment in self.agent.current_level().altars.items()]))
                    ])
                    .until(self.agent, lambda: (self.agent.blstats.y, self.agent.blstats.x) == (y, x))
                )

            (
                self.agent.exploration.go_to_level_strategy(*level, go_to_strategy, exploration_strategy(None))
                .before(exploration_strategy(None))#.before(self.agent.exploration.patrol())
                .preempt(self.agent, [
                    exploration_strategy(0),
                    exploration_strategy(None).until(
                        self.agent, lambda: self.agent.blstats.hitpoints >= 0.8 * self.agent.blstats.max_hitpoints)
                ])
                .preempt(self.agent, [
                    self.agent.exploration.explore_stairs(go_to_strategy, all=True).condition(explore_stairs_condition),
                ])
                .until(self.agent, lambda: condition() or
                       (self.milestone == Milestone.BE_ON_FIRST_LEVEL and self.grind_level() != level))
            ).run()

    # hypothesis: combination 2 of round 10 -- the strongest single ideas, each a different weakness: #338 takes the
    #   Mines' End luckstone (Luck +3, loot bonus), #346 + #373 pick up and put on the Sokoban prize amulet of
    #   reflection (rays/wand bolts killed the best heroes), #372 cures food poisoning/illness/sliming/strangling,
    #   #347 records the prayer turn before the prayer step (no double prayer), #358 declines "Really attack
    #   <peaceful>?" (peaceful dwarves/watch of a lawful Valkyrie in the Mines). They touch separate code paths and
    #   together make the grinding hero luckier, reflecting and harder to kill by accidents.
    # sources: round ideas #338, #346, #373, #372, #347, #358 (/board/round_ideas/node-<n>.diff)
    def global_strategy(self):
        return (
            self.current_strategy().repeat()
            .preempt(self.agent, [
                self.solve_sokoban_strategy()
                .condition(lambda: self.milestone == Milestone.SOLVE_SOKOBAN and
                                   self.agent.current_level().dungeon_number == Level.SOKOBAN),
                self.reveal_sokoban_mimics_strategy()
                .condition(lambda: self.milestone == Milestone.SOLVE_SOKOBAN and
                                   self.agent.current_level().dungeon_number == Level.SOKOBAN)
            ])
            .preempt(self.agent, [
                self.offer_corpses().preempt(self.agent, [
                    self.agent.eat_corpses_from_ground().condition(lambda: self.agent.blstats.hunger_state >= Hunger.NOT_HUNGRY),
                ]),
            ])
            .preempt(self.agent, [
                self.wait_out_unexpected_state_strategy(),
            ])
            .preempt(self.agent, [
                self.agent.cure_disease().every(5),
            ])
            .preempt(self.agent, [
                self.agent.eat_corpses_from_ground(only_below_me=True).condition(lambda: self.agent.blstats.hunger_state >= Hunger.NOT_HUNGRY),
                self.agent.eat_corpses_from_ground().every(5).condition(lambda: self.agent.blstats.hunger_state >= Hunger.NOT_HUNGRY),
                self.agent.eat_from_inventory().every(5),
            ])
            .preempt(self.agent, [
                self.follow_guard(),
            ])
            .preempt(self.agent, [
                self.wear_good_amulet(),
            ])
            .preempt(self.agent, [
                self.agent.fight2(),
            ])
            .preempt(self.agent, [
                self.retreat_upstairs_strategy(),
            ])
            .preempt(self.agent, [
                self.agent.engulfed_fight(),
            ])
            .preempt(self.agent, [
                self.agent.emergency_strategy(),
            ])
            .preempt(self.agent, [
                self.agent.cure_stoning(),
                self.agent.cure_deadly_illness(),
            ])
            .preempt(self.agent, [
                self.remove_strangling_amulet(),
            ])
        )
