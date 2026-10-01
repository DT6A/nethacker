"""Use a dropped scare-monster scroll as cover for the descent."""
import re

from nle.nethack import actions as A

from . import power, utils
from .combat import fight_heur
from .glyph import G, Hunger
from .strategy import Strategy


# hypothesis: a ground scare scroll lets a diver dig or fight safely against
# Castle minotaurs and humans that ignore Elbereth, preventing fatal interrupted digs.
# sources: https://nethackwiki.com/wiki/Scroll_of_scare_monster,
# https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/monmove.c (onscary),
# /refs/top/1c4099e80253/autoascend/dive_logic.py (gehennom_scare, _scare_hold_loop)
class ScareWard:
    HIT = re.compile(r'\b(The [\w -]+?|It) (hits|bites|butts|claws|kicks|stings|touches)!')
    IMMUNE = frozenset(('Wizard of Yendor', 'Angel', 'Aleax', 'couatl', 'ki-rin',
                       'Archon', 'Death', 'Famine', 'Pestilence', 'shopkeeper',
                       'aligned priest', 'high priest', 'unknown'))

    def __init__(self, dive):
        self.dive = dive
        self.agent = dive.agent
        self.spot = None
        self.started = 0
        self.labels = set()
        self.failed = set()

    def position(self):
        a = self.agent
        return a.current_level().key(), (a.blstats.y, a.blstats.x)

    def holding(self):
        if self.spot != self.position():
            return False
        a = self.agent
        adjacent = [m for m in a.get_visible_monsters()
                    if utils.adjacent((m[1], m[2]), self.spot[1])]
        # An unidentified pile may contain no ward. Abandon it on evidence of
        # melee damage; do not try another copy of the same appearances.
        if adjacent and self.HIT.search(a.message):
            self.failed.update(self.labels)
            self.spot = None
            return False
        below = a.inventory.items_below_me
        if below is not None and below and not any(power.is_scare_candidate(i) for i in below):
            self.spot = None
            return False
        return True

    @Strategy.wrap
    def strategy(self):
        a, d = self.agent, self.dive
        bl = a.blstats
        if not d.diving or bl.depth < 25 or d.castle.committed() or \
                d.levitating() or a.character.prop.polymorph or bl.hunger_state >= Hunger.WEAK:
            yield False
        if self.holding():
            yield True
            self.hold()
            return
        monsters = a.get_visible_monsters()
        near = [m for m in monsters if max(abs(m[1] - bl.y), abs(m[2] - bl.x)) <= 2]
        if not near or any(m[3].mname in self.IMMUNE for m in near):
            yield False
        if a.current_level().objects[bl.y, bl.x] in G.STAIR_UP | G.STAIR_DOWN:
            yield False
        bypass = any(d._melee_ignores_elbereth(m[3]) for m in near)
        if not bypass and not (d.in_gehennom() and bl.hitpoints < bl.max_hitpoints / 2):
            yield False
        known, candidates = power.scare_scrolls(a)
        drop = known[:1]
        if not drop and bypass:
            drop = [i for i, probability in candidates if probability > 0 and
                    a.inventory._scroll_key(i) not in self.failed]
        if not drop:
            yield False
        yield True
        # Commit state before the atomic drop can be interrupted by a preempt.
        self.spot = self.position()
        self.started = bl.time
        self.labels = {a.inventory._scroll_key(i) for i in drop}
        a.inventory.drop(drop, [1] * len(drop))
        a.inventory._note_dropped(drop, [1] * len(drop), force=True)
        self.hold()

    def hold(self):
        a, d = self.agent, self.dive
        while self.holding():
            bl = a.blstats
            monsters = a.get_visible_monsters()
            if bl.hunger_state >= Hunger.WEAK or bl.time - self.started >= 300 or \
                    (not monsters and bl.hitpoints >= .9 * bl.max_hitpoints):
                self.spot = None
                return
            before = a.step_count
            tool = d.digging_tool()
            if tool is not None and a.current_level().key() not in d.undiggable and \
                    not d.in_valley() and d._diggable_spot(bl.y, bl.x):
                d.dig_with_tool(tool)
            else:
                adjacent = [m for m in monsters if utils.adjacent((m[1], m[2]), (bl.y, bl.x))
                            and m[3].mname not in d.VALLEY_NO_MELEE]
                if adjacent and bl.hitpoints >= .3 * bl.max_hitpoints:
                    if not a.wield_best_melee_weapon():
                        a.melee_attack(adjacent[0][1], adjacent[0][2])
                else:
                    shots = []
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            if dy or dx:
                                shot = fight_heur.ranged_priority(a, dy, dx, monsters)
                                if shot is not None:
                                    shots.append((shot[0], dy, dx))
                    if shots:
                        _, dy, dx = max(shots)
                        a._fight2_perform_action(('ranged', dy, dx), 0)
                    else:
                        a.step(A.MiscDirection.WAIT)
            if before == a.step_count:
                self.spot = None
                return
