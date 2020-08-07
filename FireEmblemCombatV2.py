from DijkstraAlgorithm_Speedy_Custom import *
from FEH_definitions import *
from pprint import pprint
import FEH_StatGrowth

# TODO: rework loadfile output dicts to use id_nums tag as keys

DEBUG = False
from FireEmblemLoadJsonFilesBetterV2 import *

# FIXME: change casings
CONFIG = {
    "combat_animations": "off",
    "support_animations": "off",
    "foe/ally autobattle movement": "simple",
    "auto-favorite": "5",
    "starting a map": "go into battle",
    "smart end": "on",
    "show danger area": "off",
    "confirm action": "auto",
    "confirm move": "auto",
    "double tap to wait": "off",
    "auto-battle button": "all locations",
    "assist skills in auto": "no move skills",
    "auto-battle text": "auto-advance",
    "continous auto": "on",
    "map: no animation": "off",
    "auto: no animation": "off",
    "forging bonds: skip conversation": "off",
    "asset/flaw color display": "on",
    "sorting by level": "default",
    "duo hero display": "full",
    "no duo skill animation": "off",
    "tt difficulty tip": "on",
    "lost lore home notification": "on",
    "mjolnir's strike home notification": "on",  # FIXME: change mjolnir to include diacritics
    "voting gauntlet home notification": "on",
    "forging bonds home notification": "on",
    "compile CMs home notification": "on",
    "AR auto-dispatch home notification": "on",
    "enemy music": "on",
    "battle music": "on",
    "silent mode": "off",
    "BGM volume": 6,
    "SE volume": 5,
    "voice volume": 0,
}

# TODO: rework for compatibility with FEH maps (ex. initialize from map file or dict of tiles)
grid = Graph.init_as_grid(6, 8)

class SkillIsIncorrectCategoryException(Exception):
    pass

class ArbitraryAttributeClass:
    def __init__(self, **kwargs):
        # print(kwargs)
        if "input_dict" in kwargs:
            kwargs.update(kwargs["input_dict"])
            del kwargs["input_dict"]
        if "kwargs" in kwargs:
            kwargs.update(kwargs["kwargs"])
            del kwargs["kwargs"]
        for key in [_ for _ in kwargs]:
            # print(key, kwargs[key])
            setattr(self, key, kwargs[key])

    @classmethod
    def from_dict(cls, input_dict, **kwargs):
        return cls(input_dict=input_dict, kwargs=kwargs)

    def get_all_attrs(self):
        return self.__dict__


class Switch:
    @classmethod
    def validate_character_attribute(cls, key, value, verbose = False):

        # Create default return function
        # *args consumes "value" argument
        def default(*args):
            if verbose:
                print("No validation method exists for {0}, defaulting to valid".format(key))


        # Select validation method
        method_name = 'validate_' + str(key)
        # Get the method from 'self'. Defaults to default method.
        method = getattr(cls, method_name, default)
        # Call the method and return result, if no
        output = method(value)
        if output == 1 or output == 0:
            return output
        else:
            return 1

    @staticmethod
    def validate_rarity(value):
        if isinstance(value, int):
            if 1 <= value <= 5:
                return 1
        elif value is None:
            return 1
        return 0

    # TODO: Implement merged and high level unit support
    @staticmethod
    def validate_level(value):
        if isinstance(value, int):
            if 1 <= value <= 40:
                return 1
        elif value is None:
            return 1
        return 0

    @staticmethod
    def validate_pos(value):
        grid_size = grid.get_grid_width_height()
        if isinstance(value, tuple):
            if 1 <= value[0] <= grid_size[0] and 1 <= value[1] <= grid_size[1]:
                return 1
        elif value is None:
            return 1
        return 0

    @staticmethod
    def validate_move_range(value):
        if isinstance(value, int):
            if 1 <= value <= 3:
                return 1
        elif value is None:
            return 1
        return 0
        pass


class Skill(ArbitraryAttributeClass):
    def __init__(self, **kwargs):
        self.init_self_attributes()
        super().__init__(**kwargs)

    def init_self_attributes(self):

        # Full internal string identifier of the skill e.g. SID_ジークリンデ_共 for Sieglinde
        self.id_tag = None
        # Internal string identifier of the unrefined version of the weapon e.g. SID_ジークリンデ
        self.refine_base = None
        #  Internal string identifier of the skill name resource e.g. MSID_ジークリンデ
        self.name_id = None
        # Internal string identifier of the skill description resource, e.g. MSID_H_ジークリンデ改
        self.desc_id = None
        # Internal string identifier of the skill that gives rise to the refined skill effect, e.g. SID_強化共有R
        self.refine_id = None
        # Internal string identifier of the skill that activates while the unit is transformed into
        # a beast, e.g. SID_化身効果・奥義強化
        self.beast_effect_id = None
        # Internal string identifiers of skills required to learn the current skill.
        self.prerequisites = None
        # Internal string identifier of the canonical upgrade of the current skill. It is defined if and only if
        # promotion_rarity is not zero.
        self.next_skill = None
        # Filenames of the sprites used by the weapon, in this order: bow, weapon / arrow, map animation,
        # AoE Special map animation.
        self.sprites = None

        # Permanent stat bonuses of the skill. For weapons this does not include might.
        self.stats = None

        # A set of extra parameters that are used only for skill effects common to weapon classes for which
        # weapon_class_definition::is_staff, is_dagger, is_breath, or is_beast is true:
        #   - is_staff: If class_params.hp = 1, calculates damage from staff like other weapons.;
        #     If class_params.hp = 2, foe cannot counterattack.
        #   - is_dagger: After combat, if unit attacked, inflicts stat+class_params on target and foes within
        #     class_params.hp spaces of target through their next actions.
        #   - is_breath: If class_params.hp = 1, and if target_mov foe uses target_wep, calculates damage
        #     using the lower of foe's Def or Res.
        #   - is_beast: If class_params.hp = 1, at start of turn, if unit is adjacent to only beast or
        #     dragon allies or if unit is not adjacent to any ally, unit transforms (otherwise, unit reverts);
        #     if unit transforms, grants stat+class_params.
        self.class_params = None

        # Various skill parameters packed into a stat tuple. These do not necessarily represent stat values.
        # Their meanings depend on the skill abilities.
        self.skill_params = None

        # Stat bonuses of the skill's refinement, as shown on the weapon description.
        self.refine_stats = None
        # A unique increasing index for every skill, added to 0x10000000 for refined weapons.
        self.id_num = None
        # The internal sort value used in places such as the skill inheritance menu to order skills within
        # the same category according to their skill families.
        self.sort_id = None
        # The icon index of the skill, referring to the files UI/Skill_Passive*.png.
        self.icon_id = None
        # A bitmask indexed by weapon_index, with bits set for weapon classes that can equip the current skill.
        self.wep_equip = None
        # A bitmask indexed by move_index, with bits set for movement classes that can equip the current skill.
        self.mov_equip = None
        #  SP required to learn the given skill.
        self.sp_cost = None
        # Category of the skill.
        # 0	0xBC	Weapon
        # 1	0xBD	Assist
        # 2	0xBE	Special
        # 3	0xBF	Passive A
        # 4	0xB8	Passive B
        # 5	0xB9	Passive C
        # 6	0xBA	Sacred Seal
        # 7	0xBB	Refined weapon skill effect
        # 8	0xB4	Beast transformation effect
        self.category = None

        # The element type for tome weapon skills.
        self.tome_class = None
        # True if the skill cannot be inherited.
        self.exclusive = None
        # True if the skill can only be equipped by enemies.
        self.enemy_only = None
        # Range of the skill for weapons and Assists, 0 for other skills.
        self.range = None
        # Might for weapon skills, including bonuses that come from refinements, 0 for other skills.
        self.might = None
        # Cooldown count of the skill. The total cooldown count of a unit is the sum of cooldown_count
        # for all equipped skills. Skills that accelerate Special trigger have a negative value.
        self.cooldown_count = None
        # True if the skill grants Special cooldown count-1 to the unit after this Assist is used.
        self.assist_cd = None
        # True if the skill is a healing Assist skill.
        self.healing = None
        #  Range of the skill effect that comes with the given skill, e.g. 1 for Hone skills and
        #  weapons that give equivalent skill effects.
        self.skill_range = None
        # A value that roughly corresponds to the SP cost of the skill. Might have been used for Arena matches.
        self.score = None
        # 2 for a few low-tier Specials and staff weapons / Assists, 0 for highest-tier skills,
        # and 1 for everything else. Used by derived maps to determine how far skills are allowed to promote.
        self.promotion_tier = None
        # If non-zero, this skill would be promoted on derived maps if the unit's rarity is greater than or
        # equal to this value.
        self.promotion_rarity = None
        # True if the skill is a refined weapon.
        self.refined = None
        # Internal sort value for refined weapons: 1 and 2 for skills, 101 – 104 for Atk/Spd/Def/Res refinements,
        # 0 otherwise.
        self.refine_sort_id = None
        # A bitmask indexed by weapon_index, representing weapon class effectivenesses this skill grants.
        # Only meaningful on weapon skills.
        self.wep_effective = None
        # A bitmask indexed by move_index, representing movement class effectivenesses this skill grants.
        # Only meaningful on weapon skills.
        self.mov_effective = None
        # A bitmask indexed by weapon_index, representing weapon class effectivenesses this skill protects from.
        # Used by Breath of Blight.
        self.wep_shield = None
        # A bitmask indexed by move_index, representing movement class effectivenesses this skill protects from.
        self.mov_shield = None
        # A bitmask indexed by weapon_index, representing weapon class weaknesses this skill grants.
        # Used by Loptous.
        self.wep_weakness = None
        # A bitmask indexed by move_index, representing movement class weaknesses this skill grants.
        # Currently unused.
        self.mov_weakness = None
        # A bitmask indexed by weapon_index, representing weapon classes that receive damage from this
        # skill calculated using the lower of Def or Res. Used by breaths. Only meaningful on weapon skills.
        self.wep_adaptive = None
        # A bitmask indexed by move_index, representing movement classes that receive damage from this
        # skill calculated using the lower of Def or Res. Currently unused. Only meaningful on weapon skills.
        self.mov_adaptive = None
        # An index into the string table in Common/SRPG/SkillTiming.bin indicating the moment where the skill triggers.
        self.timing_id = None
        # An index into the string table in Common/SRPG/SkillAbility.bin indicating the skill effect type.
        # A skill can only contain one skill effect (refined weapons have an extra skill effect if
        # refine_id is non-null).
        self.ability_id = None
        # An index into the string table in Common/SRPG/SkillTiming.bin indicating the skill's activation restriction.
        self.limit1_id = None
        # Restriction-dependent parameters.
        self.limit1_params = None
        # An additional activation restriction on the given skill. Both must be satisfied for the skill to activate.
        self.limit2_id = None
        self.limit2_params = None
        # A bitmask indexed by weapon_index, representing the target's weapon classes required for the
        # skill's effect to activate. If zero, works on all weapon classes.
        self.target_wep = None
        # A bitmask indexed by move_index, representing the target's movement classes required for the
        # skill's effect to activate. If zero, works on all movement classes.
        self.target_mov = None
        # Like next_skill, except that this field is null for weapons, Spur Atk 2 does not point to Spur Atk 3,
        # and similarly for the three other Spur passives.
        # (Death Blow 3 pointed to Death Blow 4 even before the CYL2 update.)
        self.passive_next = None


        # A POSIX timestamp relative to the skill's release date; half a month into the future for skills
        # released before Version 2.0.0, 1 month into the future for skills released since Version 2.0.0.
        # This skill may be equipped by random units if timestamp is -1 or the current time is past timestamp.
        self.timestamp = None
        # Indicates whether random units can equip this skill. This affects Training Tower and Allegiance Battles.
        # It has 3 possible values:
        #   - 0: This skill may not be equipped on random units.
        #   - 10: This skill may be equipped on random units.
        #   - 20: Purpose unknown. Same effect as 10. Used by basic non-staff weapons
        #     (e.g. Iron Sword, Flametongue+, Adult (Cavalry)) and basic staff Assists.
        self.random_allowed = None
        # If non-zero, represent the lowest and highest levels respectively that allow random units
        # to equip the given skill.
        self.min_lv = None
        self.max_lv = None
        # If true, this skill may be considered by the 10th Stratum of the Training Tower for the
        # random skill pool if it is equipped by the corresponding unit from the base map.
        self.tt_inherit_base = None
        # Controls how random units may equip this skill. It has 3 possible values: (see #Random skills for details)
        #   - 0: This skill may not be equipped on random units.
        #   - 1: This skill may be equipped by any random unit.
        #   - 2: This skill may be equipped by random units that own the skill.
        self.random_mode = None


        # Unknown usage
        # self.range_shape = range_shape
        # self.id_tag2 = id_tag2
        # self.next_seal = next_seal
        # self.prev_seal = prev_seal
        # self.ss_coin = ss_coin
        # self.ss_badge_type = ss_badge_type
        # self.ss_badge = ss_badge
        # self.ss_great_badge = ss_great_badge

        pass


class Character(ArbitraryAttributeClass):
    def __init__(self, **kwargs):
        self.init_self_attributes()
        super().__init__(**kwargs)
        self.set_attribute_values()


    def __setattr__(self, key, value):

        if Switch.validate_character_attribute(key, value):
            super().__setattr__(key, value)
        else:
            raise ValueError("Invalid value supplied for {0} attribute of {1}".format(key, self))

        pass


    def init_self_attributes(self):

        self.id_tag = None
        self.roman = None
        self.face_name = None
        self.face_name2 = None
        self.legendary = None
        self.dragonflowers = None
        self.timestamp = None
        self.id_num = None
        self.sort_value = None
        self.origins = None
        self.weapon_type = None
        self.tome_class = None
        self.move_type = None
        self.series = None
        self.regular_hero = None
        self.permanent_hero = None
        self.base_vector_id = None
        self.refresher = None
        self.base_stats = None
        self.growth_rates = None
        # for given rarity, first 6 values (0-5) are default (already learned), remaining 8 (6-13) are unlockable
        # index 0 and index 6 are weapons
        # index 1 and index 7 are assists
        # index 2 and index 8 are specials
        # index 3 and index 9 are A slot (except for Drag Back on Gwendolyn)
        # index 4 and index 10 are B slot (Except Defiant Attack on Ogma)
        # index 5 and index 11 are C slot (Except HP+ on Abel)
        # index 12 is empty
        # index 13 is empty
        self.skills = None

        self.pos = None
        self.node = None
        self.move_range = None
        self.rarity = None
        self.level = None
        self.weapon = None
        self.stats = None

    # sets default values for character attributes
    def set_attribute_values(self):
        # if character's position is defined, sets "node" attribute to a Node object in the map grid and
        # sets node's "holds" attribute to character
        if self.pos:
            self.node = grid.nodes[grid.get_index_from_xy(self.pos)]
            self.node.holds = self
        if not self.move_range:
            self.move_range = move_data[self.move_type]["range"]
        if not self.rarity:
            self.rarity = 3
        if not self.level:
            self.level = 1
        # this doesn't seem right. What happens if character is created with weapon attribute defined?
        if not self.weapon:
            self.equip_weapon()

    def equip_weapon(self, **kwargs):

        if not "weapon" in kwargs:
            self.weapon = self.get_weapon()

        else:
            self.weapon = Weapon.from_dict(skills_data[1][kwargs["weapon"]])


        pass

    def get_weapon(self):
        weapon = None
        for i in range(self.rarity):
            weapon = self.skills[i][0] if self.skills[i][0] is not None else weapon
        if skills_data[1][weapon]["category"] == 0:
            return Weapon.from_dict(skills_data[1][weapon])
        else:
            raise SkillIsIncorrectCategoryException(str("Weapon should be a category 0 skill, received category " + str(skills_data[1][weapon]["category"]) + " skill instead"))
        pass



class Weapon(ArbitraryAttributeClass):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Enemy(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Player(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


skills_data, players_data, enemies_data, weapons_data, english_data, growth_data, move_data, stage_encount_data, \
terrain_data = load_files(Skill, Player, Enemy, Weapon, output_as_class=False)

name = translate_jp_to_en_dict(skills_data[1]["SID_ジークリンデ"], english_data, is_skill=True)

char_wep = Weapon.from_dict(skills_data[0][name])

# pprint(char_wep.get_all_attrs())

char = Character.from_dict(players_data[0]["EIRIK"], pos=(1,1))


def find_inconsistencies():
    for index in [9,10,11,12,13]:
        skillList = []
        cat = None
        allSkills = {}
        temp_set = set()
        for key, value in players_data[1].items():
            for rarity in range(5):
                iskill = value["skills"][rarity][index]

                if iskill is not None:
                    allSkills[iskill] = (skills_data[1][iskill], key)
                    skillList.append(skills_data[1][iskill]["category"])
                    cat = skillList[0]

        if len(set(skillList)) in [1, 0]:
            print("Category is", cat, "for index", index)
        else:
            print("Index", index, "is an aberrant")
            print("Counts:", ["Cat "+str(i)+": "+str(skillList.count(i)) for i in set(skillList)])
            temp_set = set(skillList)
            temp_dict = {k: v for k,v in zip([skillList.count(i) for i in temp_set], [i for i in temp_set])}
            wrong_cat = temp_dict[min(temp_dict.keys())]
            print("Wrong cat:", wrong_cat)
            for iskill, tup in allSkills.items():
                value = tup[0]
                key = tup[1]
                if value["category"] == wrong_cat:
                    print("On hero:", key, "("+str(players_data[1][key]["roman"])+")\n\t", value["id_tag"], ",",translate_jp_to_en_dict(value, english_data, is_skill=True))

        print("Index", index, "has", temp_set)
        print("")



def pos(expr):
    if expr < 0:
        return 0
    return expr


def neg(expr):
    if expr > 0:
        return 0
    return expr


def print_grid(grid):
    x, y = grid.get_grid_width_height()

    for iy in reversed(range(0, y)):
        row = []
        for ix in range(0, x):
            held = grid.nodes[iy * x + ix].holds
            if held == None:
                row.append("  ")
            elif held.__class__ == Enemy:
                row.append("x ")
            elif held.__class__ == Player:
                row.append("O ")
        print(row)


def program_instructions():

    testchar = Character.from_dict(players_data[1]["PID_クライネ"], level = 20, rarity = 5)



    pass


if __name__ == "__main__":
    program_instructions()
    print("Program execution complete; terminating process")
