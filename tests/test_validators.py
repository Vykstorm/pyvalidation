from unittest import TestCase
import re
from functools import partial
from itertools import chain
from decimal import Decimal
from enum import Enum, auto


from src.decorators import validate
from src.validators import TypeValidator
from src.validators import matchregex, fullmatchregex, number
from src.exceptions import ValidationError
from src.operations import arg


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

        @validate(partial(re.fullmatch, '\¿.+\?'))
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


    def test_kwargs(self):
        '''
        validate() decorator can accept positional and keyword arguments. This test checks if arguments are validated if
        validators are specified as keyword arguments.
        '''
        @validate(int, int, z=range(0, 20))
        def foo(x, y, z):
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, int)
            self.assertIn(z, range(0, 20))

        foo(30, 30, 10)
        with self.assertRaises(Exception):
            foo(30, 30, 30)

        @validate(z=int, y=float, x=str)
        def bar(x, y, z):
            self.assertIsInstance(x, str)
            self.assertIsInstance(y, float)
            self.assertIsInstance(z, int)

        bar('Hello World!', 1.0, 1)
        with self.assertRaises(Exception):
            bar(1, 1.0, 'Hello World!')


    def test_default_values(self):
        '''
        Argument default values are not validated. This test checks if default values are validated or not.
        :return:
        '''
        @validate(int, int, str)
        def foo(x, y, z=1):
            self.assertTrue(z == 1 or isinstance(z, str))

        foo(1, 1)
        with self.assertRaises(Exception):
            foo(1, 1, 1)



    def test_exceptions(self):
        '''
        All exceptions raised by decorated functions using the decorator validate() are instances of class ValidationError
        :return:
        '''

        @validate(int)
        def foo(x):
            pass

        with self.assertRaises(ValidationError):
            foo(None)



    def test_regex_validators(self):
        '''
        Test the validators matchregex and fullmatchregex
        :return:
        '''

        @validate(matchregex('\d+'))
        def foo(x):
            self.assertIsInstance(x, str)
            self.assertRegex(x, '\d+')

        foo('1234  ')
        with self.assertRaises(Exception):
            foo('  1234')

        with self.assertRaises(Exception):
            foo(False)


        @validate(fullmatchregex('[ ]*[^ ]+[ ]+[^ ]+[ ]*'))
        def bar(x):
            self.assertIsInstance(x, str)
            self.assertRegex(x, '[ ]*[^ ]+[ ]+[^ ]+[ ]*')

        bar(' Hello World! ')
        bar(' Can i? ')

        with self.assertRaises(Exception):
            bar('HelloWorld')
        with self.assertRaises(Exception):
            bar(False)


    def test_number_validators(self):
        '''
        Test numeric builtin validators
        :return:
        '''

        @validate(number)
        def foo(x):
            self.assertIsInstance(x, (int, float, Decimal))

        foo(1)
        foo(2.5)
        foo(Decimal('123'))
        with self.assertRaises(Exception):
            foo('123')

    def test_callable_validators(self):
        '''
        Test callable builtin validator
        '''

        @validate(callable)
        def foo(x):
            pass

        def bar():
            pass

        foo(lambda x: x)
        foo(bar)
        with self.assertRaises(Exception):
            foo(1)


    def test_enum_validators(self):
        '''
        Test that enum classes can be used as type validators
        :return:
        '''
        class Colors(Enum):
            RED = auto()
            BLUE = auto()
            GREEN = auto()

        @validate(Colors)
        def foo(x):
            pass

        foo(Colors.RED)
        foo(Colors.BLUE)
        foo(Colors.GREEN)

        with self.assertRaises(Exception):
            foo(None)



    def test_expressions(self):
        '''
        Expressions built with the placeholder argument feature can be used as validators.
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
