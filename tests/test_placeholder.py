


import unittest
from unittest import TestCase
from src.operations import arg


class TestPlaceholder(TestCase):
    '''
    Set of tests to verify the argument "placeholder" feature.
    '''

    def test_identity(self):
        '''
        Build expressions using the argument placeholder
        :return:
        '''
        expr = arg
        self.assertEqual(expr(1), 1)
        self.assertEqual(expr(True), True)
        self.assertEqual(expr(2.0), 2.0)


    def test_arithmetic_operators(self):
        '''
        Build expressions using the argument placeholder and arithmetic operators
        :return:
        '''
        expr = arg + 2
        self.assertEqual(expr(1), 1+2)

        expr = arg - 2
        self.assertEqual(expr(4), 4-2)

        expr = arg * 2
        self.assertEqual(expr(1), 1*2)

        expr = arg / 2
        self.assertEqual(expr(1), 1/2)

        expr = arg // 2
        self.assertEqual(expr(5), 5//2)

        expr = arg % 2
        self.assertEqual(expr(5), 5%2)

        expr = arg ** 2
        self.assertEqual(expr(2), 2**2)

        expr = -arg
        self.assertEqual(expr(2), -2)

        expr = +arg
        self.assertEqual(expr(-2), +-2)

        expr = abs(arg)
        self.assertEqual(expr(-4), abs(-4))


    def test_bitwise_operators(self):
        '''
        Build expressions using the argument placeholder and bitwise operators
        :return:
        '''
        expr = arg | 4
        self.assertEqual(expr(1), 1|4)

        expr = arg & 5
        self.assertEqual(expr(1), 1&5)

        expr = arg ^ 5
        self.assertEqual(expr(3), 3^5)

        expr = ~arg
        self.assertEqual(expr(7), ~7)

        expr = arg << 2
        self.assertEqual(expr(5), 5<<2)

        expr = arg >> 2
        self.assertEqual(expr(9), 9>>2)


    def test_comparision_operators(self):
        '''
        Build expressions using the argument placeholder and comparision operators
        '''
        expr = arg > 0
        self.assertEqual(expr(1), 1>0)
        self.assertEqual(expr(0), 0>0)
        self.assertEqual(expr(-1), -1>0)

        expr = arg >= 0
        self.assertEqual(expr(1), 1>=0)
        self.assertEqual(expr(0), 0>=0)
        self.assertEqual(expr(-1), -1>=0)

        expr = arg == 0
        self.assertEqual(expr(1), 1==0)
        self.assertEqual(expr(0), 0==0)
        self.assertEqual(expr(-1), -1==0)

        expr = arg < 0
        self.assertEqual(expr(1), 1<0)
        self.assertEqual(expr(0), 0<0)
        self.assertEqual(expr(-1), -1<0)

        expr = arg <= 0
        self.assertEqual(expr(1), 1<=0)
        self.assertEqual(expr(0), 0<=0)
        self.assertEqual(expr(-1), -1<=0)

        expr = arg != 0
        self.assertEqual(expr(1), 1!=0)
        self.assertEqual(expr(0), 0!=0)
        self.assertEqual(expr(-1), -1!=0)




if __name__ == '__main__':
    unittest.main()