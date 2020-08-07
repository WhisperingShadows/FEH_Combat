import json
import os
from pprint import pprint
from time import time


DEBUG = False
from dprint import dprint

def translate_jp_to_en_dict(input_dict, english_data,tag="id_tag", prefix="MSID_", old_prefix="SID_", is_skill=False):
    # this was the result of like 4 days with no sleep, constantly coding, I have no idea how it works
    if is_skill:
        output = None
        try:
            if input_dict["refined"]:
                output = str(translate_jp_to_en_dict(input_dict, english_data,tag="refine_base")) + "_" + (
                    input_dict["id_tag"].split("_")[-1])
            else:
                try:
                    output = translate_jp_to_en_dict(input_dict, english_data)

                except KeyError as e:
                    #dprint("\n")

                    if input_dict["beast_effect_id"] is not None and input_dict["category"] == 8:
                        output = translate_jp_to_en_dict(input_dict, english_data,prefix="MSID_H_")
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
                        output = translate_jp_to_en_dict(input_dict, english_data,prefix="MSID_H_")
                    # dprint("\n Yo")
                    pass

            return output

        except KeyError as e:
            print("Error:", e)
        pass
    else:
        return english_data[input_dict[tag].replace(old_prefix, prefix)]
    raise Exception("How did you get here")

def translate_jp_to_en_class(input_class, english_data, attribute="id_tag", prefix="MSID_", old_prefix="SID_", is_skill=False):
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

                except KeyError as e:
                    dprint("\n")

                    if getattr(input_class, "beast_effect_id") is not None and getattr(input_class, "category") == 8:
                        output = translate_jp_to_en_class(input_class, english_data, prefix="MSID_H_")
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


def load_files(Skill, Player, Enemy, Weapon, output_as_class = True, get_english_data=True, get_skills=True, get_characters=True, get_weapons=True, get_growth = True, get_move = True, get_stage_encount = True, get_terrain = True):
    # print("Starting")
    start = time()

    english_data = {}

    if get_english_data:
        os.chdir(r"C:\Users\admin\PycharmProjects\FireEmblemClone\Resources\data\assets\USEN\Message\Data")

        total = int()
        for file in os.listdir():
            dprint("Processing:", file)
            with open(file, "r", encoding="utf-8") as json_data:
                english_data[file.replace(".json", "")] = json.load(json_data)
                dprint(len(english_data[file.replace(".json", "")]))
                total += len(english_data[file.replace(".json", "")])
        dprint("Total:", total)

        myList = []
        for key in english_data:
            myList.extend(english_data[key])

        english_data = my_merger(myList)

    def my_merger2(list_of_dicts, output_class):
        my_dict = {}
        my_dict2 = {}
        for idict in list_of_dicts:

            if idict["id_tag"] == "PID_無し" or idict["id_tag"] == "EID_無し":
                # maybe insert something that just uses these as blanks?
                continue

            if output_class == Player or output_class == Enemy:
                if output_as_class:
                    my_dict[idict["roman"]] = output_class.from_dict(input_dict=idict)
                else:
                    my_dict[idict["roman"]] = idict
            if output_class == Skill:
                translate_output = translate_jp_to_en_dict(idict, english_data=english_data, is_skill=True)
                if translate_output != None:
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
        total = int()
        output_name = str(output_class.__name__) if output_class else "\b"
        single_file = False
        try:
            for file in os.listdir(data_loc):
                dprint("Processing:", file)
                with open(data_loc + "/" + file, "r", encoding="utf-8") as json_data:
                    # FIXME: change to output.update()
                    output[file.replace(".json", "")] = json.load(json_data)
                    dprint(len(output[file.replace(".json", "")]), output_name, "entries found")
                    total += len(output[file.replace(".json", "")])
        except NotADirectoryError:
            single_file = True
            dprint("Processing:", data_loc)
            with open(data_loc, "r", encoding="utf-8") as json_data:
                output = json.load(json_data)
                dprint(len(output), output_name, "entries found")
                total += len(output)

        if output_class:
            dprint("Total:", total, "entries for", output_name)
        else:
            dprint("Total:", total, "entries")
        dprint("\n")

        if output_class:
            if not single_file:
                # dictionary to list of dictionary's values
                myList = []
                for key in output:
                    myList.extend(output[key])
            else:
                myList = output

            output = my_merger2(myList, output_class)
        return output

    os.chdir(r"C:\Users\admin\PycharmProjects\FireEmblemClone\Resources\data\assets\Common\SRPG")
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
        skills = process_data("Skill", skills, Skill)

    if get_characters:
        players = process_data("Person", players, Player)

        # ===========================================

        enemies = process_data("Enemy", enemies, Enemy)

    if get_weapons:
        weapons = process_data("Weapon.json", weapons, Weapon)

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


if __name__ == "__main__":
    from FireEmblemCombatV2 import Skill, Weapon, Enemy, Player
    skills, players, enemies, weapons, english_data, growth, move, stage_encount, terrain = load_files(Skill, Player, Enemy, Weapon)

    print(players[0]["MARTH"].skills)

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
