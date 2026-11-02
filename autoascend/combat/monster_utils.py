# heuristic monster types lists
# hypothesis: never melee the acid-passive sessile monsters (spotted jelly, green mold): each melee hit risks a passive acid splash that corrodes weapon and armour, and a spotted jelly's (level+1)d6 splash killed an XL 8 game on Dlvl 4.
# sources: https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/monst.c (spotted jelly ATTK(AT_NONE, AD_ACID, 0, 6), green mold ATTK(AT_NONE, AD_ACID, 0, 4)); passive() in uhitm.c; https://nethackwiki.com/wiki/Spotted_jelly ; https://nethackwiki.com/wiki/Green_mold ; https://nethackwiki.com/wiki/Passive_attack
from ..glyph import MON
from .monster_attacks import MELEE_ATTACKS, PASSIVE_ATTACKS

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
    return hp <= max_melee_damage(monster) + max_passive_damage(agent, monster)


# hypothesis: fight2 judged a melee exchange only by the monster's own attacks, but an energy vortex (passive shock
# 7d4), fire vortex and fire elemental (passive fire 9d4), red mold (fire 4d4) and ochre jelly (acid 3d6) hit back
# every time the hero swings at them -- shock, fire and cold on 2/3 of swings while the monster lives even when the
# hero misses, acid on half of the hits -- so heroes at XL 9-12 kept trading blows with them down to death (energy
# vortex and fire elemental are among this run's commonest killers: ~30 and 11 deaths over nodes >= 376). Adding the
# worst-case passive to the "one exchange can kill me" line makes the hero stop closing in / meleeing them in time
# and use ranged attacks, Elbereth or a step back instead; cold is skipped for the cold-resistant Valkyrie.
# sources: https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/monst.c (AT_NONE attacks:
#   energy vortex ATTK(AT_NONE, AD_ELEC, 0, 4), fire vortex/fire elemental ATTK(AT_NONE, AD_FIRE, 0, 4), ...);
#   https://raw.githubusercontent.com/NetHack/NetHack/NetHack-3.6.6_Released/src/uhitm.c passive() (d(damn,damd) or
#   d(m_lev+1,damd); AD_ACID if mhit && rn2(2); AD_FIRE/AD_COLD/AD_ELEC if malive && !mcan && rn2(3), hit or miss);
#   src/role.c (Valkyrie intrinsic cold resistance); https://nethackwiki.com/wiki/Passive_attack ;
#   https://nethackwiki.com/wiki/Energy_vortex ("A ranged attack is all but required to dispatch of an energy vortex
#   quickly since it will not trigger the passive attacks") ; https://nethackwiki.com/wiki/Fire_elemental ; https://nethackwiki.com/wiki/Fire_vortex
#   ported to this chain (#414 -> #420 -> #427) from tree node #425 (+0.021 over its parent #422: public +0.034,
#   held-out and dev equal); my parent's public seed 5 dies to an energy vortex (XL 11) and seed 11 to a fire
#   elemental (XL 10). Player advice: Usenet 1999 thread on Valkyries with 90-140 HP lost to energy vortices
#   (https://www.alt.org/nethack/mirror/www.nethack.de/spoiler/energy_vortex.txt: "pretty nasty", get shock resistance
#   or escape) ; no passive when the blow kills, ranged attacks avoid it (https://nethackwiki.com/wiki/Passive_attack)
def max_passive_damage(agent, monster):
    """ Worst-case HP damage the monster's passive attacks deal back to the hero for one melee swing at it. """
    _, _, _, mon, _ = monster
    total = 0
    for adtyp, damn, damd in PASSIVE_ATTACKS.get(mon.mname, ()):
        if adtyp == 'COLD' and agent.character.role == agent.character.VALKYRIE:
            continue
        total += (damn if damn else mon.mlevel + 1) * damd
    return total


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
