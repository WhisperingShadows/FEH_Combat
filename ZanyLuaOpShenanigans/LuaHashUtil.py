from ZanyLuaOpShenanigans.LuaBase import *

def invert(t):
    z = {}
    for k, v in pairs(t):
        z[v] = k
    return z
