from ZanyLuaOpShenanigans.LuaBase import LuaList

from typing import Union, Any
from types import FunctionType, LambdaType
from pprint import pprint

FuncOrLamb = Any

def accepts_input(*types):
    def check_accepts(f):
        new_types = list(types)
        if len(types) != f.__code__.co_argcount:
            new_types.extend(["any" for i in range(f.__code__.co_argcount - len(types))])

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


def accepts_output(out_type: type):
    def check_accepts(f):

        def new_f(*args, **kwds):
            out_arg = f(*args, **kwds)
            print("Out_arg:", out_arg)

            try:
                assert isinstance(out_arg, out_type), \
                       "Output arg %r does not match %s in function %s" % (out_arg, out_type, f.__code__.co_name)
            except AssertionError:
                print("Attempting to convert output type")
                try:
                    out_arg = out_type(out_arg)
                except ValueError:
                    print("Failed to convert")
                    raise Exception
                    pass
                print("Successfully converted:", out_arg)
            return out_arg
        new_f.__name__ = f.__name__
        return new_f
    return check_accepts

@accepts_input(LuaList, FuncOrLamb)
def count_if(t: LuaList, pr: FuncOrLamb) -> int:
    print("Count_if in:", t)
    z = 0
    for i in range(1, len(t) + 1):
        if pr(t[i], i):
            z = z + 1
    # z = LuaList(z)
    print("Count_if out:", z)
    return z

@accepts_input(FuncOrLamb, LuaList)
def map_i(f: FuncOrLamb, t: LuaList) -> LuaList:
    print("Map in:", f.__name__, ",", t)
    z = {}

    if f.__code__.co_argcount == 1:
        for i in range(1, len(t) + 1):
            print("Attempting", i)
            z[i] = f(t[i])
    elif f.__code__.co_argcount == 2:
        for i in range(1, len(t) + 1):
            z[i] = f(t[i], i)
    else:
        print("Too many arguements")
        raise Exception
    z = LuaList(z)
    print("Map out:", z)
    return z


@accepts_input(LuaList)
def arrayOrder(arr: LuaList) -> LuaList:
    print("Array order in:", arr)

    # map_i(lambdaOne(arg), arr)
    #
    # for each element of arr, lambdaOne(element), and return list of function returns
    #
    # def lambdaOne(lhs, i):
    #     lhs = arg[1]
    #     i = arg[0]
    #     return count_if(arr, lambdaTwo)
    #
    # def lambdaTwo(rhs, j):
    #     return (i < j and lhs >= rhs) or (i > j and lhs > rhs)
    #
    #
    #

    var = map_i(lambda lhs, i: count_if(arr, lambda rhs, j: (i < j and lhs >= rhs) or (i > j and lhs > rhs)), arr)
    var = LuaList(var)
    print("Array order out:", var)
    return var


# includes both ends, used in FEH_StatGrowth for removing HP stat as it cannot have an asset or flaw
def sub(t: LuaList, i: int, j: int) -> LuaList:
    print("Sub in:", t, "from", i, "to", j)
    j = j or len(t)
    if i < 0:
        i = i + len(t) + 1
    if j < 0:
        j = j + len(t) + 1
    z = []
    for k in range(i, j + 1):
        z.append(t[k])
    # z = LuaList(z)
    z = LuaList(z)
    print("Sub out:", z)
    return z


def generate(n: int, f: FuncOrLamb) -> LuaList:
    print("Generate in", n, ",",  f.__name__, )
    z = []
    for i in range(1, n+1):
        z.append(f(i))
    z = LuaList(z)
    print("Generate out:")
    pprint(z)
    return z


def zip_op(t1: LuaList, t2: LuaList, op: FuncOrLamb) -> LuaList:
    print("Zip_op in:", t1, t2, op.__name__)
    z = []
    for i in range(1, len(t1) + 1):
        z.append(op(t1[i], t2[i]))
    z = LuaList(z)
    print("Zip_op out:", z)
    return z
