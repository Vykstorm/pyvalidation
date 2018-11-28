

import unittest
from unittest import TestCase

from decorators import validate, parse, FuncWrapper


class TestDecorators(TestCase):
    '''
    This is a set of unitary tests to check if decorators validate() and parse() works properly.
    '''

    def test_static_method(self):
        '''
        Test if decorators can decorate static class methods.
        :return:
        '''
        class Qux:
            @staticmethod
            @validate(int, int, int)
            def bar(x, y, z):
                pass

            @staticmethod
            @parse(str, str, str)
            def foo(x, y, z):
                pass

        Qux.bar(1, 2, 3)
        Qux.foo(1, 2, 3)
        Qux().bar(1, 2, 3)
        Qux().foo(1, 2, 3)

    def test_class_method(self):
        '''
        Test if decorators can decorate class methods.
        :return:
        '''
        class Qux:
            @classmethod
            @validate(object, int, int, float)
            def foo(cls, x, y, z):
                self.assertIs(cls, Qux)

            @classmethod
            @parse(None, float, float, float)
            def bar(cls, x, y, z):
                self.assertIs(cls, Qux)

        Qux.foo(1, 2, 3.0)
        Qux.bar(1.0, 2.0, 3.0)
        Qux().foo(1, 2, 3.0)
        Qux().bar(1.0, 2.0, 3.0)

    def test_instance_method(self):
        '''
        Test if decorators can decorate instance methods.
        :return:
        '''
        class Qux:
            @validate(object, int, int, float)
            def foo(obj, x, y, z):
                self.assertIsInstance(obj, Qux)

            @parse(None, float, float, float)
            def bar(obj, x, y, z):
                self.assertIsInstance(obj, Qux)

        Qux().foo(1, 1, 2.0)
        Qux().bar(1, 1, 1)
        Qux.foo(Qux(), 1, 1, 2.0)
        Qux.bar(Qux(), 1, 1, 1)

    def test_function(self):
        '''
        Test if decorators can decorate regular methods.
        :return:
        '''
        @validate(int, int, float)
        def foo(x, y, z):
            pass

        self.assertIsInstance(foo, FuncWrapper)
        foo(1, 1, 1.0)

        @parse(str, str, str)
        def bar(x, y, z):
            pass

        self.assertIsInstance(foo, FuncWrapper)
        bar('Hello', 'my', 'friend')


    def test_chain_decorators(self):
        '''
        Check if decorators can be chained.
        :return:
        '''
        @validate(int, int, int)
        @parse(str, str, str)
        def foo(x, y, z):
            pass

        foo(1, 2, 3)

        @validate(int, int, int)
        @validate(range(0, 20), range(0, 15), [2, 3, 5])
        @parse(str, str, str)
        def bar(x, y, z):
            pass

        bar(1, 2, 3)

        @parse(float, float, float)
        @parse(int, int, int)
        @validate(int, int, int)
        def qux(x, y, z):
            pass

        qux('1.5', '2.3', '7.6')


    def test_introspection(self):
        '''
        Checks if the decorated function can be inspected (it has attributes __qualname__, __name__, __annotations__ and
        __docs__)
        :return:
        '''
        def foo(x, y, z):
            '''
            Test function
            '''
            pass
        bar = validate(int, int, int)(foo)

        self.assertEqual(foo.__qualname__, bar.__qualname__)
        self.assertEqual(foo.__name__, bar.__name__)
        self.assertEqual(foo.__doc__, bar.__doc__)
        self.assertEqual(foo.__annotations__, bar.__annotations__)

        self.assertEqual(str(foo), str(bar))
        self.assertEqual(repr(foo), repr(bar))


    def test_kwargs(self):
        '''
        Test if decorator accepts either positional and keyword argumnents.
        :return:
        '''

        @validate(int, y=str, z=bool)
        def foo(x, y, z):
            pass

        @validate(z=bool, y=str, x=int)
        def bar(x, y, z):
            pass

        @parse(str, y=str, z=str)
        def foo(x, y, z):
            pass

        @parse(z=str, y=str, x=str)
        def bar(x, y, z):
            pass


    def test_default_values(self):
        '''
        Test if a method with default values can be decorated using parse() and validate() decorators
        :return:
        '''

        @validate(bool)
        def foo(x=True):
            pass

        @validate(int, str)
        def foo(x, y=1):
            pass

        @parse(None)
        def bar(x=True):
            pass

        @parse(None, None)
        def bar(x, y=1):
            pass

    def test_return_values(self):
        '''
        Test if the returned values of the wrapped functions are forwarded correctly.
        :return:
        '''

        @validate()
        def foo(x):
            return x

        for x in (1, (1, 2, 3), (1, 2), (1,), [1, 2], [1], frozenset([1, 2, 3]) ):
            self.assertEqual(x, foo(x))

if __name__ == '__main__':
    unittest.main()