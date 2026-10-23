# heuristic monster types lists
# hypothesis: never melee the acid-passive sessile monsters (spotted jelly, green mold): each melee hit risks a passive acid splash that corrodes weapon and armour, and a spotted jelly's (level+1)d6 splash killed an XL 8 game on Dlvl 4.
# sources: https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/monst.c (spotted jelly ATTK(AT_NONE, AD_ACID, 0, 6), green mold ATTK(AT_NONE, AD_ACID, 0, 4)); passive() in uhitm.c; https://nethackwiki.com/wiki/Spotted_jelly ; https://nethackwiki.com/wiki/Green_mold ; https://nethackwiki.com/wiki/Passive_attack
from ..glyph import MON

ONLY_RANGED_SLOW_MONSTERS = ['floating eye', 'blue jelly', 'brown mold', 'gas spore', 'acid blob', 'spotted jelly', 'green mold']
EXPLODING_MONSTERS = ['yellow light', 'gas spore', 'flaming sphere', 'freezing sphere', 'shocking sphere']
INSECTS = ['giant ant', 'killer bee', 'soldier ant', 'fire ant', 'giant beetle', 'queen bee']
WEAK_MONSTERS = ['lichen', 'newt', 'shrieker', 'grid bug']
WEIRD_MONSTERS = ['leprechaun', 'nymph']


# hypothesis: Elbereth never scares '@' humans and elves or minotaurs (3.6.6 onscary()), so the hero must fight such a monster instead of waiting on the engraving while it keeps hitting.
# sources: https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/monmove.c (onscary: mlet == S_HUMAN, PM_MINOTAUR); https://nethackwiki.com/wiki/Elbereth ; https://nethackwiki.com/wiki/Woodland-elf
def ignores_elbereth(monster):
    _, _, _, mon, _ = monster
    return ord(mon.mlet) == MON.S_HUMAN or mon.mname == 'minotaur'


def is_monster_faster(agent, monster):
    _, y, x, mon, _ = monster
    # TOOD: implement properly
    return 'bat' in mon.mname or 'dog' in mon.mname or 'cat' in mon.mname \
           or 'kitten' in mon.mname or 'pony' in mon.mname or 'horse' in mon.mname \
           or 'bee' in mon.mname or 'fox' in mon.mname


def imminent_death_on_melee(agent, monster):
    if is_dangerous_monster(monster):
        return agent.blstats.hitpoints <= 16
    return agent.blstats.hitpoints <= 8


def is_dangerous_monster(monster):
    _, y, x, mon, _ = monster
    is_pet = 'dog' in mon.mname or 'cat' in mon.mname or 'kitten' in mon.mname or 'pony' in mon.mname \
             or 'horse' in mon.mname
    # 'mumak' in mon.mname or 'orc' in mon.mname or 'rothe' in mon.mname \
    # or 'were' in mon.mname or 'unicorn' in mon.mname or 'elf' in mon.mname or 'leocrotta' in mon.mname \
    # or 'mimic' in mon.mname
    return is_pet or mon.mname in INSECTS


def consider_melee_only_ranged_if_hp_full(agent, monster):
    return monster[3].mname in ('brown mold', 'blue jelly') and agent.blstats.hitpoints == agent.blstats.max_hitpoints
