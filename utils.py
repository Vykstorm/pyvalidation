
'''
This module provides helper routines for the rest of the modules in this library.
'''

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