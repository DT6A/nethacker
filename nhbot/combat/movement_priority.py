from .. import jf_config
from ..glyph import Hunger
from ..utils import adjacent
from . import utils
from .monster_utils import WEAK_MONSTERS, ONLY_RANGED_SLOW_MONSTERS, consider_melee_only_ranged_if_hp_full, \
    imminent_death_on_melee, EXPLODING_MONSTERS, WEIRD_MONSTERS


def _draw_around(priority, y, x, value, radius=1, operation='add'):
    # TODO: optimize
    for y1 in range(y - radius, y + radius + 1):
        for x1 in range(x - radius, x + radius + 1):
            if max(abs(y1 - y), abs(x1 - x)) != radius:
                continue
            if 0 <= y1 < priority.shape[0] and 0 <= x1 < priority.shape[1]:
                if operation == 'add':
                    priority[y1, x1] += value
                elif operation == 'max':
                    priority[y1, x1] = max(priority[y1, x1], value)
                else:
                    assert 0, operation


def _draw_ranged(priority, y, x, value, walkable, radius=1, operation='add'):
    # TODO: optimize
    for direction_y in (-1, 0, 1):
        for direction_x in (-1, 0, 1):
            if direction_y != 0 or direction_x != 0:
                for i in range(1, radius + 1):
                    y1 = y + direction_y * i
                    x1 = x + direction_x * i
                    if 0 <= y1 < priority.shape[0] and 0 <= x1 < priority.shape[1]:
                        if not walkable[y1, x1]:
                            break
                        if operation == 'add':
                            priority[y1, x1] += value
                        elif operation == 'max':
                            priority[y1, x1] = max(priority[y1, x1], value)
                        else:
                            assert 0, operation


THIEF_OTHERS_DIFFICULTY = 3   # jackals, coyotes, newts, rats...: not a reason to let the thief go


def thief_chase(agent, monster):
    """THIEF_CHASE_TURNS: this is the monkey that ran off with our item lately (agent._thief), we are healthy, and it
    is the only hostile in view bar trivial ones: close in on it (and keep a throwing line) instead of the strike-first standoff
    that a monster fleeing at our speed never walks into."""
    thief = getattr(agent, '_thief', None)
    if thief is None or not jf_config.THIEF_CHASE_TURNS:
        return False
    _, y, x, mon, _ = monster
    bl, level = agent.blstats, agent.current_level()
    if mon.mname != thief[1] or thief[0] != level.key() or not 0 <= bl.time - thief[2] <= jf_config.THIEF_CHASE_TURNS:
        return False
    if bl.hitpoints < jf_config.THIEF_CHASE_HP * bl.max_hitpoints or bl.hunger_state >= Hunger.WEAK or \
            level.shop[y, x] or agent.character.prop.polymorph:
        return False
    return all(m[3].mname == thief[1] or getattr(m[3], 'difficulty', 99) <= THIEF_OTHERS_DIFFICULTY
               for m in agent.get_visible_monsters())


def zapper_here(agent, monster):
    """ZAPPER_RUSH: this is (our best guess at) the monster that zapped a wand at us lately (agent._zapper)."""
    z = getattr(agent, '_zapper', None)
    if z is None or not jf_config.ZAPPER_RUSH:
        return False
    _, y, x, mon, _ = monster
    return mon.mname == z[1] and (int(y), int(x)) == (z[2], z[3]) and agent.zapper_kind(mon.mname)


def zapper_rush(agent, monster):
    """ZAPPER_RUSH: healthy enough to walk through a zap or two and kill the zapper in melee."""
    bl = agent.blstats
    return bl.hitpoints >= max(jf_config.ZAPPER_RUSH_MIN_HP, jf_config.ZAPPER_RUSH_HP * bl.max_hitpoints) and \
        not imminent_death_on_melee(agent, monster) and not agent.character.prop.polymorph


def draw_monster_priority_positive(agent, monster, priority, walkable):
    _, y, x, mon, _ = monster

    # don't move into the monster
    priority[y, x] = float('nan')

    if thief_chase(agent, monster):
        _draw_around(priority, y, x, 2, radius=1, operation='max')
        _draw_around(priority, y, x, 1, radius=2, operation='max')
        if len(agent.inventory.get_ranged_combinations()):
            _draw_ranged(priority, y, x, 1, walkable, radius=7, operation='max')
        return

    # hypothesis: a wand zapper fires whenever it is lined up with us and can move and zap in the same turn, so the
    # strike-first standoff two squares off is a firing range; next to it it zaps too, but each of our hits now
    # counts, and a hill orc / gnome lord with a wand dies in 2-3 hits (agent._update_zapper_state).
    # sources: https://nethackwiki.com/wiki/Muse.c ; https://nethackwiki.com/wiki/Monmove.c ;
    # https://nethackwiki.com/wiki/Movement_tactics ; NetHack 3.6.6 src/muse.c find_offensive, src/monmove.c dochug
    if zapper_here(agent, monster) and zapper_rush(agent, monster):
        _draw_around(priority, y, x, 4, radius=1, operation='max')
        _draw_around(priority, y, x, 2, radius=2, operation='max')   # off its lines: a knight's move away
        return

    if mon.mname in WEAK_MONSTERS:
        # weak monster - freely engage in melee
        _draw_around(priority, y, x, 2, radius=1, operation='max')
        _draw_around(priority, y, x, 1, radius=2, operation='max')
    elif 'mold' in mon.mname and mon.mname not in ONLY_RANGED_SLOW_MONSTERS:
        if agent.blstats.hitpoints >= 15 or agent.blstats.hitpoints == agent.blstats.max_hitpoints:
            # freely engage in melee
            _draw_around(priority, y, x, 2, radius=1, operation='max')
            _draw_around(priority, y, x, 1, radius=2, operation='max')
        if len(agent.inventory.get_ranged_combinations()):
            _draw_ranged(priority, y, x, 1, walkable, radius=7, operation='max')
    elif mon.mname in ONLY_RANGED_SLOW_MONSTERS:  # and agent.inventory.get_ranged_combinations():
        if consider_melee_only_ranged_if_hp_full(agent, monster):
            _draw_around(priority, y, x, 2, radius=1, operation='max')
            _draw_around(priority, y, x, 1, radius=2, operation='max')
        if len(agent.inventory.get_ranged_combinations()):
            _draw_ranged(priority, y, x, 1, walkable, radius=7, operation='max')
    elif 'unicorn' in mon.mname:
        if agent.blstats.hitpoints >= 15 or agent.blstats.hitpoints == agent.blstats.max_hitpoints:
            # freely engage in melee
            _draw_around(priority, y, x, 2, radius=1, operation='max')
            _draw_around(priority, y, x, 1, radius=2, operation='max')
    else:
        if not imminent_death_on_melee(agent, monster) and not utils.wielding_ranged_weapon(agent):
            # engage, but ensure striking first if possible
            if mon.mmove <= 12:
                _draw_around(priority, y, x, 3, radius=2, operation='max')
            else:
                _draw_around(priority, y, x, 3, radius=3, operation='max')
        if utils.wielding_ranged_weapon(agent):
            _draw_ranged(priority, y, x, 4, walkable, radius=7, operation='max')
        elif len(agent.inventory.get_ranged_combinations()):
            _draw_ranged(priority, y, x, 1, walkable, radius=7, operation='max')


def draw_monster_priority_negative(agent, monster, priority, walkable):
    _, y, x, mon, _ = monster

    if thief_chase(agent, monster):
        return

    if zapper_here(agent, monster):
        # ZAPPER_RUSH: its lines of fire beyond melee reach (find_offensive needs lined_up(): row, column or
        # diagonal, BOLT_LIM 8 squares); the squares next to it are left to the melee drawing
        _draw_ranged(priority, y, x, -3, walkable, radius=7)
        _draw_ranged(priority, y, x, 3, walkable, radius=1)
        if zapper_rush(agent, monster):
            return

    if imminent_death_on_melee(agent, monster) and not mon.mname in WEAK_MONSTERS \
            and not mon.mname in ONLY_RANGED_SLOW_MONSTERS:
        if mon.mmove <= 12:
            _draw_around(priority, y, x, -10, radius=1)
        else:
            if adjacent((agent.blstats.y, agent.blstats.x), (y, x)):
                # no point in running -- monster is fast
                pass
            else:
                _draw_around(priority, y, x, -10, radius=2)
                _draw_around(priority, y, x, -5, radius=1)

        if not len(agent.inventory.get_ranged_combinations()):
            # prefer avoiding being in line of fire
            _draw_ranged(priority, y, x, -1, walkable, radius=7)

    # if agent.blstats.hitpoints <= 8 and not is_monster_faster(agent, monster) and not mon.mname in WEAK_MONSTERS \
    #         and not mon.mname in ONLY_RANGED_SLOW_MONSTERS:
    #     # stay out of melee range
    #     _draw_around(priority, y, x, -10, radius=1)
    #     if not len(agent.inventory.get_ranged_combinations()):
    #         # prefer avoiding being in line of fire
    #         _draw_ranged(priority, y, x, -1, walkable, radius=7)

    if mon.mname in EXPLODING_MONSTERS:
        _draw_around(priority, y, x, -10, radius=1)
        if mon.mname not in ONLY_RANGED_SLOW_MONSTERS:
            _draw_around(priority, y, x, -5, radius=2)
        _draw_ranged(priority, y, x, 4, walkable, radius=7)
    elif 'mold' in mon.mname and mon.mname not in ONLY_RANGED_SLOW_MONSTERS:
        # prioritize staying in ranged weapons line of fire
        if len(agent.inventory.get_ranged_combinations()):
            _draw_ranged(priority, y, x, 2, walkable, radius=7)
    elif mon.mname in WEIRD_MONSTERS:
        # stay away
        _draw_around(priority, y, x, -10, radius=1)
        # prioritize staying in ranged weapons line of fire
        if len(agent.inventory.get_ranged_combinations()):
            _draw_ranged(priority, y, x, 6, walkable, radius=7)
    elif mon.mname == 'gelatinous cube':
        # its touch paralyses (and it engulfs): keep out of reach -- it is slow (6), walking away always
        # works (14 games stood next to one on an item pile until 'You are frozen by the gelatinous cube!')
        _draw_around(priority, y, x, -10, radius=1)
        _draw_around(priority, y, x, -3, radius=2)
    elif mon.mname in ONLY_RANGED_SLOW_MONSTERS:  # and agent.inventory.get_ranged_combinations():
        # ignore
        pass
    elif 'unicorn' in mon.mname:
        pass
    else:
        if mon.mname not in WEAK_MONSTERS:
            # engage, but ensure striking first if possible
            _draw_around(priority, y, x, -9, radius=1)
            if not len(agent.inventory.get_ranged_combinations()):
                _draw_ranged(priority, y, x, -1, walkable, radius=7)

    if mon.mname == 'purple worm' and len(agent.inventory.get_ranged_combinations()):
        _draw_around(priority, y, x, -10, radius=1)
