from typing import Union, Dict


def unpack(list):
    return list if isinstance(list, LuaList) else LuaList(list)


def pairs(t):
    return t.items()


class assertEqualsException(Exception):
    pass


def genLuaList(L):
    z = {}
    index = 0
    for i in L:
        z[index + 1] = i
        index += 1
    return z
    pass


# depth = lambda L: isinstance(L, list) and len(L) != 0 and max(map(depth, L)) + 1


def luaListRecursive(L: list, d: int = 0) -> Union[list, Dict[int, dict]]:
    if not isinstance(L, list):
        return L
    z = {}
    for i in range(len(L)):
        z[i + 1] = luaListRecursive(L[i])
    return z
    pass


def recursivePrint(D, i=0):
    for k, v in D.items():
        if isinstance(v, dict):
            print(i * "\t", k, ":")
            i += 1
            recursivePrint(v, i)
            i -= 1
        else:
            print(i * "\t", k, ":", v)
    pass



# TODO: Add other dictionary init methods
# dict(**kwarg)
# dict(mapping, **kwarg)
# dict(iterable, **kwarg)
class LuaList(dict):
    def __init__(self, *args, **kwargs):
        super().__init__()

        if kwargs:
            self.update(kwargs)

        else:
            if len(args) == 1:

                if isinstance(args[0], list):
                    self.clear()
                    self.update(luaListRecursive(args[0]))
                    pass
                elif isinstance(args[0], dict):
                    self.update(args[0])
                elif isinstance(args[0], int):
                    self.update(luaListRecursive([args[0]]))
                    pass
                else:
                    print("Boi the hell am I supposed to do with this")
                    raise Exception
            else:
                print("Too many args bud, I can't work with this")
                raise Exception

    def __lt__(self, other):
        to_compare = next(iter(self.values()))
        if isinstance(other, int):
            if to_compare < other:
                return 1
            else:
                return 0

    def __iter__(self):
        yield from self.items()


    def insert_at_beginning(self, arg):
        keys = [i for i in self.keys()]
        values = [i for i in self.values()]
        for i, key in enumerate(keys):
            self[key+1] = values[i]
        self[1] = arg
        print("Inserted", arg, "at index 1")
        print("New list is", self)
        return self


# and not L.count([]) == len(L)
# def assertEquals(in1, in2):
#     try:
#         assert in1 == in2
#     except AssertionError as e:
#         raise assertEqualsException(str(in1)+" does not equal "+str(in2))
