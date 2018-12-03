
'''
This module provides helper routines for the rest of the modules in this library.
'''

from itertools import islice
from types import FunctionType


def iterable(x):
    '''
    Checks if an object is iterable or not.
    An object is iterable if it defines the method __iter__
    :param x: Is the object to check if its iterable.
    :return: Returns True if x is iterable, False otherwise.
    '''
    try:
        iter(x)
        return True
    except:
        pass
    return False



def format_range(x):
    '''
    Stringifies a range object for pretty printing in error messages.
    :param x: Is an object of class range
    :return:
    '''
    if not isinstance(x, range):
        raise TypeError()

    if len(x) < 5:
        return str(list(x))
    return '[{}]'.format(', '.join(map(str, tuple(x[:2]) + ('...',) + tuple(x[-2:]))))

def format_sequence(x):
    '''
    Stringifies an iterable object for pretty printing in error messages.
    :return:
    '''
    if not iterable(x):
        raise TypeError()

    if len(x) < 6:
        return str(list(x))
    return '[{}]'.format(', '.join(map(str, tuple(islice(x, 0, 6)) + ('...',))))


def islambda(x):
    '''
    Check if an object is a lambda function.
    :param x:
    :return:
    '''
    return isinstance(x, FunctionType) and x.__name__ == '<lambda>'