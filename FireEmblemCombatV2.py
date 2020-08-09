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


#============================================================================================================
# MODULE LEVEL VARIABLE DEFINITIONS START

weapon_advantage = {
    "Red": "Green",
    "Blue": "Red",
    "Green": "Blue"
}

# MODULE LEVEL VARIABLE DEFINITIONS END
#============================================================================================================


#============================================================================================================
# CUSTOM EXCEPTIONS DEFINITIONS START

class SkillIsIncorrectCategoryException(Exception):
    pass


class InvalidWeapon(Exception):
    pass

# CUSTOM EXCEPTIONS DEFINITIONS START
#============================================================================================================


#============================================================================================================
# CLASS DEFINITIONS START

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
    def validate_character_attribute(cls, key, value, verbose=False):

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


# NOT TO BE CONFUSED WITH THE WEAPON CLASS
# This refers to the a weapon's base weapon-class.
# For example, the base weapon class of Clarisse's Sniper's Bow is colorless bow
class WeaponClass(ArbitraryAttributeClass):
    def __init__(self, **kwargs):
        self.init_self_attributes()
        super().__init__(**kwargs)

    def init_self_attributes(self):
        self.id_tag = None
        self.sprite_base = None
        self.base_weapon = None
        self.index = None
        self.color = None
        self.range = None
        self._unknown1 = None
        self.sort_id = None
        self.equip_group = None
        self.res_damage = None
        self.is_staff = None
        self.is_dagger = None
        self.is_breath = None
        self.is_beast = None

    # def __eq__(self, other):
    #     if isinstance(other, WeaponClass):
    #         return self.id_tag == other.id_tag
    #     elif isinstance(other, int):
    #         return self.index == other
    #     elif isinstance(other, str):
    #         return self.id_tag == other
    #     else:
    #         raise TypeError("Type WeaponClass and type {0} cannot be compared".format(type(other)))
    #     pass


class Weapon(Skill):
    def __init__(self, **kwargs):
        self.init_self_attributes()
        super().__init__(**kwargs)
        self.set_attribute_values()

    def init_self_attributes(self):
        super().init_self_attributes()
        self.weapon_class = None

    def set_attribute_values(self):
        if not self.weapon_class:
            self.weapon_class = self.get_base_weapon_class(self)

    @staticmethod
    def get_base_weapon_class(weapon):
        weapon_data_by_base_weapon_id = {v["base_weapon"]: v for v in weapons_data[1].values()}

        # FIXME: This can probably be combined and made more compact
        prereqs = list(filter(lambda pr: pr is not None, weapon.prerequisites))
        if len(prereqs) == 0:
            if weapon.id_tag in weapon_data_by_base_weapon_id:
                # do stuff in weapon.json
                base_weapon_class = weapon_data_by_base_weapon_id[weapon.id_tag]
            else:
                bin_list = list(map(int, list(bin(weapon.mov_equip)[2:])))
                base_weapon_class = weapon_data_by_index[len(bin_list) - 1 - bin_list.index(1)]

        else:
            prereq = prereqs[0]
            while True:
                prereqs = list(filter(lambda pr: pr is not None, skills_data[1][prereq]["prerequisites"]))
                if len(prereqs) == 0:
                    base_weapon_class = weapon_data_by_base_weapon_id[prereq]
                    break
                else:
                    prereq = prereqs[0]
        return WeaponClass.from_dict(base_weapon_class)


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

    def __repr__(self):
        return "{0}, {1} ({2} object with id {3})".format(self.id_tag, self.roman, self.__class__, id(self))

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
        self.weapon_class = None
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
        if not self.stats:
            self.stats = self.base_stats

        if not self.weapon_class:
            self.weapon_class = WeaponClass.from_dict(weapon_data_by_index[self.weapon_type])

        self.equip_weapon(weapon=self.weapon)

    # TODO: Add in support for automatic skill/weapon generation for TT and the like
    # checks whether character may possess weapon
    def validate_weapon(self, weapon):
        """

        :type weapon: Weapon
        """

        # checks if character is of correct weapon type and move type
        if in_bitmask(self.weapon_type, weapon.wep_equip) and in_bitmask(self.move_type, weapon.mov_equip):

            # FIXME: Does not currently support refined weapons
            # Idea for refined weapons: check num of underscores, greater than 1, remove suffix and check base
            if weapon.exclusive:
                # checks if character owns exclusive weapon
                owns_weapon = False
                for skillset in self.skills:
                    if weapon.id_tag in skillset:
                        owns_weapon = True
                        break
                if not owns_weapon:
                    return False

            if weapon.enemy_only:
                # checks if character is an enemy
                if not (self.__class__ == Enemy or self.id_tag.startswith("EID_")):
                    return False

            return True

        return False

    def get_weapon(self):
        weapon = None
        for i in range(self.rarity):
            weapon = self.skills[i][0] if self.skills[i][0] is not None else weapon
        if skills_data[1][weapon]["category"] == 0:
            return Weapon.from_dict(skills_data[1][weapon])
        else:
            raise SkillIsIncorrectCategoryException(str("Weapon should be a category 0 skill, received category " + str(
                skills_data[1][weapon]["category"]) + " skill instead"))
        pass

    # handles equipping a weapon to a character
    def equip_weapon(self, weapon: str):
        if weapon is not None:
            # create weapon object from weapon id
            weapon = Weapon.from_dict(skills_data[1][weapon])
            # check whether character can equip weapon
            if self.validate_weapon(weapon):

                # if character already has a weapon equipped, unequip it
                if self.weapon:
                    self.unequip_weapon()

                # add weapon's might to character's attack stat
                self.stats["atk"] += weapon.might

                # add weapon's stat bonuses to character's stats (separate from might)
                for stat in weapon.stats:
                    self.stats[stat] += weapon.stats[stat]

                # set character's weapon attribute to weapon
                self.weapon = weapon

            else:
                # if weapon fails to pass validation, character cannot equip weapon
                raise InvalidWeapon("Character {0} does not have access to weapon {1}".format(self, weapon.id_tag))

        # if weapon to equip is None, unequip weapon
        else:
            self.unequip_weapon()

    def unequip_weapon(self):
        if self.weapon is not None:
            if isinstance(self.weapon, Weapon):
                self.stats["atk"] -= self.weapon.might

                for stat in self.weapon.stats:
                    self.stats[stat] -= self.weapon.stats[stat]

            self.weapon = None

    def get_distance_to(self, enemy):
        get_distance(self, enemy)

    # TODO: Work on this next coding session
    # def calc_weapon_triangle(self, enemy):
    #     if enemy.color == weapon_advantage[self.color]:
    #         return 0.2
    #     elif self.color == weapon_advantage[enemy.color]:
    #         return -0.2
    #     elif self.color == enemy.color or self.color == "gray" or enemy.color == "gray":
    #         return 0


class Enemy(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Player(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# CLASS DEFINITIONS END
#============================================================================================================


# load all necessary data from JSON files
skills_data, players_data, enemies_data, weapons_data, english_data, growth_data, move_data, stage_encount_data, \
    terrain_data = load_files(Skill, Player, Enemy, Weapon, output_as_class=False)

weapon_data_by_index = {v["index"]: v for v in weapons_data[1].values()}


weapon_index_to_color_dict = {k: v for k, v in zip([i for i in range(24)],
                               [1, 2, 3, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 0, 1, 2, 3, 0, 1, 2, 3, 0])}


#============================================================================================================
# GENERAL FUNCTION DEFINITIONS START

def get_distance(self: Character, enemy: Character):
    return abs(enemy.pos[0] - self.pos[0]) + abs(enemy.pos[1] - self.pos[1])

def in_bitmask(nums, bitmask: int):
    bitmask_list = list(map(int, list(bin(bitmask)[::-1][:-2])))

    in_bitmask_dict = dict()

    if isinstance(nums, int):
        if len(bitmask_list) < nums:
            return False
        return True if bitmask_list[nums] == 1 else False

    for num in nums:
        if bitmask_list[num] == 1:
            in_bitmask_dict[num] = True
        else:
            in_bitmask_dict[num] = False
    return in_bitmask_dict


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

def find_inconsistencies():
    for index in [9, 10, 11, 12, 13]:
        skill_list = []
        cat = None
        all_skills = {}
        temp_set = set()
        for key, value in players_data[1].items():
            for rarity in range(5):
                iskill = value["skills"][rarity][index]

                if iskill is not None:
                    all_skills[iskill] = (skills_data[1][iskill], key)
                    skill_list.append(skills_data[1][iskill]["category"])
                    cat = skill_list[0]

        if len(set(skill_list)) in [1, 0]:
            print("Category is", cat, "for index", index)
        else:
            print("Index", index, "is an aberrant")
            print("Counts:", ["Cat " + str(i) + ": " + str(skill_list.count(i)) for i in set(skill_list)])
            temp_set = set(skill_list)
            temp_dict = {k: v for k, v in zip([skill_list.count(i) for i in temp_set], [i for i in temp_set])}
            wrong_cat = temp_dict[min(temp_dict.keys())]
            print("Wrong cat:", wrong_cat)
            for iskill, tup in all_skills.items():
                value = tup[0]
                key = tup[1]
                if value["category"] == wrong_cat:
                    print("On hero:", key, "(" + str(players_data[1][key]["roman"]) + ")\n\t", value["id_tag"], ",",
                          translate_jp_to_en_dict(value, english_data, is_skill=True))

        print("Index", index, "has", temp_set)
        print("")

# GENERAL FUNCTION DEFINITIONS END
#============================================================================================================

def program_instructions():
    testchar = Character.from_dict(players_data[1]["PID_クライネ"], weapon="SID_鉄の弓")
    testchar.unequip_weapon()
    testchar.equip_weapon("SID_狙撃手の弓")

    name = translate_jp_to_en_dict(skills_data[1]["SID_ジークリンデ"], english_data, is_skill=True)

    char_wep = Weapon.from_dict(skills_data[0][name])

    char = Character.from_dict(players_data[0]["EIRIK"], pos=(1, 1))

    pass


if __name__ == "__main__":
    prog_start = time()
    program_instructions()
    prog_stop = time()
    print("\nTime elapsed:", prog_stop - prog_start)
    print("Program execution complete; terminating process")
