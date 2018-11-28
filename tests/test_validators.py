
import unittest
from unittest import TestCase
from re import match, fullmatch
from functools import partial
from itertools import chain

from decorators import validate, parse
from validators import TypeValidator


class TestValidators(TestCase):
    '''
    Set of tests to check validation features
    '''

    def test_value_validator(self):
        '''
        Check value validators
        :return:
        '''

        @validate((1, 4, 9), ['r', 'w', 'a'])
        def foo(x, y):
            self.assertIn(x, (1, 4, 9))
            self.assertIn(y, ['r', 'w', 'a'])

        foo(1, 'r')
        foo(4, 'w')
        foo(9, 'a')

        with self.assertRaises(Exception):
            foo(None, 't')
        with self.assertRaises(Exception):
            foo(True, 'r')
        with self.assertRaises(Exception):
            foo(4, 's')


    def test_range_validator(self):
        '''
        Check range validators
        :return:
        '''

        @validate(range(0, 10), range(1, 10, 2))
        def foo(x, y):
            self.assertIn(x, range(0, 10))
            self.assertIn(y, range(1, 10, 2))

        for x in range(0, 10):
            for y in range(1, 10, 2):
                foo(x, y)

        with self.assertRaises(Exception):
            foo(11, 10)

        with self.assertRaises(Exception):
            foo(1, 8)

        with self.assertRaises(Exception):
            foo(True, True)


    def test_type_validator(self):
        '''
        Check type validators
        :return:
        '''

        # Test built-in classes as type validators
        @validate(bool, str)
        def foo(x, y):
            self.assertIsInstance(x, bool)
            self.assertIsInstance(y, str)

        foo(True, 'Hello World!')
        with self.assertRaises(Exception):
            foo(None, 'Hello World')
        with self.assertRaises(Exception):
            foo(True, None)

        # Test custom classes as type validators
        class Qux:
            pass

        class Baz(Qux):
            pass

        @validate(Qux, Baz)
        def bar(x, y):
            self.assertIsInstance(x, Qux)
            self.assertIsInstance(y, Baz)

        bar(Qux(), Baz())
        bar(Baz(), Baz())
        with self.assertRaises(Exception):
            bar(False, False)
        with self.assertRaises(Exception):
            bar(None, None)
        with self.assertRaises(Exception):
            bar(Qux, Baz)
        with self.assertRaises(Exception):
            bar(Qux(), Qux())


    def test_user_validators(self):
        '''
        Test user defined validators
        '''
        def odd(x):
            return x % 2 == 1

        def even(x):
            return not odd(x)

        @validate(odd, even)
        def foo(x, y):
            self.assertTrue(odd(x))
            self.assertTrue(even(y))

        foo(1, 2)
        with self.assertRaises(Exception):
            foo(2, 1)

        @validate(partial(fullmatch, '\¿.+\?'))
        def bar(x):
            self.assertRegex(x, '^\¿.+\?$')

        bar('¿How are you?')
        with self.assertRaises(Exception):
            bar('Hello world!')



    def test_composed_validators(self):
        '''
        Test composed validators.
        :return:
        '''

        @validate([str, float, int])
        def foo(x):
            self.assertIsInstance(x, (str, float, int))
        foo('10')
        foo(10)
        foo(10.0)
        with self.assertRaises(Exception):
            foo(True)

        @validate([range(0, 5), [10, 11]])
        def foo(x):
            self.assertIn(x, tuple(chain(range(0, 5), [10, 11])))

        foo(1)
        foo(10)
        with self.assertRaises(Exception):
            foo(12)
        with self.assertRaises(Exception):
            foo(False)


    def test_empty_validator(self):
        '''
        Test empty validators
        :return:
        '''
        @validate()
        @validate(object)
        @validate(object, object)
        @validate(object, object, object)
        def bar(x, y, z):
            pass

        bar(1, True, 'Hello World!')
        bar(None, 3.0, bar)



    def test_explicit_validators(self):
        '''
        Validators are created during the method decoration process, but can also be
        instantiated manually and passed as parameters to the decorator.
        This test checks if manually created decorators are working properly.
        :return:
        '''

        v = TypeValidator([int, str])

        @validate(v, [int, str])
        def foo(x, y):
            self.assertIsInstance(x, (int, str))
            self.assertIsInstance(y, (int, str))

        foo(1, 1)
        foo('Hello World!', 'Bye world!')
        with self.assertRaises(Exception):
            foo(False, 1)
        with self.assertRaises(Exception):
            foo(1, False)