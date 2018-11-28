
from validators import Validator


'''
This module defines the base classes for exceptions thrown by this library
'''



class ParsingError(Exception):
    '''
    This error is raised when parsing input/output values of a method
    '''
    def __init__(self, param, description = ''):
        '''
        Initializes this instance..
        :param param: Must be the index of the parameter that was parsed (starting with 0 for the first argument)
        :param description: An optional description of why argument parsing failed
        '''
        if not isinstance(param, int):
            raise TypeError()
        if param < 0:
            raise ValueError()
        if not isinstance(description, str) and description is not None:
            raise TypeError()

        super().__init__()
        self._param = param
        self._description = description if isinstance(description, str) else ''
        self._level = None


    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, x):
        if not isinstance(x, int) and x is not None:
            raise TypeError()

        if isinstance(x, int) and x < 0:
            raise ValueError()
        self._level = x


    def __str__(self):
        param, description, level = self._param, self._description, self._level

        msg = 'Error parsing argument at position {}{}'.format(
            param+1,
            ': {}'.format(description) if description else '')
        if level is not None:
            msg += ' (at level {})'.format(level+1)
        return msg

class ValidationError(ParsingError):
    '''
    This error is raised when validating input/output values of a method
    '''
    def __str__(self):
        param, description, level = self._param, self._description, self._level

        msg = 'Invalid argument at position {}{}'.format(
            param+1,
            ': {}'.format(description) if description else '')
        if level is not None:
            msg += ' (at level {})'.format(level+1)
        return msg