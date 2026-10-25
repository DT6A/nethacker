from collections import defaultdict
from itertools import product

import numpy as np
from scipy import signal

from ..glyph import G, SS
from ..utils import adjacent, isin
from .monster_utils import is_monster_faster, is_dangerous_monster, ignores_elbereth, \
    ONLY_RANGED_SLOW_MONSTERS, EXPLODING_MONSTERS, WEAK_MONSTERS, consider_melee_only_ranged_if_hp_full
from .movement_priority import draw_monster_priority_positive, draw_monster_priority_negative
from .utils import wielding_ranged_weapon, line_dis_from, inside


def melee_monster_priority(agent, monsters, monster):
    _, y, x, mon, _ = monster
    ret = 1
    if agent.blstats.hitpoints > 8 or is_monster_faster(agent, monster):
        ret += 15
    if wielding_ranged_weapon(agent) and not is_monster_faster(agent, monster):
        ret -= 6
    if mon.mname in EXPLODING_MONSTERS:
        ret -= 17
    if 'were' in mon.mname:
        ret += 1
    # if not wielding_melee_weapon(agent):
    #     ret -= 5
    if mon.mname in ONLY_RANGED_SLOW_MONSTERS:
        if not consider_melee_only_ranged_if_hp_full(agent, monster):
            ret -= 100
            if mon.mname == 'floating eye':
                ret -= 10
            if mon.mname == 'gas spore':
                ret -= 5

    if mon.mname == 'gas spore':
        # handle a specific case when you are trapped by a gas spore
        if len(agent.get_visible_monsters()) == 1 \
                and agent.blstats.hitpoints / agent.blstats.max_hitpoints:
            dis = agent.bfs()
            for y2, x2 in zip(*np.nonzero(dis != -1)):
                if not adjacent((y, x), (y2, x2)):
                    return ret
            agent.stats_logger.log_event('melee_gas_spore')
            return 1  # a priority higher than random moving around

    return ret


def ranged_priority(agent, dy, dx, monsters):
    ret = 11

    closest_mon_dis = float('inf')
    for monster in monsters:
        _, my, mx, mon, _ = monster
        assert my != agent.blstats.y or mx != agent.blstats.x
        if mon.mname not in WEAK_MONSTERS + ONLY_RANGED_SLOW_MONSTERS:
            closest_mon_dis = min(closest_mon_dis, line_dis_from(agent, my, mx))

    if closest_mon_dis == 1:
        ret -= 11

    launcher, ammo = agent.inventory.get_best_ranged_set()
    if ammo is None:
        return None

    if launcher is not None and not launcher.equipped:
        ret -= 5

    y, x = agent.blstats.y, agent.blstats.x
    while True:
        y += dy
        x += dx
        if not 0 <= y < agent.glyphs.shape[0] or not 0 <= x < agent.glyphs.shape[1]:
            return None

        if agent.glyphs[y, x] in G.PETS or not agent.current_level().walkable[y, x]:
            return None

        if agent.glyphs[y, x] in G.MONS:
            monster = [m for m in monsters if m[1] == y and m[2] == x]
            if not monster:
                # there is a monster that shouldn't be attacked
                return None
            assert len(monster) == 1
            _, _, _, mon, _ = monster[0]
            dis = line_dis_from(agent, y, x)
            if dis > agent.character.get_range(launcher, ammo):
                return None
            if dis in (1, 2):
                ret -= 5
            if dis == 1:
                ret -= 6
                if mon.mname == 'gas spore':  # only gas spore ?
                    ret -= 100
            return ret, y, x, monster[0]


def get_next_states(agent, wand, y, x, dy, dx):
    if not inside(agent, y, x) or not agent.current_level().walkable[y, x]:
        can_bounce = wand.is_ray_wand()
        if not can_bounce:
            return []
        if dy == 0 or dx == 0:
            return [(y - dy, x - dx, -dy, -dx, 1.0, 1)]
        # TODO: diagonal
        side1 = (y, x - dx)
        side2 = (y - dy, x)
        side1_wall = not inside(agent, *side1) or not agent.current_level().walkable[side1]
        side2_wall = not inside(agent, *side2) or not agent.current_level().walkable[side2]
        dy1, dx1 = side2[0] - side1[0], side2[1] - side1[1]
        dy2, dx2 = side1[0] - side2[0], side1[1] - side2[1]
        if side1_wall and side2_wall:
            return [(y - dy, x - dx, -dy, -dx, 1.0, 1)]
        elif not side1_wall and not side2_wall:
            return [(y - dy, x - dx, -dy, -dx, 1 / 20, 1),
                    (y + dy1, x + dx1, dy1, dx1, 19 / 40, 1),
                    (y + dy2, x + dx2, dy2, dx2, 19 / 40, 1)]
        elif side1_wall:
            return [(y + dy1, x + dx1, dy1, dx1, 1.0, 1)]
        elif side2_wall:
            return [(y + dy2, x + dx2, dy2, dx2, 1.0, 1)]
        else:
            assert 0
    return [(y + dy, x + dx, dy, dx, 1.0, 0)]


def _simulate_wand_path(agent, wand, monsters, y, x, dy, dx, range_left, hit_targets, probability):
    if range_left < 0:
        return

    for y, x, dy, dx, next_prob, range_penalty in get_next_states(agent, wand, y, x, dy, dx):
        range_left -= range_penalty
        monster = [m for m in monsters if m[1] == y and m[2] == x]
        if monster:
            assert len(monster) == 1
            monster = monster[0]
            # For each monster hit, range decreases by 2.
            range_left -= 2
        elif inside(agent, y, x) and agent.glyphs[y, x] in G.PETS:
            monster = 'pet'
            # For each monster hit, range decreases by 2.
            range_left -= 2
        elif agent.blstats.y == y and agent.blstats.x == x:
            monster = 'self'
            range_left -= 2
        else:
            monster = None

        hit_targets[(y, x, monster)] += probability * next_prob

        _simulate_wand_path(agent, wand, monsters, y, x, dy, dx, range_left - 1, hit_targets, 1.0)


def simulate_wand_path(agent, wand, monsters, dy, dx):
    """ Returns list of tuples (y, x, hit_object, expected_hit_count).
    """
    y, x = agent.blstats.y, agent.blstats.x

    # TODO: random range left from 6 or 7 to 13
    hit_targets = defaultdict(int)
    _simulate_wand_path(agent, wand, monsters, y, x, dy, dx, 13, hit_targets, 1.0)
    for (y, x, hit_object), expected_hit_count in hit_targets.items():
        yield y, x, hit_object, expected_hit_count


def get_potential_wand_usages(agent, monsters, dy, dx):
    ret = []
    player_hp_ratio = agent.blstats.hitpoints / agent.blstats.max_hitpoints
    # TODO: also get items recursively from bags
    for item in agent.inventory.items:
        targeted_monsters = set()
        if not item.is_offensive_usable_wand():
            continue
        priority = 0
        # print('--------------', dy, dx)
        for y, x, monster, p in simulate_wand_path(agent, item, monsters, dy, dx):
            # print(y, x, monster, p)
            if monster == 'pet':
                priority -= p * 20
            elif monster == 'self':
                priority -= p * 30
            elif monster is not None:
                _, y, x, mon, _ = monster
                if mon.mname in WEAK_MONSTERS:
                    priority += min(p, 1) * 1
                elif is_dangerous_monster(monster):
                    priority += p * 25
                else:
                    priority += min(p, 1) * 10
                targeted_monsters.add((y, x, monster))
        if targeted_monsters:
            # priority = priority * (1 - player_hp_ratio) - 10
            priority = priority - 15
            if agent.inventory.engraving_below_me.lower() == 'elbereth':
                priority -= 100
            ret.append((priority, ('zap', dy, dx, item, targeted_monsters)))
    return ret


def elbereth_action(agent, monsters):
    if agent.inventory.engraving_below_me.lower() == 'elbereth':
        return []
    if not agent.can_engrave():
        return []
    adj_monsters_count = 0
    for monster in monsters:
        _, my, mx, mon, _ = monster
        if mon.mname in ONLY_RANGED_SLOW_MONSTERS:
            continue
        if not adjacent((my, mx), (agent.blstats.y, agent.blstats.x)):
            continue
        if ignores_elbereth(monster):
            return []
        multiplier = np.clip(20 / agent.blstats.hitpoints, 1.0, 1.5)
        if is_monster_faster(agent, monster):
            multiplier *= 2
        # hypothesis: WEAK_MONSTERS holds names, so `mon in WEAK_MONSTERS` on the monster object was always False and newts, lichens, shriekers and grid bugs counted as full Elbereth threats; at low HP the hero then engraves and waits instead of killing one.
        # sources: https://nethackwiki.com/wiki/Elbereth ; https://nethackwiki.com/wiki/Lichen ; https://nethackwiki.com/wiki/Newt ; https://nethackwiki.com/wiki/Talk:Elbereth ; GameFAQs NetHack 1987 board "Ok, seriously, what are the golden rules for the Early Stage of the game?" (https://gamefaqs.gamespot.com/boards/582497-nethack-1987/59952741?page=2)
        if mon.mname in WEAK_MONSTERS:
            adj_monsters_count += 0.1 * multiplier
            continue
        adj_monsters_count += 1 * multiplier
        if is_dangerous_monster(monster):
            adj_monsters_count += 2 * multiplier

    player_hp_ratio = (agent.blstats.hitpoints / agent.blstats.max_hitpoints) ** 0.5
    if agent.blstats.hitpoints < 30 and adj_monsters_count > 0:
        return [(-15 + 20 * adj_monsters_count * (1 - player_hp_ratio), ('elbereth',))]
    return []


def wait_action(agent, monsters):
    if agent.inventory.engraving_below_me.lower() == 'elbereth' and not any(
            ignores_elbereth(monster) and adjacent((monster[1], monster[2]), (agent.blstats.y, agent.blstats.x))
            for monster in monsters):
        player_hp_ratio = agent.blstats.hitpoints / agent.blstats.max_hitpoints
        priority = 30 - player_hp_ratio * 40
        return [(priority, ('wait',))]
    return []


def get_available_actions(agent, monsters):
    actions = []

    # melee attack actions
    for monster in monsters:
        _, y, x, mon, _ = monster
        if adjacent((y, x), (agent.blstats.y, agent.blstats.x)):
            priority = melee_monster_priority(agent, monsters, monster)
            if agent.inventory.engraving_below_me.lower() == 'elbereth' and not ignores_elbereth(monster):
                priority -= 100
            dy = y - agent.blstats.y
            dx = x - agent.blstats.x
            actions.append((priority, ('melee', dy, dx)))

    # ranged attack actions
    for dy, dx in product([-1, 0, 1], [-1, 0, 1]):
        if dy != 0 or dx != 0:
            ranged_pr = ranged_priority(agent, dy, dx, monsters)
            if ranged_pr is not None:
                pri, y, x, monster = ranged_pr
                if agent.inventory.engraving_below_me.lower() == 'elbereth' and not ignores_elbereth(monster):
                    pri -= 100
                if all(monster[3].mname in ONLY_RANGED_SLOW_MONSTERS for monster in monsters):
                    pri += 10
                actions.append((pri, ('ranged', dy, dx)))

            actions.extend(get_potential_wand_usages(agent, monsters, dy, dx))

    to_pickup = decide_what_to_pickup(agent)
    if to_pickup:
        actions.append((15, ('pickup', to_pickup)))

    actions.extend(elbereth_action(agent, monsters))
    actions.extend(wait_action(agent, monsters))

    return actions


def decide_what_to_pickup(agent):
    projectiles_below_me = [i for i in agent.inventory.items_below_me
                            if i.is_thrown_projectile() or i.is_fired_projectile()]
    my_launcher, ammo = agent.inventory.get_best_ranged_set(additional_ammo=[i for i in projectiles_below_me])
    to_pickup = []
    for item in agent.inventory.items_below_me:
        if item.is_thrown_projectile() or (my_launcher is not None and item.is_fired_projectile(launcher=my_launcher)):
            to_pickup.append(item)
    return to_pickup


def goto_action(agent, priority, monsters):
    values = []
    walkable = agent.current_level().walkable
    for dy, dx in [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]:
        y, x = agent.blstats.y - dy, agent.blstats.x - dx
        if not 0 <= y < walkable.shape[0] or not 0 <= x < walkable.shape[1]:
            continue
        if not np.isnan(priority[y, x]):
            values.append(priority[y, x])
    if len(set(values)) > 1:
        return []

    assert monsters
    for monster in monsters:
        _, my, mx, mon, _ = monster
        if not adjacent((agent.blstats.y, agent.blstats.x), (my, mx)):
            # and not mon.mname in ONLY_RANGED_SLOW_MONSTERS:
            return [(1, ('go_to', my, mx))]
    assert 0, monsters


def get_corridors_priority_map(walkable):
    k = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    wall_count = signal.convolve2d((~walkable).astype(int), k, boundary='symm', mode='same')
    corridor_mask = (wall_count == 6).astype(int)
    corridor_mask[~walkable] = 0
    corridor_dilated = signal.convolve2d(corridor_mask.astype(int), k, boundary='symm', mode='same')
    return corridor_mask + corridor_dilated >= 1


# hypothesis: fight2 met packs (rothes, soldier ants, killer bees, jackals, gnomes, orcs, Woodland-elves -- all group
#   monsters, 2-4 or 2-11 at a time) wherever it happened to be, mostly in the open room where up to 8 of them get a melee
#   round on the hero each turn; rothe and soldier ant packs are among this run's commonest killers of XL 6-11 heroes.
#   With two or more hostile melee monsters in view the move heatmap now costs each square the number of them that can
#   stand next to it at once (its walkable neighbours, capped at the crowd size), so the hero waits for the pack in a
#   corridor, a dead end or just outside a door, where it meets one or two of them at a time. Movement into/out of an
#   intact doorway is orthogonal only, but attacks ignore that rule (mon.c monnear, hack.c domove attacks before
#   test_move), so a doorway square counts all its walkable neighbours like any other square. Monsters adjacent to the
#   hero are still meleed first (melee priority >= 16 vs at most a few points here); the danger terms are unchanged.
# sources: https://nethackwiki.com/wiki/Group ("lure them into a corridor or doorway, so only one member of the group can
#   attack the player at a time"; rothe, ants, jackals, gnomes, elves small groups; killer bees, orcs large groups) ;
#   https://nethackwiki.com/wiki/Soldier_ant ("avoid being surrounded at all costs, and try to lead them through a nearby
#   corridor") ; https://nethackwiki.com/wiki/Rothe (groups of 2-4 overwhelm under-prepared heroes; "refine their
#   movement tactics") ; https://nethackwiki.com/wiki/Door (the diagonal rule is for movement; doorways as bottlenecks) ;
#   https://nethack.fandom.com/wiki/Movement_tactics (in the open a group surrounds you on 6 of 8 sides, in a corridor
#   only one can be adjacent) ; player guides: Mikko Saari's NetHack Beginner's Guide
#   (https://www.melankolia.net/nethack/nethack.guide.html: rothes come in groups, "retreat into a corridor where only one
#   of them can attack you at time"), the SLASH'EM-bundled strategy.txt
#   (https://stuff.mit.edu/afs/sipb/project/nethackserver/src/slashem-0.0.7E7F2/doc/strategy.txt: back up into the
#   hallway) and GameFAQs "How to avoid moccasins, demons, bees and ants"
#   (https://gamefaqs.gamespot.com/boards/582497-nethack-1987/40910927) ; NetHack 3.6.6 src/mon.c monnear(), mfndpos()
#   and src/hack.c domove() ; the commented-out corridor map below is AutoAscend's untried TODO for the same idea
def get_attack_square_counts(agent, walkable):
    """ For every square, how many squares next to it a monster could stand on to hit the hero there """
    level = agent.current_level()
    # a dark room's floor beyond the hero's sight is not remembered yet -- count unseen squares next to room floor as
    # open, but not the never-displayed rock beside a corridor
    room_floor = isin(level.objects, frozenset({SS.S_room, SS.S_darkroom}))
    near_room = signal.convolve2d(room_floor.astype(int), np.ones((3, 3), dtype=int), mode='same') > 0
    open_squares = walkable | (~level.seen & near_room)
    k = np.ones((3, 3), dtype=int)
    k[1, 1] = 0
    return signal.convolve2d(open_squares.astype(int), k, mode='same')


# hypothesis: my parent's chokepoint term only pays against a pack that walks into the corridor; it also removes
#   fight2's "go to the monster" fallback (that fires only when all neighbour priorities are equal), so the hero now
#   waits in a corridor or dead end forever for monsters that never come -- a sleeping zoo, barracks or beehive, a
#   monster stuck behind water or a boulder, a fleeing one -- while fight2 (which outranks exploring and eating) never
#   ends, and it holds still under the arrows, daggers and wand zaps of the archers that packs carry (hill orcs,
#   Uruk-hai, forest centaurs, elves, soldiers), which keep shooting from out of reach instead of closing in.
#   Parent #380 fell from 0.536 to 0.384 public / 0.350 to 0.180 held-out against root #376, with new deaths to an
#   Uruk-hai, hill orc and forest centaur and games that end alive at XL 10-12. The wait now has to pay: it holds while
#   the nearest pack member keeps getting closer (or is already adjacent), and is dropped -- back to the root's
#   approach-and-strike-first behaviour -- when the pack stops closing in for CHOKEPOINT_PATIENCE turns or a missile,
#   wand zap or ray comes at the hero, until a pack member reaches the hero again or the encounter ends.
# sources: https://nethackwiki.com/wiki/Group (lure groups into a corridor -- "so only one member of the group can
#   attack the player at a time" -- which needs them to follow) ; https://nethackwiki.com/wiki/Uruk-hai ("facing an
#   Uruk-hai in melee may deter them from using their arrows"; bows and poisoned arrows) ;
#   https://nethackwiki.com/wiki/Hill_orc ; https://nethackwiki.com/wiki/Zoo (a zoo is a room of sleeping monsters,
#   also the Sokoban top level's) ; https://nethackwiki.com/wiki/Stealth (with stealth -- intrinsic for a Valkyrie --
#   sleeping monsters do not wake as the hero moves, so they never come to the chokepoint) ;
#   https://nethackwiki.com/wiki/Valkyrie ; player guide in search results (mazesofmenace.ai/spoilers: "fight from the
#   doorway so they wake one or two at a time"; reach the chokepoint first) ; NetHack 3.6.6 src/mthrowu.c thitu()
#   ("You are hit by" / "You are almost hit by"), m_throw()/monshoot() ("%s shoots/throws"), src/zap.c buzz()
#   ("whizzes by you") ; past nodes #66/#378 (close to melee with a monster shooting from range)
#   ; ported unchanged from node #389 (the same repair on #380 alone: 0.327 -> 0.440, held-out 0.180 -> 0.375) onto
#   #380 -> #387, whose crash fixes do not touch fight2
CHOKEPOINT_PATIENCE = 8
UNDER_FIRE_MESSAGES = ('You are hit by', 'You are almost hit by', 'whizzes by you', ' shoots ', ' throws ', ' zaps ')


def chokepoint_wait_pays(agent, crowd):
    st = agent.chokepoint_state
    turn = agent.blstats.time
    pos = (agent.blstats.y, agent.blstats.x)
    reachable = [m[0] for m in crowd if m[0] >= 0]
    nearest = min(reachable) if reachable else None
    if st['turn'] is None or not 0 <= turn - st['turn'] <= 20:
        # a new encounter
        st.update(turn=turn, nearest=nearest, stalled=0, suspended=False)
    if any(adjacent((m[1], m[2]), pos) for m in crowd):
        st.update(turn=turn, nearest=nearest, stalled=0, suspended=False)
        return True
    if any(msg in agent.message for msg in UNDER_FIRE_MESSAGES):
        st['suspended'] = True
    if turn != st['turn']:
        if nearest is not None and (st['nearest'] is None or nearest < st['nearest']):
            st['stalled'] = 0
        else:
            st['stalled'] += turn - st['turn']
        st['nearest'] = nearest
        st['turn'] = turn
    if st['stalled'] >= CHOKEPOINT_PATIENCE:
        st['suspended'] = True
    return not st['suspended']


def get_priorities(agent):
    """ Returns a pair (move priority heatmap, other actions (with priorities) list) """
    walkable = agent.current_level().walkable
    priority = np.zeros(walkable.shape, dtype=float)
    monsters = agent.get_visible_monsters()
    for m in monsters:
        draw_monster_priority_positive(agent, m, priority, walkable)
    for m in monsters:
        draw_monster_priority_negative(agent, m, priority, walkable)
    priority[~walkable] = float('nan')

    crowd = [m for m in monsters
             if m[3].mname not in WEAK_MONSTERS + ONLY_RANGED_SLOW_MONSTERS + EXPLODING_MONSTERS]
    if len(crowd) >= 2 and chokepoint_wait_pays(agent, crowd):
        priority -= np.minimum(get_attack_square_counts(agent, walkable), len(crowd))

    # TODO: figure out how to use corridors priority so that it improves the score
    # if len([m for m in monsters if m[3].mname not in chain(ONLY_RANGED_SLOW_MONSTERS, WEAK_MONSTERS)]) >= 4:
    #     priority += get_corridors_priority_map(walkable)
    # for _, _, _, mon, _ in monsters:
    #     if ord(mon.mlet) == MON.S_ANT:
    #         priority += get_corridors_priority_map(walkable)
    #         break

    # use relative priority to te current position
    priority -= priority[agent.blstats.y, agent.blstats.x]

    actions = get_available_actions(agent, monsters)
    if not any(a[1][0] in ('melee', 'ranged') for a in actions):
        actions.extend(goto_action(agent, priority, monsters))
    return priority, actions


def get_move_actions(agent, dis, move_priority_heatmap):
    """ Returns list of tuples (priority, ('move', dy, dx)) """
    ret = []
    for dy, dx in [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]:
        y, x = agent.blstats.y + dy, agent.blstats.x + dx
        if not 0 <= y < dis.shape[0] or not 0 <= x < dis.shape[1]:
            continue
        if not dis[y, x] == 1:
            continue

        if not np.isnan(move_priority_heatmap[y, x]):
            ret.append((move_priority_heatmap[y, x], ('move', dy, dx)))
    return ret
