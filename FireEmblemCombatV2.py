from DijkstraAlgorithm_Speedy_Custom import *
from typing import Union
# from FEH_definitions import *
import FEH_StatGrowth
from FireEmblemLoadJsonFilesBetterV2 import *
from math import trunc, floor

# TODO: rework loadfile output dicts to use id_nums tag as keys

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
GRID = Graph.init_as_grid(6, 8)

# ============================================================================================================
# MODULE LEVEL VARIABLE DEFINITIONS START

weapon_advantage = {
    1: 3,
    2: 1,
    3: 2
}

char_list = []

category_number_to_name_dict = {
    0: "weapon",
    1: "assist",
    2: "special",
    3: "a",
    4: "b",
    5: "c",
    6: "seal",
    7: "refined weapon skill",
    8: "beast transformation"
}

category_name_to_number_dict = {v:k for k,v in category_number_to_name_dict.items()}


# MODULE LEVEL VARIABLE DEFINITIONS END
# ============================================================================================================


# ============================================================================================================
# CUSTOM EXCEPTIONS DEFINITIONS START

class SkillIsIncorrectCategoryException(Exception):
    pass


class InvalidWeapon(Exception):
    pass


# CUSTOM EXCEPTIONS DEFINITIONS START
# ============================================================================================================


# ============================================================================================================
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
        def default(input_value):
            if verbose:
                print("Could not validate value {0} as no validation method exists for {0}, "
                      "defaulting to valid".format(input_value, key))

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
        grid_size = GRID.get_grid_width_height()
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

        self.range_shape = None

        self.target_either = None

        # Unknown usage
        # self.id_tag2 = id_tag2
        # self.next_seal = next_seal
        # self.prev_seal = prev_seal
        # self.ss_coin = ss_coin
        # self.ss_badge_type = ss_badge_type
        # self.ss_badge = ss_badge
        # self.ss_great_badge = ss_great_badge

        pass

    def targeted(self, items):

        if not self.target_either:
            return [i for i in items if i.target_mov == self.target_mov and i.target_wep == self.target_wep]
        else:
            return [i for i in items if i.target_mov == self.target_mov or i.target_wep == self.target_wep]


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

        char_list.append(self)

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
        self.affinity = None
        self.weapon: Union[Weapon, None] = None
        self.weapon_class = None
        self.stats = None
        self.color = None
        self.name = None
        self.equipped_skills = None

    # sets default values for character attributes
    def set_attribute_values(self):
        # if character's position is defined, sets "node" attribute to a Node object in the map grid and
        # sets node's "holds" attribute to character
        if self.pos:
            self.node = GRID.nodes[GRID.get_index_from_xy(self.pos)]
            self.node.holds = self
        if not self.move_range:
            self.move_range = move_data[self.move_type]["range"]
        if not self.rarity:
            self.rarity = 3
        if not self.level:
            self.level = 1
        if not self.affinity:
            self.affinity = 0
        if not self.stats:
            self.stats = self.base_stats
            self.set_stats_to_stats_for_level()

        if not self.color:
            self.color = weapon_index_to_color_dict[self.weapon_type]

        if not self.weapon_class:
            self.weapon_class = WeaponClass.from_dict(weapon_data_by_index[self.weapon_type])

        self.equip_weapon(weapon=self.weapon)

        if not self.name:
            self.name = str(translate_jp_to_en_class(self, english_data, prefix="MPID", old_prefix="PID"))

        if not self.equipped_skills:
            self.equipped_skills = {
                "assist": None,
                "special": None,
                "a": None,
                "b": None,
                "c": None,
                "seal": None
            }


    def validate_skill(self, skill: Skill):
        # checks if character is of correct weapon type and move type
        if in_bitmask(self.weapon_type, skill.wep_equip) and in_bitmask(self.move_type, skill.mov_equip):

            if skill.exclusive:
                # checks if character owns exclusive skill
                owns_skill = False
                for skillset in self.skills:
                    if skill.id_tag in skillset:
                        owns_skill = True
                        break
                if not owns_skill:
                    return False

            if skill.enemy_only:
                # checks if character is an enemy
                if not (self.__class__ == Enemy or self.id_tag.startswith("EID_")):
                    return False

            if skill.healing:
                # checks if character is a staff unit
                if self.weapon_type != 15:
                    return False

            return True

        return False
        pass

    def get_skill(self, category: str):
        skill = None
        category = category_name_to_number_dict[category]
        for i in range(self.rarity):
            skill = self.skills[i][category] if self.skills[i][category] is not None else skill
        if skills_data[1][skill]["category"] == category:
            return Skill.from_dict(skills_data[1][skill])
        else:
            raise SkillIsIncorrectCategoryException(
                "Skill should be a category {0} skill, received category {1} skill instead".format(category, str(
                skills_data[1][skill]["category"]))
            )
        pass


    def equip_skill(self, skill: str):
        if skill is not None:
            # create Skill object from weapon id
            skill = Skill.from_dict(skills_data[1][skill])
            # check whether character can equip skill
            if self.validate_skill(skill):

                category = category_number_to_name_dict[skill.category]

                # if character already has a weapon equipped, unequip it
                if self.equipped_skills[category]:
                    self.unequip_skill(category)

                # # add weapon's might to character's attack stat
                # self.stats["atk"] += weapon.might

                # add skill's stat bonuses to character's stats
                for stat in skill.stats:
                    self.stats[stat] += skill.stats[stat]

                # update character's equipped_skills attribute with skill
                self.equipped_skills[category] = skill

            else:
                # if skill fails to pass validation, character cannot equip skill
                raise InvalidWeapon("Character {0} does not have access to skill {1}".format(self, skill.id_tag))


    def unequip_skill(self, category: str):
        skill = self.equipped_skills[category]
        if skill is not None:
            if isinstance(skill, Skill):
                for stat in skill.stats:
                    self.stats[stat] -= skill.stats[stat]

            self.equipped_skills[category] = None
        pass

    # TODO: Add in support for automatic skill/weapon generation for TT and the like
    # checks whether character may possess weapon
    def validate_weapon(self, weapon: Weapon):
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

    def get_distance_to(self, enemy: "Character"):
        get_distance(self, enemy)

    def calc_weapon_triangle(self, enemy: "Character"):
        # if character has weapon triangle advantage, increase attack by 20%
        if enemy.color == weapon_advantage[self.color]:
            return 0.2
        # if character has weapon triangle disadvantage, decrease attack by 20%
        elif self.color == weapon_advantage[enemy.color]:
            return -0.2
        # if character has neither weapon triangle advantage or disadvantage, do not modify attack
        # if either character or enemy is colorless, weapon triangle does not apply
        # FIXME: Add support for raven-tomes and weapon triangle advantage against colorless
        elif self.color == enemy.color or self.color == "gray" or enemy.color == "gray":
            return 0

    # calculates whether unit has weapon effectiveness against enemy
    def calc_effectiveness(self, enemy: "Character"):
        # assertions used to force IDE autocompletion
        assert isinstance(enemy.weapon, Weapon)
        assert isinstance(self.weapon, Weapon)

        # bitmask of movement types unit has effectiveness against
        mov_effective = self.weapon.mov_effective
        # bitmask of weapon types unit has effectiveness against
        wep_effective = self.weapon.wep_effective

        # if unit is effective against enemy movement type or enemy has movement weakness,
        # and enemy does not have a movement shield effect, then deal 50% extra damage
        if (in_bitmask(enemy.move_type, mov_effective)
            or in_bitmask(enemy.weapon.mov_weakness, mov_effective)) \
                and not in_bitmask(enemy.weapon.mov_shield, mov_effective):
            return 1.5

        # if unit is effective against enemy weapon type or enemy has weapon weakness,
        # and enemy does not have a weapon shield effect, then deal 50% extra damage
        if (in_bitmask(enemy.weapon_type, wep_effective)
            or in_bitmask(enemy.weapon.wep_weakness, wep_effective)) \
                and not in_bitmask(enemy.weapon.wep_shield, wep_effective):
            return 1.5

        # otherwise, deal normal damage
        return 1

    def calc_boosted_damage(self, enemy: "Character"):
        return 0
        # TODO: add functionality

    def set_stats_to_stats_for_level(self):
        stat_increases = FEH_StatGrowth.get_all_stat_increases_for_level(self)
        for stat in stat_increases:
            self.stats[stat] = self.base_stats[stat] + stat_increases[stat]

    def attack_enemy(self, enemy: "Character"):
        assert isinstance(self.weapon, Weapon)
        assert isinstance(enemy.weapon, Weapon)

        if enemy.pos == self.pos:
            print("You can't attack yourself silly")
            return None
        if enemy.HP > 0:
            if self.get_distance_to(enemy) == self.weapon.range:
                print("Enemy in range, commencing attack")
                # TODO: Add support for adaptive damage
                mitigation = enemy.stats["def"] if self.weapon.tome_class == 0 else enemy.stats["res"]

                damage = pos(floor(self.stats["atk"] * self.calc_effectiveness(enemy)) + trunc(
                    floor(self.stats["atk"] * self.calc_effectiveness(enemy)) * (self.calc_weapon_triangle(enemy) * (
                            self.affinity + 20) / 20)) + self.calc_boosted_damage(enemy) - mitigation)
                enemy.HP = enemy.HP - damage

                if enemy.HP > 0:
                    print(self.name, "dealt", damage, "damage,", enemy.name, "has", enemy.HP, "HP remaining")
                else:
                    print(self.name, "dealt", damage, "damage,", enemy.name, "has been defeated")
                    GRID.nodes[GRID.get_index_from_xy(enemy.pos)].holds = None
                return None
            print("Enemy not in range")
        else:
            print("Enemy has already been defeated")

    def attack_node(self, node: Node):
        enemy = GRID.nodes[GRID.get_index_from_xy(node)].holds
        if enemy is not None:
            self.attack_enemy(enemy)
        else:
            print("There is no enemy at position", node)

    def move(self, new_pos: tuple):
        print(self.name, "moved", get_distance_from_tuples(self.pos, new_pos), "spaces from", self.pos, "to", new_pos)
        GRID.nodes[GRID.get_index_from_xy(self.pos)].holds = None
        self.pos = new_pos
        GRID.nodes[GRID.get_index_from_xy(new_pos)].holds = self

    def fight(self, enemy: "Character"):
        # TODO: Add check for vantage skill
        self.attack_enemy(enemy)
        if enemy.stats["hp"] > 0:
            # TODO: Add checks for "prevent counterattack" status, weapon range, distant/close counter skills
            # TODO: Add check for desperation skill
            enemy.attack_enemy(self)
            if self.stats["spd"] >= enemy.stats["spd"] + 5 and self.stats["hp"] > 0:
                self.attack_enemy(enemy)
            elif enemy.stats["spd"] >= self.stats["spd"] + 5:
                enemy.attack_enemy(self)

    def move_to_attack(self, enemy: "Character"):
        endpoints = GRID.dijkstra(enemy.pos, eval_to_length=self.weapon.range)

        endpoints = [i for i in [points[-1] if get_distance_from_tuples(enemy.pos, points[-1].data) ==
                                               self.weapon.range else None for (weight, points) in endpoints] if
                     i is not None]

        endpoints = [endpoint for endpoint in endpoints if
                     get_distance_from_tuples(self.pos, endpoint.data) <= self.move_range]

        if len(endpoints) == 0:
            print("No available moves that can target", enemy.name)
        else:
            endpoint = endpoints[0]
            print("Chose position", endpoint.data, "from possible positions", [endpoint.data for endpoint in endpoints])

            if endpoint.data == self.pos:
                print(self.name, "stays where they are and attacks", enemy.name, "at position", enemy.pos)
            else:
                print(self.name, "moves to", endpoint.data, "to attack", enemy.name, "at position", enemy.pos)
                self.move(endpoint.data)

            self.fight(enemy)

    def move_towards(self, enemy: "Character"):
        weight, nodes = GRID.dijkstra(self.pos, enemy.pos, only_end=True)[0]

        distance = get_distance_from_tuples(self.pos, enemy.pos)

        if distance == self.weapon.range:
            print(self.name, "is already in range and does not move")

        if distance > self.weapon.range:
            move_distance = distance - self.weapon.range
            if move_distance > self.move_range:
                self.move(nodes[self.move_range].data)
            else:
                self.move(nodes[move_distance].data)
            pass

        if distance < self.weapon.range:
            print(self.name, "is too close and moves further away")


class Enemy(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Player(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# CLASS DEFINITIONS END
# ============================================================================================================


# load all necessary data from JSON files
skills_data, players_data, enemies_data, weapons_data, english_data, growth_data, move_data, stage_encount_data, \
terrain_data = load_files(Skill, Player, Enemy, Weapon, output_as_class=False)

weapon_data_by_index = {v["index"]: v for v in weapons_data[1].values()}

colors_by_weapon_index = [1, 2, 3, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 0, 1, 2, 3, 0, 1, 2, 3, 0]
weapon_index_to_color_dict = {k: v for k, v in zip([i for i in range(24)], colors_by_weapon_index)}


# ============================================================================================================
# GENERAL DEFINITIONS START

def get_distance_from_tuples(self: tuple, enemy: tuple):
    return abs(enemy[0] - self[0]) + abs(enemy[1] - self[1])


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


def print_grid(input_grid):
    x, y = input_grid.get_grid_width_height()

    for iy in reversed(range(0, y)):
        row = []
        for ix in range(0, x):
            held = input_grid.nodes[iy * x + ix].holds
            if held is None:
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


def in_range(away, origin, distance):
    if get_distance_from_tuples(away, origin) > distance:
        return 0
    return 1


def ones(x):
    return x % 10


def tens(x):
    return floor(x / 10) % 10


def hundreds(x):
    return floor(x / 100) % 10


def tens_ones(x):
    return x % 100


condition_dict = {
    "within_range": "in_range(node.data, origin, distance)",
    "within_columns": "in_range((node.data[0], 0), (origin[0], 0), distance)",
    "within_rows": "in_range((0, node.data[1]), (0, origin[1]), distance)",
    "in_cardinals": "node.data[0] == origin[0] or node.data[1] == origin[1]",
    "within_area": "in_range((node.data[0], 0), (origin[0], 0), ones(distance)) and "
                   "in_range((0, node.data[1]), (0, origin[1]), tens(distance))"
}


def within_range_abstracted(unit: Character, skill: Skill, condition, grid: Graph = GRID):
    within_range_list = list()

    origin = unit.pos
    distance = skill.skill_range

    for node in grid.nodes:
        if node.holds and node.holds != unit and eval(condition_dict[condition]):
            within_range_list.append(node.holds)

    return within_range_list


WITHIN_RANGE_EX_dict = {0: "within_range",  # within range distance of unit
                        1: "within_range",  # same as 0; used by duo skills
                        2: "within_area",  # within ONES(distance) rows and TENS(distance) columns of unit
                        3: "in_cardinals",  # in cardinal directions of unit
                        4: "within_columns",  # within distance columns of unit
                        5: "within_rows",  # within distance rows of unit
                        }


# returns list of characters within range of unit where range is determined by range_shape
def within_range_ex_abstract(range_shape: int, unit, skill, grid: Graph = GRID):
    return within_range_abstracted(unit, skill, WITHIN_RANGE_EX_dict[range_shape], grid)


def foes(items):
    return [i for i in items if i.__class__ == Enemy]


def allies(items):
    return [i for i in items if i.__class__ == Player]



# GENERAL DEFINITIONS END
# ============================================================================================================

def main_game_loop():



    pass


def program_instructions():
    testchar = Character.from_dict(players_data[0]["PID_Clarisse"], weapon="SID_鉄の弓")
    print(testchar.stats)
    testchar.unequip_weapon()
    print(testchar.stats)
    testchar.equip_weapon("SID_狙撃手の弓")
    print(testchar.stats)

    print("")

    pass


if __name__ == "__main__":
    prog_start = time()
    program_instructions()
    prog_stop = time()
    print("\nTime elapsed:", prog_stop - prog_start)
    print("Program execution complete; terminating process")
