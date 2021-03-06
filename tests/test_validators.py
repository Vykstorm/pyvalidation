from unittest import TestCase
import re
from functools import partial
from itertools import chain
from decimal import Decimal
from enum import Enum, auto
from math import floor, sqrt

from src.decorators import validate

from src.validators import TypeValidator, UserValidator
from src.validators import matchregex, fullmatchregex, number
from src.validators import Int, Float, Bool, Complex, Str, List, Tuple, Set, FrozenSet, Dict
from src.validators import array

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


        @validate(Int, Float, Bool, Str, Complex)
        def bar(x, y, z, w, q):
            self.assertIsInstance(x, int)
            self.assertIsInstance(y, float)
            self.assertIsInstance(z, bool)
            self.assertIsInstance(w, str)
            self.assertIsInstance(q, complex)

        bar(1, 1.0, True, 'Hello World!', complex(1))

        @validate(List, Tuple, Set, FrozenSet, Dict)
        def bar(x, y, z, w, q):
            self.assertIsInstance(x, list)
            self.assertIsInstance(y, tuple)
            self.assertIsInstance(z, set)
            self.assertIsInstance(w, frozenset)
            self.assertIsInstance(q, dict)

        bar([], (), set(), frozenset(), {})


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


        # Test disjunctive validators

        @validate(Int | Float)
        def bar(x):
            self.assertIsInstance(x, (int, float))

        bar(1)
        bar(1.0)
        with self.assertRaises(Exception):
            bar(True)

        # Test conjunctive validators

        @validate(Int & UserValidator(lambda x: x % 2 == 0))
        def baz(x):
            self.assertIsInstance(x, int)
            self.assertTrue(x % 2 == 0)

        baz(0)
        baz(2)
        with self.assertRaises(Exception):
            baz('Hello World')
        with self.assertRaises(Exception):
            baz(1)


        # Test xor validators

        @validate(UserValidator(lambda x: floor(sqrt(x))**2 == x) ^ UserValidator(lambda x: x % 2 == 0))
        def foo(x):
            self.assertTrue((floor(sqrt(x)) ** 2 == x) ^ (x % 2 == 0))

        foo(9)
        foo(10)
        with self.assertRaises(Exception):
            foo(4)
        with self.assertRaises(Exception):
            foo(11)

        # Test inverted validators

        @validate(~Str)
        def qux(x):
            self.assertNotIsInstance(x, str)

        qux(1.0)
        with self.assertRaises(Exception):
            qux('Hello World')


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


        # Test if expressions can be composed with regular validators using bitwise operators

        @validate(Int & (arg > 0))
        def foo(x):
            self.assertIsInstance(x, int)
            self.assertGreater(x, 0)

        foo(1)
        with self.assertRaises(Exception):
            foo('Hello world!')

        with self.assertRaises(Exception):
            foo(0)


        @validate((Int & (arg > 0)) ^ (Float & (arg < 0)))
        def bar(x):
            self.assertTrue((isinstance(x, int) and x > 0) ^ (isinstance(x, float) and x < 0))

        bar(1)
        bar(-1.0)

        with self.assertRaises(Exception):
            bar(-1)
        with self.assertRaises(Exception):
            bar(1.0)
        with self.assertRaises(Exception):
            bar('Hello world')


        @validate(Int | (Float & (arg > 0)))
        def qux(x):
            self.assertTrue(isinstance(x, int) or (isinstance(x, float) and x > 0))

        qux(-1)
        qux(1)
        qux(1.0)

        with self.assertRaises(Exception):
            qux(-1.0)
        with self.assertRaises(Exception):
            qux('Hello world!')


    def test_ndarray_validators(self):
        '''
        Test array built-in validator to check numpy ndaray objects.
        This test will only be executed if numpy module is avaliable.
        :return:
        '''

        try:
            import numpy as np
        except:
            return


        @validate(array)
        def foo(x):
            self.assertIsInstance(x, np.ndarray)

        foo(np.array([]))
        with self.assertRaises(Exception):
            foo([])

        # Test array validator with filters

        @validate(array(dtype=np.uint8))
        def foo(x):
            self.assertEqual(x.dtype, np.uint8)

        foo(np.array([], dtype=np.uint8))
        with self.assertRaises(Exception):
            foo(np.array([], dtype=np.float64))


        @validate(array(ndim=1), array(size=4))
        def bar(x, y):
            self.assertEqual(x.ndim, 1)
            self.assertEqual(y.size, 4)

        bar(np.array([1,2,3]), np.ones([2,2]))
        with self.assertRaises(Exception):
            bar(np.ones([2,2]))
        with self.assertRaises(Exception):
            bar(np.array([]), np.ones([3,3]))


        @validate(array(ndim=2, size=9))
        def qux(x):
            self.assertEqual(x.ndim, 2)
            self.assertEqual(x.size, 9)

        qux(np.zeros([3,3]))
        with self.assertRaises(Exception):
            qux(np.zeros([4,4]))


        @validate(array(shape=(3,3)))
        def baz(x):
            self.assertEqual(x.shape, (3,3))

        baz(np.ones([3,3]))
        with self.assertRaises(Exception):
             baz(np.zeros([4,2]))