import json
import os
from time import time
from dprint import dprint
from FEH_definitions import weapon_index_dict


def remove_digits(input_string: str) -> str:
    remove_digits_translation_table = str.maketrans('', '', "0123456789")
    output_string = input_string.translate(remove_digits_translation_table)
    return output_string


def translate_jp_to_en_dict(input_dict, english_data, tag="id_tag", prefix="MSID_", old_prefix="SID_", is_skill=False):
    # this was the result of like 4 days with no sleep, constantly coding, I have no idea how it works
    if is_skill:
        output = None
        try:
            if input_dict["refined"]:
                output = str(translate_jp_to_en_dict(input_dict, english_data, tag="refine_base")) + "_" + (
                    input_dict["id_tag"].split("_")[-1])
            else:
                try:
                    output = translate_jp_to_en_dict(input_dict, english_data)

                except KeyError:
                    # dprint("\n")

                    if input_dict["beast_effect_id"] is not None and input_dict["category"] == 8:
                        # output = translate_jp_to_en_dict(input_dict, english_data, prefix="MSID_H_")
                        return None

                    # dprint("Beast effect id:", input_dict["beast_effect_id"], "Category:", input_dict["category"])
                    # this means it's a duo effect or something similar (beast effect?), doesn't catch all duos
                    if input_dict["beast_effect_id"] is None and input_dict["category"] == 8:
                        # duo skills don't have names, but they do have descriptions
                        # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]

                        if input_dict["wep_equip"] == 0 and input_dict["skill_range"] == 0:
                            # print("Weird beast thing, not touching it")
                            return None

                        dprint("Duo Effect:", english_data[input_dict["id_tag"].replace("SID_", "MSID_H_")])
                        # print(skillsDict[skill].id_tag.replace("SID_", "MSID_H_"))
                        return None

                    if input_dict["id_tag"] == "SID_無し":
                        return "blank"

                    # category 7 refers to refined weapon skill effects, these normally have an R in them
                    # these also do not have a translation because they are simply an additional effect that is
                    # added onto the base weapon
                    # you could find the base weapon by iterating through all skill dicts and checking if they have
                    # an entry in their "refine_id" key and creating a dict that links all "refine_id" values to
                    # the value/entry in their "id_tag" key (so dicts would take form key = refine_id value,
                    # value = id_tag value)
                    if input_dict["category"] != 7:
                        output = translate_jp_to_en_dict(input_dict, english_data, prefix="MSID_H_")
                    # dprint("\n Yo")
                    pass

            return output

        except KeyError as e:
            print("Error:", e)
        pass
    else:
        return english_data[input_dict[tag].replace(old_prefix, prefix)]
    raise Exception("How did you get here")


def translate_jp_to_en_class(input_class, english_data, attribute="id_tag", prefix="MSID_", old_prefix="SID_",
                             is_skill=False):
    # this was the result of like 4 days with no sleep, constantly coding, I have no idea how it works
    if is_skill:
        output = None
        try:
            if getattr(input_class, "refined"):
                output = str(translate_jp_to_en_class(input_class, english_data, attribute="refine_base")) + "_" + (
                    getattr(input_class, "id_tag").split("_")[-1])
            else:
                try:
                    output = translate_jp_to_en_class(input_class, english_data)

                except KeyError:
                    dprint("\n")

                    if getattr(input_class, "beast_effect_id") is not None and getattr(input_class, "category") == 8:
                        # output = translate_jp_to_en_class(input_class, english_data, prefix="MSID_H_")
                        return None

                    # dprint("Beast effect id:", input_dict["beast_effect_id"], "Category:", input_dict["category"])
                    # this means it's a duo effect or something similar (beast effect?), doesn't catch all duos
                    if getattr(input_class, "beast_effect_id") is None and getattr(input_class, "category") == 8:
                        # duo skills don't have names, but they do have descriptions
                        # skillsDict[skill].roman_name = english_data[skillsDict[skill].id_tag.replace("SID_", "MSID_")]

                        if getattr(input_class, "wep_equip") == 0 and getattr(input_class, "skill_range") == 0:
                            # print("Weird beast thing, not touching it")
                            return None

                        dprint("Duo Effect:", english_data[getattr(input_class, "id_tag").replace("SID_", "MSID_H_")])
                        # print(skillsDict[skill].id_tag.replace("SID_", "MSID_H_"))
                        return None

                    if getattr(input_class, "id_tag") == "SID_無し":
                        return "blank"

                    # category 7 refers to refined weapon skill effects, these normally have an R in them
                    # these also do not have a translation because they are simply an additional effect that is
                    # added onto the base weapon
                    # you could find the base weapon by iterating through all skill dicts and checking if they have
                    # an entry in their "refine_id" key and creating a dict that links all "refine_id" values to
                    # the value/entry in their "id_tag" key (so dicts would take form key = refine_id value,
                    # value = id_tag value)
                    if getattr(input_class, "category") != 7:
                        output = translate_jp_to_en_class(input_class, english_data, prefix="MSID_H_")
                    dprint("\n")
                    pass

            return output

        except KeyError as e:
            print("Error:", e)
        pass
    else:
        return english_data[getattr(input_class, attribute).replace(old_prefix, prefix)]
    raise Exception("How did you get here")


def my_merger(list_of_dicts):
    my_dict = {}
    for idict in list_of_dicts:
        my_dict[idict["key"]] = idict["value"]
    return my_dict


def load_files(skill_class, player_class, enemy_class, weapon_class, output_as_class=True, get_english_data=True,
               get_skills=True, get_characters=True, get_weapons=True, get_growth=True, get_move=True,
               get_stage_encount=True, get_terrain=True):
    # print("Starting")
    start = time()

    english_data = {}

    if get_english_data:
        os.chdir(r"C:\Users\admin\PycharmProjects\FireEmblemClone\HertzDevil_JSON_assets\USEN\Message\Data")

        total = int()
        for file in os.listdir():
            dprint("Processing:", file)
            with open(file, "r", encoding="utf-8") as english_json_data:
                english_data[file.replace(".json", "")] = json.load(english_json_data)
                dprint(len(english_data[file.replace(".json", "")]))
                total += len(english_data[file.replace(".json", "")])
        dprint("Total:", total)

        my_list = []
        for english_data_entry in english_data:
            my_list.extend(english_data[english_data_entry])

        english_data = my_merger(my_list)

    def my_merger2(list_of_dicts, output_class):
        my_dict = {}
        my_dict2 = {}
        for idict in list_of_dicts:

            if idict["id_tag"] == "PID_無し" or idict["id_tag"] == "EID_無し":
                # maybe insert something that just uses these as blanks?
                continue

            # FIXME: Change from using "roman" to translating using USEN data files (PID to MPID)
            # if output_class == player_class or output_class == enemy_class:
            #     if output_as_class:
            #         my_dict[idict["roman"]] = output_class.from_dict(input_dict=idict)
            #     else:
            #         my_dict[idict["roman"]] = idict

            if output_class == player_class:
                translated_name = translate_jp_to_en_dict(idict, english_data, prefix="MPID", old_prefix="PID")

                unit_identifiers = remove_digits(str(idict["roman"])).split("_")[1:]

                # suffix that identifies unit as male version (used for protagonists)
                if "M" in unit_identifiers:
                    suffix = "_M"
                # suffix that identifies unit as female version (used for protagonists)
                elif "F" in unit_identifiers:
                    suffix = "_F"
                # elif "A" in unit_identifiers:
                #     suffix = "_A"
                else:
                    suffix = ""

                prefix_dict = {
                    "A": "Adult_",  # prefix that identifies hero as an adult alt
                    "POPULARITY": "Brave_",  # prefix that identifies hero as a brave alt
                    "DANCE": "Dancer_",  # prefix that identifies hero as a dancer alt
                    "PAIR": "Duo_",  # prefix that identifies hero as a duo unit
                    "LEGEND": "Legendary_",  # prefix that identifies hero as a legendary hero
                    "GOD": "Mythic_",  # prefix that identifies hero as a mythic hero
                    "BRIDE": "Bridal_",  # prefix that identifies hero as a bridal alt
                    "DARK": "Fallen_",  # prefix that identifies hero as a fallen alt
                    "HALLOWEEN": "Halloween_",  # prefix that identifies hero as a halloween alt
                    "SUMMER": "Summer_",  # prefix that identifies hero as a summer alt
                    "PICNIC": "Picnic_",  # prefix that identifies hero as a picnic alt
                    "SPRING": "Spring_",  # prefix that identifies hero as a spring alt
                    "VALENTINE": "Valentine_",  # prefix that identifies hero as a valentine alt
                    "WINTER": "Winter_",  # prefix that identifies hero as a winter alt
                    "ONSEN": "HotSprings_",  # prefix that identifies hero as a Hot Springs alt
                    "DREAM": "Adrift_",  # prefix that identifies hero as an adrift alt
                    "MIKATA": "Ally_",  # prefix that identifies hero as a playable alt of a NPC
                    "BON": "HoshidanSummer_",  # prefix that identifies hero as a Hoshidan Summer alt
                    "NEWYEAR": "NewYears_",  # prefix that identifies hero as a New Years alt
                    "KAKUSEI": "Awakening_",  # prefix that identifies hero as an Awakening alt (only Anna so far)
                    "ECHOES": "Echoes_",  # prefix that identifies hero as an Echoes alt (only Catria so far)
                    "BEFORE": "Young_",  # prefix that identifies hero as a young alt
                }

                prefix = ""
                for identifier in prefix_dict:
                    if identifier in unit_identifiers:
                        prefix += prefix_dict[identifier]

                translated_name = "PID_" + prefix + translated_name + suffix

                if translated_name not in my_dict:
                    if output_as_class:
                        my_dict[translated_name] = output_class.from_dict(input_dict=idict)
                    else:
                        my_dict[translated_name] = idict
                else:
                    if output_as_class:
                        # creates new entry that includes id_num in key for old entry
                        my_dict["PID_" + str(my_dict[translated_name].id_num).replace(" ", "")
                                + "_" + str(translated_name).replace("PID_", "")] = my_dict[translated_name]

                        # creates new entry that includes id_num in key for duplicate entry
                        my_dict["PID_" + str(idict["id_num"]).replace(" ", "") + "_" +
                                str(translated_name).replace("PID_", "")] = output_class.from_dict(input_dict=idict)
                    else:
                        # creates new entry that includes id_num in key for old entry
                        my_dict["PID_" + str(my_dict[translated_name]["id_num"])
                            .replace(" ", "") + "_" + str(translated_name).replace("PID_", "")] \
                            = my_dict[translated_name]

                        # creates new entry that includes id_num in key for duplicate entry
                        my_dict["PID_" + str(idict["id_num"]).replace(" ", "") + "_" +
                                str(translated_name).replace("PID_", "")] = idict

                    # deletes old entry without id_num in name
                    del my_dict[translated_name]


            if output_class == enemy_class:
                translated_name = translate_jp_to_en_dict(idict, english_data, prefix="MEID", old_prefix="EID")

                if output_as_class:
                    my_dict[translated_name] = output_class.from_dict(input_dict=idict)
                else:
                    my_dict[translated_name] = idict

            if output_class == skill_class:
                translate_output = translate_jp_to_en_dict(idict, english_data=english_data, is_skill=True)
                if translate_output is not None:
                    if output_as_class:
                        my_dict[translate_output] = output_class.from_dict(input_dict=idict)
                    else:
                        my_dict[translate_output] = idict
            if output_as_class:
                my_dict2[idict["id_tag"]] = output_class.from_dict(input_dict=idict)
            else:
                my_dict2[idict["id_tag"]] = idict
        dprint("\n")
        return my_dict, my_dict2

    def process_data(data_loc, output, output_class):
        total_entries = int()

        if output_class is not None:
            output_name = str(output_class.__name__)
        else:
            output_name = "\b"
            pass

        single_file = False
        try:
            for file in os.listdir(data_loc):
                dprint("Processing:", file)
                with open(data_loc + "/" + file, "r", encoding="utf-8") as json_data:
                    # FIXME: change to output.update()
                    # But why though? What do you know that I don't, past me?
                    output[file.replace(".json", "")] = json.load(json_data)
                    dprint(len(output[file.replace(".json", "")]), output_name, "entries found")
                    total_entries += len(output[file.replace(".json", "")])
        except NotADirectoryError:
            single_file = True
            dprint("Processing:", data_loc)
            with open(data_loc, "r", encoding="utf-8") as json_data:
                output = json.load(json_data)
                dprint(len(output), output_name, "entries found")
                total_entries += len(output)

        if output_class:
            dprint("Total:", total_entries, "entries for", output_name)
        else:
            dprint("Total:", total_entries, "entries")
        dprint("\n")

        if output_class:
            if not single_file:
                # dictionary to list of dictionary's values
                dict_values_list = []
                for key in output:
                    dict_values_list.extend(output[key])
            else:
                dict_values_list = output

            output = my_merger2(dict_values_list, output_class)
        return output

    os.chdir(r"C:\Users\admin\PycharmProjects\FireEmblemClone\HertzDevil_JSON_assets\Common\SRPG")
    dprint(os.listdir())
    # dictionary of json files converted to dicts
    # keys are json file names strings, values are lists of dictionaries which contain FEH skills
    skills = {}
    players = {}
    enemies = {}
    weapons = {}
    growth = {}
    move = {}
    stage_encount = {}
    terrain = {}

    # maybe do something like:
    # for k, v in [_ for _ in locals().items()]:
    #   if k:
    #       var = process_data(parse k for string here, list here, and class here

    if get_skills:
        skills = process_data("Skill", skills, skill_class)

    if get_characters:
        players = process_data("Person", players, player_class)

        # ===========================================

        enemies = process_data("Enemy", enemies, enemy_class)

    if get_weapons:
        weapons = process_data("Weapon.json", weapons, weapon_class)

    if get_growth:
        growth = process_data("Grow.json", growth, None)

    if get_move:
        move = process_data("Move.json", move, None)

    if get_stage_encount:
        stage_encount = process_data("StageEncount.json", stage_encount, None)

    if get_terrain:
        terrain = process_data("Terrain.json", terrain, None)

    stop = time()
    print("Time elapsed:", stop - start, "secs")
    return skills, players, enemies, weapons, english_data, growth, move, stage_encount, terrain



from FireEmblemCombatV2 import Player
# FIXME: Running this script as a standalone breaks everything
skills_output, players_output, enemies_output, weapons_output, english_data_output, growth_output, \
    move_output, stage_encount_output, terrain_output = load_files(None, Player, None, None, output_as_class=False)

print(len(players_output))

for xitem in players_output[1]:
    item_in_english = False
    for yitem in players_output[0]:
        if players_output[0][yitem]["id_tag"] == xitem:
            item_in_english = True
    if item_in_english == False:
        print(xitem)

# if __name__ == "__main__":
#     from FireEmblemCombatV2 import Skill, Weapon, Enemy, Player
#
#     skills_output, players_output, enemies_output, weapons_output, english_data_output, growth_output, \
#         move_output, stage_encount_output, terrain_output = load_files(Skill, Player, Enemy, Weapon)
#
#     print(players_output[0]["MARTH"].skills)

# CONCLUSION: some things, like Falchion, get overridden, others cannot be translated by current translation method
# List: 3515, Set: 3400 --> 3400 translated normally; 96 untranslated, set as None; 11 overridden Falchion items;
# 7 Umbra Burst? Also 1 Missiletainn, but I think that's because the game has 2 separate Missiletainn weapons,
# those being the sword (used by Owain) and the tome (used by Ophelia), so that one doesn't count

# pprint([i for i in skills])
# print(len(skills["00_first"]))
# for i in skills["00_first"]:
#     print("")
#     print(i)
#     for j in i:
#         try:
#             print(j, ":", i[j])
#         except TypeError as e:
#             # print(e)
#             pass
#     print("")
# pprint([i for i in characters])
# pprint([i for i in weapons])
