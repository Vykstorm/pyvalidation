

import unittest
from unittest import TestCase
from functools import partial
from re import match, fullmatch
from math import floor, ceil

from decorators import parse


class TestParsers(TestCase):
    '''
    Set of tests to check features of decorator parse()
    '''

    def test_empty_parser(self):
        '''
        Tests that when None value is indicated as a parser to process some input value, it just acts like an empty
        parser.
        '''
        @parse(None, None, None)
        def foo(x, y, z):
            self.assertEqual(x, 1)
            self.assertEqual(y, 'Hello World!')
            self.assertEqual(z, 2.3)

        @parse()
        @parse(None)
        @parse(None, None)
        @parse(None, None, None)
        def bar(x, y, z):
            foo(x, y, z)

        bar(1, 'Hello World!', 2.3)


    def test_parsers(self):
        '''
        Tests a few parsers
        :return:
        '''

        @parse(floor, ceil, abs)
        def foo(x, y, z):
            self.assertEqual(x, 1)
            self.assertEqual(y, 2)
            self.assertEqual(z, 3)

        @parse(str, str, str)
        def bar(x, y, z):
            self.assertEqual(''.join([x, y, z]), '123')

        @parse(partial(fullmatch, '<h1>([^<]*)<\/h1>'))
        @parse(lambda r: r.group(1))
        def qux(x):
            self.assertEqual(x, 'Hello World!')


        foo(1.85, 1.85, -3)
        foo(1.5, 1.7, -3)

        bar(1, 2, 3)
        bar('1', '2', '3')

        qux('<h1>Hello World!</h1>')
        with self.assertRaises(Exception):
            qux('')

    def test_parsing_order(self):
        '''
        This checks if parsers are called in the expected order (when chaining decorators)
        :return:
        '''
        @parse(partial(int.__add__, 3))
        @parse(partial(int.__mul__, 7))
        @parse(partial(int.__rfloordiv__, 4))
        def foo(x):
            return x
        # foo(x) = (x+3)*7 // 4

        self.assertEqual(foo(1), 7)
        self.assertEqual(foo(2), 8)
        self.assertEqual(foo(3), 10)

if __name__ == '__main__':
    unittest.main()