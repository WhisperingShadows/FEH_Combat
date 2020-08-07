from FireEmblemLoadJsonFilesBetterV2 import load_files
from pprint import pprint
from FEH_definitions import STAT_dict
from math import trunc
from math import floor
from ZanyLuaOpShenanigans.LuaBase import *
from ZanyLuaOpShenanigans.LuaListUtil import *

DEBUG = False

# growth_data contains a list of growth vectors in decimal format
skills_data, players_data, enemies_data, weapons_data, english_data, growth_data, move_data, stage_encount_data, \
terrain_data = load_files(None, None, None, None, False, False, False, False, False, True, False, False, False)

StatOffset = {"hp": -35, "atk": -28, "spd": -21, "def": -14, "res": -7}


# TODO: expand to work on kwargs, fix co_argcount for args also counting kwargs
def accepts_input(*types):
    def check_accepts(f):
        new_types = list(types)
        if len(types) != f.__code__.co_argcount:
            new_types.extend(["any" for _ in range(f.__code__.co_argcount - len(types))])

        def new_f(*args, **kwds):
            new_args = list(args)
            for i, (a, t) in enumerate(zip(args, new_types)):
                if t != "any" and t != Any:
                    try:
                        assert isinstance(a, t), \
                            "Arg %r does not match %s in function %s" % (a, t, f.__code__.co_name)
                    except AssertionError as e:
                        print(e)
                        print("Attempting to convert input type")
                        try:
                            new_args[i] = t(a)
                        except ValueError:
                            print("Failed to convert")
                            raise Exception
                        print("Successfully converted:", new_args[i])
            return f(*new_args, **kwds)

        new_f.__name__ = f.__name__
        return new_f

    return check_accepts


# def accepts(*types):
#     def check_accepts(f):
#         assert len(types) == f.__code__.co_argcount
#         def new_f(*args, **kwds):
#             for (a, t) in zip(args, types):
#                 assert isinstance(a, t), \
#                        "arg %r does not match %s" % (a,t)
#             return f(*args, **kwds)
#         new_f.__name__ = f.__name__
#         return new_f
#     return check_accepts

# applied growth rate
@accepts_input(int, int)
def get_applied_growth_rate(rarity, rate):
    return trunc(rate * (0.79 + 0.07 * rarity))


@accepts_input(int, int)
def get_growth_value(rarity, rate):
    return trunc(0.39 * get_applied_growth_rate(rarity, rate))


# checks for super asset/flaw
@accepts_input(int, int)
def get_super_growth(rarity, rate):
    neutral = get_growth_value(rarity, rate)
    if get_growth_value(rarity, rate + 5) > neutral + 2:
        return 1
    elif get_growth_value(rarity, rate - 5) < neutral - 2:
        return -1
    return 0


# lua for do loop function takes arg1 and arg2 as start and endpoint and arg3 (optional) as step
# lua range includes both ends, python does not     # fixed it
# list indices start at 1 (bruh what)
@accepts_input(int, int)
def find_growth_rate(rarity, growth):
    for rate in range(0, 210 + 5, 5):
        if get_growth_value(rarity, rate) == growth:
            return rate, False
    for rate in range(210, 0, -1):
        if get_growth_value(rarity, rate) == growth:
            return rate, True


@accepts_input(LuaList)
def get_rarity_bonuses(five_star_lv1_stats):
    var = arrayOrder(sub(five_star_lv1_stats, 2, 5))
    print("Order before unpack:", var)
    order = var.insert_at_beginning(0)
    print("Order after insert:", order)
    order = unpack(var)
    print("Order after unpack:", order)
    return generate(5, lambda rarity: map_i(lambda o: 2 - floor((5 - rarity + (o < 2 and 1 or 0)) / 2), order))


# generate(5, lambda rarity: map_i(lambda o: 2 - floor((5 - rarity + (o < 2 and 1 or 0)) / 2), order))
#
# generate(5, lambdaOne)
#
# def lambdaOne(rarity):
#     return map_i(lambdaTwo, order)
#
# def lambdaTwo(o):
#     return 2 - floor((5 - rarity + (o < 2 and 1 or 0)) / 2)

def convert_lv1_3star_stats_to_5star(stats):
    if isinstance(stats, int):
        return stats + 1
        pass
    else:
        if len(stats) != 5:
            raise Exception("Invalid number of stats supplied, should be 5")
        else:
            new_stats = []
            for stat in stats:
                stat += 1
                new_stats.append(stat)
            return new_stats


@accepts_input(LuaList)
def full_lv1_stats(five_star_lv1_stats):
    var = arrayOrder(sub(five_star_lv1_stats, 2, 5))
    print("Order before unpack:", var)
    order = var.insert_at_beginning(0)
    print("Order after insert:", order)
    order = unpack(var)
    print("Order after unpack:", order)

    # order = unpack(arrayOrder(sub(fiveStarLv1Stats, 2, 5)))
    return generate(5, lambda rarity: zip_op(five_star_lv1_stats, order,
                                             lambda b, o: b - floor((5 - rarity + (o < 2 and 1 or 0)) / 2)))


@accepts_input(LuaList)
def full_lv40_stats(rate_set, full_1_stat_set):
    return map_i(
        lambda stat_set, rarity: zip_op(stat_set, rate_set, lambda base, rate: base + get_growth_value(rarity, rate)),
        full_1_stat_set)


# # BVID is a byte in the Hero's files; it's stored under the "base_vector_id" tag for each character
# GrowthVectorID = ((3*5StarLevel1NeutralBaseStat)+StatOffset+AppliedGrowthRate+BVID) % 64
#
# GrowthValue = trunc((NewLevel - OldLevel) * AppliedGrowthRatePercent)
#
# Assets/Flaws increase/decrease the base stats by 1 AND increase/decrease the growth values by 5%


# not used for playable units at any level other than 40 where randomized stats converge
# mostly used for tempest trials, training tower, chain challenges, etc.
def general_levelup(new_level, old_level, applied_growth_rate):
    # returns growth value
    return trunc((new_level - old_level) * (applied_growth_rate * 0.01))


def get_growth_vector_id(five_star_lv1_neutral_base_stat, offset, applied_growth_rate, bvid):
    if isinstance(offset, int):
        num_offset = offset
    elif isinstance(offset, str):
        if offset in StatOffset:
            num_offset = StatOffset[offset]
        else:
            print("Invalid stat key supplied")
            raise KeyError
    else:
        print("Invalid offset supplied")
        raise TypeError

    return ((3 * five_star_lv1_neutral_base_stat) + num_offset + applied_growth_rate + bvid) % 64


def get_growth_vector(growth_value, growth_vector_id):
    # print(format(growth_data[growth_value][growth_vector_ID], "0b")[::-1][1:], "Formated Ver")
    # print(bin(growth_data[growth_value][growth_vector_ID])[::-1][1:].replace("b0", ""), "Bin ver 1")
    # print(bin(growth_data[growth_value][growth_vector_ID])[1:-1][::-1], "Bin ver 2") # still has b at the end
    bin_string = format(growth_data[growth_value][growth_vector_id], "0b")[::-1][1:]
    output = bin_string + "0" * (40 - len(bin_string))
    return output


def test_growth_vector(growth_vector, base, lv40):
    # print(growth_vector)
    # print(list(growth_vector).count("1"))
    return base + list(growth_vector).count("1") == lv40


# vec_id = get_growth_vector_id(18, -35, get_applied_growth_rate(5, 45), 169)
# print(get_growth_vector(19, vec_id))


def get_stat_increase_for_level(stat, char):
    rarity = char.rarity
    level = char.level
    stats = char.base_stats
    rates = char.growth_rates
    bvid = char.base_vector_id

    rate = rates[stat]
    stat_val = stats[stat] + 1

    applied_growth_rate = get_applied_growth_rate(rarity, rate)

    growth_value = get_growth_value(rarity, rate)

    growth_vector_id = get_growth_vector_id(stat_val, stat, applied_growth_rate, bvid)

    growth_vector = get_growth_vector(growth_value, growth_vector_id)

    print("{0}: {1}".format(stat, growth_vector))

    stat_increase = 0

    for i in range(level):
        stat_increase += int(growth_vector[i])

    return stat_increase


def get_all_stat_increases_for_level(char) -> dict:
    stat_increases = {k: None for k in STAT_dict.values()}

    for stat in STAT_dict.values():
        stat_increases[stat] = get_stat_increase_for_level(stat, char)

    return stat_increases
