
'''
This module defines all kinds of validators that can be used to validate your function arguments.
'''


from utils import iterable
from itertools import islice
from inspect import isclass


class Validator:
    '''
    Base class for all kind of validators
    '''
    def __init__(self):
        pass

    def __call__(self, arg):
        '''
        This method must be implemented by subclasses. It validates the given argument with the validator.
        :param arg: Is the argument to validate.
        :return: True if the given argument is valid or not. False otherwise. When returning False, another value
        can be returned (a string with a brief description that will indicate why the given arg is not valid)
        '''
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__

    @staticmethod
    def from_object(obj):
        if isinstance(obj, Validator):
            return obj
        if type(obj) == object:
            return EmptyValidator()
        return TypeValidator((obj, ))

class TypeValidator(Validator):
    '''
    Validator that check if the given arguments has a proper type.
    '''
    def __init__(self, types, check_subclasses = True, check_bool_subclasses = False):
        '''
        Initializes this instance.
        :param types: Is a list of class objects used for type validation.
        :param check_subclasses: Is a boolean value that indicates how the given argument is checked. If it is True (default value),
        the argument is checked verifying that its type is equal to one of the types specified or a subclass of them.
        This is the default option. Otherwise if its set to False, argument will be validated testing only if its type is the same
        as one of the named classes.
        :param check_bool_type: This has effect only if types includes the 'int' class object and check_subclasses is set to True
        This argument overrides the value of check_subclasses when testing argument type with the bool builin type.
        If its set to True (default Value), boolean values (True and False) are valid numeric values (because bool is a
        subclass of type)
        By default this behaviour is disabled (default value is False)
        '''
        try:
            if not iterable(types):
                raise Exception()
            for cls in types:
                if not isclass(cls):
                    raise Exception()
        except:
            raise TypeError()

        if not isinstance(check_subclasses, bool):
            raise TypeError()
        if not isinstance(check_bool_subclasses, bool):
            raise TypeError()

        super().__init__()

        types = tuple(frozenset(types))
        self.types = tuple(types)
        self.check_subclasses = check_subclasses
        self.check_bool_subclasses = check_bool_subclasses

    def __call__(self, arg):
        cls = type(arg)
        if not self.check_subclasses or (not self.check_bool_subclasses and cls == bool):
            valid = cls in self.types
        else:
            valid = isinstance(arg, self.types)

        if valid:
            return True
        return False, 'Type {} expected but got {}'.format(
            ' or '.join([cls.__name__ for cls in self.types]),
            type(arg).__name__)


class ValueValidator(Validator):
    '''
    This is a validator that checks if the given arguments has a valid value.
    '''
    def __init__(self, values, match_types = True):
        '''
        Initializes this validator.
        :param values: Must be a list of all possible values that the given arguments can take in order to pass the
        validation stage. The operator == is used to check if the argument matches with any value in this list.
        :param match_types: If set to True, the argument must have also the same type as the matched value.
        By default is set to True.
        '''
        super().__init__()
        if not iterable(values):
            raise TypeError()
        self.values = tuple(values)
        self.match_types = match_types

    def __call__(self, arg):
        for value in self.values:
            if arg == value and (not self.match_types or (type(arg) == type(value))):
                return True
        return False, 'Value {} expected but got {}'.format(
            ' or '.join([str(value) for value in self.values]),
            str(arg))


class EmptyValidator(Validator):
    '''
    This is a special validator. Is an "empty" validator because all given arguments will pass
    its validation stage.
    '''
    def __call__(self, arg):
        return True


class RangeValidator(Validator):
    '''
    Validator that checks if the given argument is within a numeric range.
    '''
    def __init__(self, interval, match_types = True):
        '''
        Initializes this instance.
        :param interval: Must be an instance of the built-in class range(). The given argument will pass the validation stage if
        its inside such range (the operator 'in' which uses the method __contains__ is used to check if the argument is contained
        within that range).
        :param match_types: When is set to True, not only the given must be within the range specified, but also need to
        be an int value.
        '''
        if not isinstance(interval, range):
            raise TypeError()
        if not isinstance(match_types, bool):
            raise TypeError()

        super().__init__()
        self.interval = interval
        self.match_types = match_types

    def __call__(self, arg):
        if arg not in self.interval or (self.match_types and (type(arg) != int)):
            return False, 'Value in {} expected but got {}'.format(self.interval, arg)
        return True