import re

import nle.nethack as nh
import numpy as np
from nle.nethack import actions as A

from .kernels import figure_out_monster_movement
from .. import jf_config, utils
from ..exceptions import AgentPanic
from ..glyph import C, G, MON


class MonsterTracker:
    _UNSEEN_ATTACK = re.compile(r"\bIt (?:hits|bites|misses|just misses|stings|touches|butts|kicks|claws|"
                                r"thrusts|swings|lashes|squeezes|gores|pummels|scratches|stabs|zaps|casts|spits)")
    # mhitu.c hitmsg()/missmu(): 'The rothe bites!', 'The pony kicks!', 'The giant ant misses!'
    _SEEN_ATTACK = re.compile(r"\bThe ([a-z][a-z -]*?) (?:bites|hits|kicks|butts|stings|touches you|misses|"
                              r"just misses)!")

    def __init__(self, agent):
        self.agent = agent
        self._unseen_attack_turn = -10 ** 6
        self._shk_seen = {}   # (level key, y, x) -> last turn a shopkeeper stood there
        self.on_panic()

    def on_panic(self):
        self._last_glyphs = None
        self.peaceful_monster_mask = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.monster_mask = np.zeros((C.SIZE_Y, C.SIZE_X), bool)

    def take_all_monsters(self):
        if utils.any_in(self.agent.glyphs, G.SWALLOW):
            return {}
        with self.agent.atom_operation():
            self.agent.step(A.Command.WHATIS, iter(['M']))
            if 'No monsters are currently shown on the map.' in self.agent.message:
                return {}
            try:
                index = self.agent.popup.index('All monsters currently shown on the map:')
            except IndexError:
                assert 0, (self.agent.message, self.agent.popup)
            regex = re.compile(r"^<(\d+),(\d+)>  ([\x00-\x7F])  ([a-zA-z-,' ]+)$")

            monsters = {}
            for line in self.agent.popup[index + 1:]:
                r = regex.search(line)
                assert r is not None, line
                x, y, char, name = r.groups()
                y, x = int(y), int(x) - 1

                # char_on_map = self.agent.last_observation['chars'][y, x]
                # assert ord(char) == char_on_map, (char, chr(char_on_map))

                monsters[y, x] = name
        return monsters

    def _get_current_masks(self):
        new_monster_mask = utils.isin(self.agent.glyphs, G.MONS, G.INVISIBLE_MON)
        new_monster_mask[self.agent.blstats.y, self.agent.blstats.x] = 0
        pet_mask = utils.isin(self.agent.glyphs, G.PETS)

        return new_monster_mask, pet_mask

    def update(self):
        new_monster_mask, _ = self._get_current_masks()

        if self._last_glyphs is None:
            new_peaceful_mons = None
        else:
            pea_mon = self._last_glyphs.copy()
            pea_mon[~self.peaceful_monster_mask] = -1
            agr_mon = self._last_glyphs.copy()
            agr_mon[~self.monster_mask | self.peaceful_monster_mask] = -1
            new_mon = self.agent.glyphs.copy()
            new_mon[~new_monster_mask] = -1
            new_peaceful_mons = figure_out_monster_movement(pea_mon, agr_mon, new_mon, max_radius=2)

        self.monster_mask = new_monster_mask
        self.peaceful_monster_mask.fill(0)
        if not self.agent.character.prop.hallu:
            if new_peaceful_mons is None:
                all_monsters = self.take_all_monsters()
                self.monster_mask, pet_mask = self._get_current_masks()  # glyphs can change sometimes after calling `take_all_monsters`
                for (y, x), name in all_monsters.items():
                    if not (self.monster_mask[y, x] or pet_mask[y, x] or (y, x) == (
                    self.agent.blstats.y, self.agent.blstats.x)):
                        raise AgentPanic('monsters differs between list and glyphs')
                    if 'peaceful' in name and not pet_mask[y, x]:
                        self.peaceful_monster_mask[y, x] = 1
            else:
                self.peaceful_monster_mask = new_peaceful_mons
        # TODO: on hallu no monsters are peaceful

        # an unseen monster ('I': felt while blind, or an invisible one) next to where a shopkeeper stood in
        # the last 30 turns is presumed to be him -- neither attacked nor walked into (a move into an 'I'
        # attacks it). A yellow light blinded an XL8 in a shop doorway; it swung at the 'I' next to it:
        # 'It gets angry!', and the shopkeeper's magic missiles killed it. Never once an unseen monster
        # attacks us: presuming every 'I' near a recently seen peaceful (Mines gnomes are everywhere) left
        # five of 60 games answering 'It hits!' / 'It bites!' with nothing (invisible centaurs, blinding ravens).
        t = self.agent.blstats.time
        key = self.agent.current_level().key()
        for y, x in zip(*utils.isin(self.agent.glyphs, G.SHOPKEEPER).nonzero()):
            self._shk_seen[(key, int(y), int(x))] = t
        unseen = self.agent.glyphs == nh.GLYPH_INVISIBLE
        if self._UNSEEN_ATTACK.search(self.agent.message):
            self._unseen_attack_turn = t
        if t - self._unseen_attack_turn <= 20:
            self.peaceful_monster_mask &= ~unseen
        elif unseen.any():
            for (k, sy, sx), st in self._shk_seen.items():
                if k == key and t - st <= 30:
                    near = np.s_[max(sy - 1, 0):sy + 2, max(sx - 1, 0):sx + 2]
                    self.peaceful_monster_mask[near] |= unseen[near] & self.monster_mask[near]

        if jf_config.HOSTILE_RECHECK and self.peaceful_monster_mask.any() and not self.agent.character.prop.hallu:
            self._recheck_attackers()

        assert (~self.peaceful_monster_mask | self.monster_mask).all()
        self._last_glyphs = self.agent.glyphs.copy()

    def _recheck_attackers(self):
        # hypothesis: the peaceful mask is carried from turn to turn by glyph movement (figure_out_monster_movement)
        # and never re-asked, so a monster marked peaceful -- a hostile look-alike that stepped where a peaceful one
        # was, or a peaceful one that turned hostile -- is skipped by fight2 / the Elbereth rest while it bites the
        # unarmoured (AC 10) Tourist in the Dlvl 1-4 grind. A peaceful monster never melees us (outside Conflict), so
        # 'The <name> bites!' with exactly one adjacent peaceful-marked <name> makes that one hostile (never an @:
        # shopkeepers, priests and the watch are not fought on a guess). Fewer early losses to an ignored attacker.
        # sources: NetHack 3.6.6 src/monmove.c dochug() (attacks only if !mpeaceful || Conflict), src/makemon.c
        #          peace_minded() (a neutral Tourist meets many peaceful neutrals), src/mhitu.c hitmsg()/missmu();
        #          https://nethackwiki.com/wiki/Peaceful, https://nethackwiki.com/wiki/Tourist,
        #          /refs/past_runs/20261008-213012/47.diff and 100.diff (kept 4 of 7 there, held-out never below parent)
        names = set(self._SEEN_ATTACK.findall(self.agent.message or ''))
        if not names:
            return
        y0, x0 = self.agent.blstats.y, self.agent.blstats.x
        seen = {}
        for y in range(max(y0 - 1, 0), min(y0 + 2, C.SIZE_Y)):
            for x in range(max(x0 - 1, 0), min(x0 + 2, C.SIZE_X)):
                g = self.agent.glyphs[y, x]
                if (y, x) == (y0, x0) or not self.monster_mask[y, x] or not MON.is_monster(g):
                    continue
                mon = MON.permonst(g)
                if mon.mname in names and ord(mon.mlet) != MON.S_HUMAN:
                    seen.setdefault(mon.mname, []).append((y, x))
        for name, squares in seen.items():
            if len(squares) == 1 and self.peaceful_monster_mask[squares[0]]:
                self.peaceful_monster_mask[squares[0]] = False
                self.agent.log(f'HOSTILE_RECHECK: the {name} at {squares[0]} attacked us: not peaceful')
