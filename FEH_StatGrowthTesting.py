from FEH_StatGrowth import *
import unittest


from forbiddenfruit import curse


def to_lua(self):
    return LuaList(self)


curse(list, "to_lua", to_lua)


class TestMasterGrowthRate(unittest.TestCase):

    # @unittest.skip("Test not needed")
    def test_main(self):
        self.assertEqual(50, get_applied_growth_rate(3, 50))
        self.assertEqual(45, get_applied_growth_rate(3, 45))
        self.assertEqual(55, get_applied_growth_rate(3, 55))

        self.assertEqual(57, get_applied_growth_rate(5, 50))
        self.assertEqual(51, get_applied_growth_rate(5, 45))
        self.assertEqual(62, get_applied_growth_rate(5, 55))

        self.assertEqual(43, get_applied_growth_rate(1, 50))
        self.assertEqual(38, get_applied_growth_rate(1, 45))
        self.assertEqual(47, get_applied_growth_rate(1, 55))


class TestGetGrowthValue(unittest.TestCase):

    # @unittest.skip("Test not needed")
    def test_main(self):
        self.assertEqual(19, get_growth_value(3, 50))
        self.assertEqual(17, get_growth_value(3, 45))
        self.assertEqual(21, get_growth_value(3, 55))

        self.assertEqual(22, get_growth_value(5, 50))
        self.assertEqual(19, get_growth_value(5, 45))
        self.assertEqual(24, get_growth_value(5, 55))


class TestGetSupergrowth(unittest.TestCase):

    # @unittest.skip("Test not needed")
    def test_main(self):
        self.assertEqual(-1, get_super_growth(5, 50))
        self.assertEqual(1, get_super_growth(5, 45))
        self.assertEqual(0, get_super_growth(5, 55))


class TestFindGrowthRate(unittest.TestCase):

    # @unittest.skip("Test not needed")
    def test_main(self):
        self.assertEqual(50, find_growth_rate(3, 19)[0])
        self.assertEqual(45, find_growth_rate(3, 17)[0])
        self.assertEqual(55, find_growth_rate(3, 21)[0])

        self.assertEqual(50, find_growth_rate(5, 22)[0])
        self.assertEqual(45, find_growth_rate(5, 19)[0])
        self.assertEqual(55, find_growth_rate(5, 24)[0])


# print("All tests completed successfully")

class TestGetRarityBonuses(unittest.TestCase):
    # @unittest.skip("Running other tests")
    def test_main(self):
        self.assertEqual([
                             [0, 0, 0, 0, 0],
                             [0, 1, 1, 0, 0],
                             [1, 1, 1, 1, 1],
                             [1, 2, 2, 1, 1],
                             [2, 2, 2, 2, 2],
                         ].to_lua(), get_rarity_bonuses([15, 9, 8, 7, 6]))
        self.assertEqual([
                             [0, 0, 0, 0, 0],
                             [0, 0, 0, 1, 1],
                             [1, 1, 1, 1, 1],
                             [1, 1, 1, 2, 2],
                             [2, 2, 2, 2, 2],
                         ].to_lua(), get_rarity_bonuses([15, 6, 7, 8, 9]))
        self.assertEqual([
                             [0, 0, 0, 0, 0],
                             [0, 1, 1, 0, 0],
                             [1, 1, 1, 1, 1],
                             [1, 2, 2, 1, 1],
                             [2, 2, 2, 2, 2],
                         ].to_lua(), get_rarity_bonuses([15, 9, 9, 9, 9]))
        self.assertEqual([
                             [0, 0, 0, 0, 0],
                             [0, 0, 1, 0, 1],
                             [1, 1, 1, 1, 1],
                             [1, 1, 2, 1, 2],
                             [2, 2, 2, 2, 2],
                         ].to_lua(), get_rarity_bonuses([15, 8, 9, 8, 9]))
        self.assertEqual([
                             [0, 0, 0, 0, 0],
                             [0, 0, 1, 1, 0],
                             [1, 1, 1, 1, 1],
                             [1, 1, 2, 2, 1],
                             [2, 2, 2, 2, 2],
                         ].to_lua(), get_rarity_bonuses([15, 8, 9, 9, 9]))


class TestFullLv1Stats(unittest.TestCase):
    # @unittest.skip("Running other tests")
    def test_main(self):
        self.assertEqual([
                             [13, 7, 6, 5, 4],
                             [13, 8, 7, 5, 4],
                             [14, 8, 7, 6, 5],
                             [14, 9, 8, 6, 5],
                             [15, 9, 8, 7, 6],
                         ].to_lua(), full_lv1_stats([15, 9, 8, 7, 6]))
        self.assertEqual([
                             [13, 4, 5, 6, 7],
                             [13, 4, 5, 7, 8],
                             [14, 5, 6, 7, 8],
                             [14, 5, 6, 8, 9],
                             [15, 6, 7, 8, 9],
                         ].to_lua(), full_lv1_stats([15, 6, 7, 8, 9]))
        self.assertEqual([
                             [13, 7, 7, 7, 7],
                             [13, 8, 8, 7, 7],
                             [14, 8, 8, 8, 8],
                             [14, 9, 9, 8, 8],
                             [15, 9, 9, 9, 9],
                         ].to_lua(), full_lv1_stats([15, 9, 9, 9, 9]))
        self.assertEqual([
                             [13, 6, 7, 6, 7],
                             [13, 6, 8, 6, 8],
                             [14, 7, 8, 7, 8],
                             [14, 7, 9, 7, 9],
                             [15, 8, 9, 8, 9],
                         ].to_lua(), full_lv1_stats([15, 8, 9, 8, 9]))
        self.assertEqual([
                             [13, 6, 7, 7, 7],
                             [13, 6, 8, 8, 7],
                             [14, 7, 8, 8, 8],
                             [14, 7, 9, 9, 8],
                             [15, 8, 9, 9, 9],
                         ].to_lua(), full_lv1_stats([15, 8, 9, 9, 9]))


#unittest.main()

from pprint import pprint
pprint(full_lv40_stats([50, 60, 55, 40, 45], full_lv1_stats([17, 7, 8, 8, 6])))
