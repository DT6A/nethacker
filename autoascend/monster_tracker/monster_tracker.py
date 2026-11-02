import re

import numpy as np
from nle.nethack import actions as A

from .kernels import figure_out_monster_movement
from .. import utils
from ..exceptions import AgentPanic
from ..glyph import C, G, MON

# attacks NetHack reports for a monster attacking the hero (mhitu.c hitmsg/missmu/wildmiss, "The <mon> hits!");
# a monster attacking another monster always names its target ("The dwarf hits the gnome."), so it does not match
_ATTACK_ON_HERO = r'(?:hits|bites|kicks|butts|stings|claws|scratches|misses|just misses|touches you|grabs you|' \
                  r'swings|thrusts|lashes)'


class MonsterTracker:
    def __init__(self, agent):
        self.agent = agent
        # (y, x) -> (glyph, turn, level) of peacefuls whose "Really attack?" prompt was declined; kept across panics
        self.declined_attacks = {}
        self.on_panic()

    def on_panic(self):
        self._last_glyphs = None
        self.peaceful_monster_mask = np.zeros((C.SIZE_Y, C.SIZE_X), bool)
        self.monster_mask = np.zeros((C.SIZE_Y, C.SIZE_X), bool)

    def decline_attack(self, y, x, glyph):
        self.declined_attacks[y, x] = (glyph, self.agent.blstats.time,
                                       (self.agent.blstats.dungeon_number, self.agent.blstats.level_number))

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

    # hypothesis: the movement kernel below only carries the old label along, so a monster once seen as peaceful
    #   stays "peaceful" for as long as it is tracked, even after it turned hostile -- hit by a stray thrown dagger
    #   or a bounced ray ("The tengu gets angry!"), an angry watch or shopkeeper, a lawful sasquatch/tengu/dwarf next
    #   to it. fight2 ignores it (get_visible_monsters drops the peaceful mask) while it mauls the hero: parent public
    #   seed 6 at T18157-18186 (XL 10, 93 max HP) -- a sasquatch and a tengu kept the peaceful label for 30 turns of
    #   "The sasquatch hits!", the bot quaffed, applied a bag, picked up items and searched until HP 0 (saved only by
    #   an amulet of life saving); stale labels also seen with soldier ants, killer bees, a rothe and a watch captain.
    #   A peaceful monster never attacks the hero (mhitu.c mattacku is only reached for a hostile or a conflicted
    #   one), so an attack-on-hero message from a monster labelled peaceful, or any "gets angry", now forces the
    #   full zero-time WHATIS rescan that reads every monster's real peaceful status from the game.
    # sources: diagnosis replay of parent public seed 6 (message log + monster_tracker masks per step);
    #   NetHack 3.6.6 src/mhitu.c (hitmsg "The %s hits!", missmu "The %s misses!"), src/mon.c setmangry()
    #   ("%s gets angry!"), src/monmove.c (peacefuls do not attack unless Conflict); https://nethackwiki.com/wiki/Peaceful
    #   ("Hitting a peaceful monster with a spell, a zapped wand that damages them, or a thrown item" angers it;
    #   "A peaceful monster will not attack the hero");
    #   https://nethackwiki.com/wiki/Tengu, https://nethackwiki.com/wiki/Sasquatch (lawful: often peaceful to lawfuls)
    def _peaceful_turned_hostile(self):
        if self._last_glyphs is None or not self.peaceful_monster_mask.any():
            return False
        message = self.agent.message
        if not message:
            return False
        if 'gets angry' in message:
            return True
        names = set()
        for y, x in zip(*self.peaceful_monster_mask.nonzero()):
            glyph = self._last_glyphs[y, x]
            if MON.is_monster(glyph):
                names.add(MON.permonst(glyph).mname)
        return any(re.search(r'\b' + re.escape(name) + r' ' + _ATTACK_ON_HERO + r'\b', message, re.IGNORECASE)
                   for name in names)

    def update(self):
        new_monster_mask, _ = self._get_current_masks()

        if self._last_glyphs is None or (not self.agent.character.prop.hallu and self._peaceful_turned_hostile()):
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

        # NetHack asked before letting us hit these, so they are peaceful even if the movement tracking missed it;
        # forget the mark once the monster moves away/changes, on another level or after 20 turns
        level = (self.agent.blstats.dungeon_number, self.agent.blstats.level_number)
        for (y, x), (glyph, turn, lvl) in list(self.declined_attacks.items()):
            if self.agent.blstats.time - turn > 20 or lvl != level or self.agent.glyphs[y, x] != glyph:
                del self.declined_attacks[y, x]
            elif self.monster_mask[y, x]:
                self.peaceful_monster_mask[y, x] = 1

        assert (~self.peaceful_monster_mask | self.monster_mask).all()
        self._last_glyphs = self.agent.glyphs.copy()
