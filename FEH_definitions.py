from pprint import pprint
from math import floor

weapon_index_dict = {k: v for k, v in zip([i for i in range(24)], [
    "Sword", "Lance", "Axe", "Red bow", "Blue bow", "Green bow", "Colorless bow", "Red Dagger", "Blue Dagger",
    "Green Dagger", "Colorless Dagger", "Red Tome", "Blue Tome", "Green Tome", "Colorless Tome", "Staff", "Red Breath",
    "Blue Breath", "Green Breath", "Colorless Breath", "Red Beast", "Blue Beast", "Green Beast", "Colorless Beast"
])}

move_index_dict = {0: "Infantry", 1: "Armored", 2: "Cavalry", 3: "Flying"}

magic_element_dict = {0: None, 1: "Fire", 2: "Thunder", 3: "Wind", 4: "Light", 5: "Dark", 6: "Earth"}

legendary_element_dict = {k: v for k, v in zip([i for i in range(9)], [None, "Fire", "Water", "Wind", "Earth", "Light",
                                                                       "Dark", "Astra", "Anima"])}

shard_color_dict = {0: "Universal", 1: "Scarlet", 2: "Azure", 3: "Verdant", 4: "Transparent"}

badge_color_dict = {0: "Scarlet", 1: "Azure", 2: "Verdant", 3: "Transparent"}


def ONES(x):
    return x % 10


def TENS(x):
    return floor(x / 10) % 10


def HUNDREDS(x):
    return floor(x / 100) % 10


def TENS_ONES(x):
    return x % 100


def WITHIN_RANGE(u):
    # within skill_range spaces of u
    pass


def WITHIN_COLUMN(u):
    # within (2 * skill_range + 1) columns centered on u
    pass


WITHIN_RANGE_EX_dict = {0: WITHIN_RANGE,
                        1: WITHIN_RANGE,  # used by duo skills
                        2: None,
                        # within (2 * ONES(skill_range) + 1) rows and (2 × TENS(skill_range) + 1) columns centered on u
                        3: None,  # in cardinal directions of u
                        4: None,  # within (2 × skill_range + 1) columns centered on u
                        5: None,  # within (2 × skill_range + 1) rows centered on u
                        }


def WITHIN_RANGE_EX(range_shape):
    return WITHIN_RANGE_EX_dict[range_shape]()


def COUNT_AROUND(u, v):
    # SkillLimit: the number of v within param1 spaces of u (excluding u)
    # SkillAbility: the number of v within skill_range spaces of u (excluding u)
    pass


def UNIT_NEAR(u):
    # if unit is WITHIN_RANGE(u)
    pass


def NEIGHBORHOOD(u):
    # u and units on u’s team WITHIN_RANGE(u)
    pass


def NEIGHBORHOOD_EX(u):
    # u and units on u’s team WITHIN_RANGE_EX(u)
    pass


STAT_dict = {0: "hp", 1: "atk", 2: "spd", 3: "def", 4: "res"}


def STAT(x):
    # TODO: add ability to reference actual stats
    return STAT_dict[x]
    pass


def STAT_DIFFERENCE(x, u):
    # TODO: (including Phantom skills)
    return STAT(x) - STAT(u)
    pass


# FIXME: rename func
def STAT_DIFFERENCE(stat, u):
    # unit’s stat − u’s stat (including Phantom skills)
    pass


def HP_BETWEEN(x, y, u):
    # x% ≤ u’s HP ≤ y%
    pass


def SKILL_TARGETS(u):
    # target_either = true: u is a target_mov unit or u uses target_wep
    # target_either = false: target_mov u uses target_wep
    pass


def TARGETED(u):
    # target_either = true: target_mov u and u using target_wep
    # target_either = false: target_mov u using target_wep
    pass


def COMBAT_BOOST(u):
    # for each stat, grants/inflicts stat+skill_params.stat to/on u during combat
    pass


def COMBAT_BOOST2(u):
    # for each stat, grants/inflicts stat+skill_params2.stat to/on u during combat
    pass


def COUNTER(u):
    # u can counterattack regardless of opponent’s range
    pass


def NO_COUNTER(u):
    # u cannot counterattack
    pass


def FOLLOW_UP(x, u):
    # x = 1: u makes a guaranteed follow-up attack
    # x = −1: u cannot make a follow-up attack
    pass


def NULL_FOLLOW_UP(x, y):
    # x = 1: neutralizes effects that guarantee foe’s follow-up attacks during combat
    # y = 1: neutralizes effects that prevent unit’s follow-up attacks during combat
    pass


def VANTAGE(u):
    # u can counterattack before opponent’s first attack
    pass


def DESPERATION(u):
    # u can make a follow-up attack before opponent can counterattack
    pass


def BRAVE(u):
    # u attacks twice
    pass


def CHARGE(mode, x, u):
    # mode = 0: grants/inflicts Special cooldown charge +x to/on u per attack during combat (Only highest value applied. Does not stack.)
    # mode = 1: grants/inflicts Special cooldown charge +x to/on u per u’s attack during combat (Only highest value applied. Does not stack.)
    # mode = 2: grants/inflicts Special cooldown charge +x to/on u per opponent of u’s attack during combat (Only highest value applied. Does not stack.)
    pass


def BLADE(u):
    # CHARGE(skill_params.hp; −skill_params.atk; u) and CHARGE(skill_params.hp; −skill_params.spd; u’s opponent)

    pass


def RAVEN(u):
    # grants weapon-triangle advantage to u against colorless opponents, and inflicts weapon-triangle
    # disadvantage on colorless opponents during combat
    pass


def CANCEL_AFFINITY(x, u):
    # x = 1: neutralizes weapon-triangle advantage granted by u’s skills
    # x = 2: if u has weapon-triangle advantage, neutralizes weapon-triangle advantage granted by u’s skills
    # x = 3: if u has weapon-triangle advantage, reverses weapon-triangle advantage granted by u’s skills
    pass


def ADAPTIVE(u):
    # calculates u’s damage during combat using the lower of opponent’s Def or Res
    pass


def ADAPTIVE_AOE(u):
    # calculates damage from u’s area-of-effect Specials using the lower of opponent’s Def or Res
    pass


def WRATHFUL_STAFF(u):
    # calculates damage from u’s staff like other weapons
    pass


def DAMAGE(x):
    # deals x damage
    pass


def COMBAT_ADD_HP(x, u):
    # restores x HP to u during combat
    pass


def MAX_ADD_HP(x, u):
    # x > 0: restores x HP to u
    # x < 0: deals −x damage to u
    pass


def COOLDOWN(x, u):
    # inflicts/grants Special cooldown count+x on/to u (Cannot exceed u’s maximum Special cooldown.
    # No effect if u does not have a Special skill.)
    pass


def BUFF(u):
    # for each stat,
    # skill_params.stat > 0: grants stat+skill_params.stat to u for 1 turn
    # skill_params.stat < 0: inflicts stat+skill_params.stat on u through their next actions
    pass


def BUFF2(u):
    # for each stat,
    # skill_params2.stat > 0: grants stat+skill_params2.stat to u for 1 turn
    # skill_params2.stat < 0: inflicts stat+skill_params2.stat on u through their next actions
    pass


STATUS_dict = {0: "Gravity", 1: "Panic", 2: "No counterattacks", 3: "March", 4: "Triangle Adept", 5: "Guard",
               6: "Air Orders", 7: "Isolation", 8: "Effective against dragons", 9: "Bonus doubler",
               10: "Dragon shield", 11: "Svalinn shield", 12: "Dominance", 13: "Resonance: Blades", 14: "Desperation"}


def STATUS(x):
    return STATUS_dict[x]


def ADD_STATUS(status, u):
    # grants/inflicts status to/on u
    pass


def SPECIAL_DAMAGE(x):
    # boosts damage by x
    pass


def LUNA(x):
    # treats foe’s Def/Res as if reduced by x%
    pass


ARENA_ASSAULT_ITEM_dict = {0: "Elixir",
                           1: "Fortifying Horn",
                           2: "Special Blade",
                           3: "Infantry Boots",
                           4: "Naga's Tear",
                           5: "Dancer's Veil",
                           6: "Lightning Charm",
                           7: "Panic Charm",
                           8: "Fear Charm",
                           9: "Pressure Charm"}


def ARENA_ASSAULT_ITEM(x):
    return ARENA_ASSAULT_ITEM_dict[x]
