"""KNIGHT_CHIVALRY: the Knight's code of conduct (uhitm.c check_caitiff).

A lawful Knight that melees (or kicks: dokick.c kick_monster) a monster that can't move, is asleep or is fleeing
gets 'You caitiff!' and adjalign(-1) -- once per attack, every attack, as long as the monster flees (mavenge, the
"it attacked first" exemption, is never set in 3.6.6). Throws, wands and spells don't count. A record below 0 makes
pray.c can_pray answer p_type 1 (angrygods). Kills of always-hostile monsters give +5 back, but only up to
ALIGNLIM (10 + turns/200), and kills that aren't always-hostile (grid bugs, alignment 0) give nothing.

We know a monster flees from monmove.c monflee's own message ('The jackal turns to flee.', 'The immobile jackal seems
to flinch.'): it is printed when a seen monster starts fleeing, whatever the cause -- our Elbereth (distfleeck:
rnd(10) turns 6 times in 7), a hit below half HP (uhitm.c), a scare. A 'You caitiff!' after our own blow marks its
target the same way. A flagged monster is followed from square to square by its glyph."""

import re

from .. import jf_config
from ..glyph import MON

_FLEE_RE = re.compile(r"(?:^|[.!?] +)(?:The |the )?(?:immobile )?([a-z][a-zA-Z' -]*?) (?:turns to flee|seems to flinch)")
_CAITIFF_TURNS = 5   # after a 'You caitiff!': the target still flees (or is helpless) for a while at least
_FOLLOW = 3          # how far a flagged monster may move between two looks (speed <= 36)


class Chivalry:
    def __init__(self, agent):
        self.agent = agent
        self._flagged = {}       # level key -> list of [glyph, y, x, until turn]
        self._last_step = None
        self.last_melee = None   # (turn, level key, y, x, glyph) of our last melee_attack

    def active(self):
        from ..character import Character
        agent = self.agent
        return jf_config.KNIGHT_CHIVALRY and agent.character.role == Character.KNIGHT

    def _flag(self, key, glyph, y, x, until):
        entries = self._flagged.setdefault(key, [])
        for e in entries:
            if e[0] == glyph and (e[1], e[2]) == (y, x):
                e[3] = max(e[3], until)
                return
        entries.append([glyph, int(y), int(x), until])

    def observe(self):
        """Once per observation (agent.update): follow the flagged monsters, then read the new message."""
        agent = self.agent
        if agent.step_count == self._last_step:
            return
        self._last_step = agent.step_count
        if not self.active():
            return
        bl = agent.blstats
        key = agent.current_level().key()
        now = bl.time
        glyphs = agent.glyphs
        entries = [e for e in self._flagged.get(key, []) if e[3] >= now]
        for e in entries:
            glyph, y, x = e[0], e[1], e[2]
            if glyphs[y, x] == glyph:
                continue
            y0, x0 = max(y - _FOLLOW, 0), max(x - _FOLLOW, 0)
            ys, xs = (glyphs[y0:y + _FOLLOW + 1, x0:x + _FOLLOW + 1] == glyph).nonzero()
            if len(ys):
                i = min(range(len(ys)), key=lambda i: max(abs(int(ys[i]) + y0 - y), abs(int(xs[i]) + x0 - x)))
                e[1], e[2] = int(ys[i]) + y0, int(xs[i]) + x0
        self._flagged[key] = entries

        msg = agent.message or ''
        if agent.character.prop.hallu or not msg:
            return
        until = now + jf_config.KNIGHT_FLEE_TURNS
        for m in _FLEE_RE.finditer(msg):
            mid = MON.id_from_name(m.group(1).strip())
            if mid is None:
                continue
            glyph = MON.from_name(m.group(1).strip())
            ys, xs = (glyphs == glyph).nonzero()
            if len(ys):
                i = min(range(len(ys)), key=lambda i: max(abs(int(ys[i]) - bl.y), abs(int(xs[i]) - bl.x)))
                self._flag(key, glyph, ys[i], xs[i], until)
        if 'You caitiff!' in msg and self.last_melee is not None:
            turn, lkey, y, x, glyph = self.last_melee
            if lkey == key and now - turn <= 1 and MON.is_monster(glyph):
                self._flag(key, glyph, y, x, now + _CAITIFF_TURNS)

    def note_melee(self, y, x):
        agent = self.agent
        self.last_melee = (agent.blstats.time, agent.current_level().key(), int(y), int(x), int(agent.glyphs[y, x]))

    def holds_back(self, monster):
        """Leave this adjacent monster (a get_visible_monsters entry) unhit: a blow would be a caitiff's."""
        if not self.active():
            return False
        agent = self.agent
        _, y, x, _, glyph = monster
        now = agent.blstats.time
        if not any(e[3] >= now and e[0] == glyph and (e[1], e[2]) == (y, x)
                   for e in self._flagged.get(agent.current_level().key(), [])):
            return False
        # something is hurting us: fight back (a cornered fleeing monster still attacks, monmove.c dochug)
        if agent._hurt_recently(2):
            return False
        # a record at -10 or below gets no further caitiff penalty (check_caitiff returns early)
        pm = getattr(agent, 'prayer_model', None)
        if pm is not None and pm.record is not None and pm.record <= -10:
            return False
        return True
