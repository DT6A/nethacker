# heuristic monster types lists
# hypothesis: never melee the acid-passive sessile monsters (spotted jelly, green mold): each melee hit risks a passive acid splash that corrodes weapon and armour, and a spotted jelly's (level+1)d6 splash killed an XL 8 game on Dlvl 4.
# sources: https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/monst.c (spotted jelly ATTK(AT_NONE, AD_ACID, 0, 6), green mold ATTK(AT_NONE, AD_ACID, 0, 4)); passive() in uhitm.c; https://nethackwiki.com/wiki/Spotted_jelly ; https://nethackwiki.com/wiki/Green_mold ; https://nethackwiki.com/wiki/Passive_attack
from ..glyph import MON
from .monster_attacks import MELEE_ATTACKS

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


# A monster weapon attack adds dmgval() of what it wields to its own dice (mhitu.c hitmu); the early weapon users carry
# orcish daggers, short swords, aklyses, maces and crossbows, i.e. about a d6 at most.
WIELDED_WEAPON_MAX_DAMAGE = 6


def max_melee_damage(monster):
    """ Worst-case HP damage the monster's melee attacks deal in one hero turn (at speed 12). """
    _, _, _, mon, _ = monster
    total = 0
    for aatyp, _adtyp, damn, damd in MELEE_ATTACKS.get(mon.mname, ()):
        # mhitu.c hitmu: d(damn, damd), or d(m_lvl + 1, damd) when the attack lists no dice count
        dice = damn if damn else mon.mlevel + 1
        total += dice * damd
        if aatyp == 'WEAP':
            total += WIELDED_WEAPON_MAX_DAMAGE
    # a monster faster than the hero gets mmove/12 attack rounds per hero turn on average (mon.c mcalcmove)
    return total * max(1.0, mon.mmove / 12)


# hypothesis: the fixed "imminent death" line (HP <= 8, or <= 16 for dogs and insects) ignores what the adjacent monster
# can actually deal: a rothe (claw 1d3, bite 1d3, bite 1d8) takes 14 HP in one round, a Mordor orc or dwarf with its weapon
# 12-14, a soldier ant ~30 per hero turn, an owlbear 28, a mumak 60, so XL 5-9 heroes on Dlvl 3-5 kept stepping in and trading
# blows at 9-30 HP and died there (parent public seeds 1, 3, 7, 13: rothe, gnome mummy, mumak, Mordor orc). Using each
# monster's worst-case melee round from its monst.c attack table, the hero stays out of reach (and gets away from slower
# monsters) as soon as one round could kill it, while it still fights trivial monsters down to the old 8 HP line.
# sources: https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/monst.c (attack tables);
# NetHack 3.6.6 src/mhitu.c hitmu (d(damn,damd), d(m_lvl+1,damd) when damn is 0, + dmgval of the wielded weapon) and
# src/mon.c mcalcmove (speed); https://nethackwiki.com/wiki/Rothe ; https://nethackwiki.com/wiki/Standard_strategy
# ("if HP goes below half, run away"; look up a monster before fighting it); https://nethackwiki.com/wiki/Why_do_I_keep_dying ;
# https://nethackwiki.com/wiki/Things_To_Do_If_You%27re_Going_to_Die_Next_Turn ; past idea #72 (rothe flagged as dangerous,
# held-out +0.10 over its parent), generalised here to every monster; ported from tree node #303 (+0.0175 over its parent #295).
def imminent_death_on_melee(agent, monster):
    hp = agent.blstats.hitpoints
    if is_dangerous_monster(monster):
        if hp <= 16:
            return True
    elif hp <= 8:
        return True
    return hp <= max_melee_damage(monster)


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
