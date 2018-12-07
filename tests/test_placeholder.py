


import unittest
from unittest import TestCase
from src.operations import arg
from src.decorators import validate, parse


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


    def test_validators(self):
        '''
        Expressions built with the placeholder argument can be used as validators.
        '''
        @validate(arg)
        def foo(x):
            self.assertTrue(x)

        foo(1)
        foo(True)
        foo(1.0)
        with self.assertRaises(Exception):
            foo(False)
        with self.assertRaises(Exception):
            foo(0)



        @validate(arg > 0)
        def bar(x):
            self.assertGreater(x, 0)

        bar(1)
        bar(1.0)
        with self.assertRaises(Exception):
            bar(0)
        with self.assertRaises(Exception):
            bar(-1.0)


        @validate((arg >= 0) & (arg < 10))
        def qux(x):
            self.assertIn(x, range(0, 10))

        qux(0)
        qux(4)
        qux(9)
        with self.assertRaises(Exception):
            qux(10)
        with self.assertRaises(Exception):
            qux(-1)


        @validate(((arg**2) % 2) == 0)
        def baz(x):
            pass

        baz(2)
        baz(4)
        baz(6)
        with self.assertRaises(Exception):
            baz(3)


    def test_parsers(self):
        '''
        Expressions built with the placeholder argument can be used as parsers
        '''

        @parse(arg)
        def foo(x):
            return x

        self.assertEqual(foo(1), 1)
        self.assertEqual(foo('Hello World!'), 'Hello World!')


        @parse((arg + 1) ** 2)
        def bar(x):
            return x
        self.assertEqual(bar(1), 4)
        self.assertEqual(bar(2), 9)



if __name__ == '__main__':
    unittest.main()