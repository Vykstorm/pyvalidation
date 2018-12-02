
'''
This module defines all kinds of validators that can be used to validate your function arguments.
'''


from .utils import iterable as _iterable
from inspect import isclass
from itertools import islice, product
from functools import reduce
import re
from functools import partial
from copy import copy
from decimal import Decimal

_callable = callable



class Validator:
    '''
    Base class for all kind of validators
    '''
    def __init__(self):
        pass

    def __call__(self, arg):
        '''
        This method turns the validator to a callable object. It calls check(arg).
        If check(arg) returns something that evaluates to True, this function returns
        the tuple (True, None). This happens when the given argument is valid.
        Otherwise, the tuple (False, error) is retrieved (when the arg is invalid). Where 'error'
        will be the value returned by the method error_message(arg)
        '''
        result = self.check(arg)
        if result:
            return True, None
        return False, self.error_message(arg)

    def check(self, arg):
        '''
        This method must be implemented by subclasses. It validates the given argument with the validator.
        :param arg: Is the argument to validate.
        :return: Something that evaluates to True if the given argument is valid or not.
        Anything that evaluates to False otherwise.
        '''
        raise NotImplementedError()

    def error_message(self, arg):
        '''
        Retrieves an error message; A brief description explaining why the given argument is not valid.
        This method may be overriden by subclasses
        :param arg:
        :return: Returns a string value, the error message.
        '''
        return ''

    def simplify(self):
        '''
        This method returns an equivalent validator of this instance and is used to optimize validation stage
        (the returned validator maybe more faster checking the arguments than this instance but both of them are still equivalent)
        This maybe overriden by subclasses, by default returns self
        :return: Another validator object.
        '''
        return self


    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)

    @staticmethod
    def from_spec(obj):
        '''
        Creates a validator instance using an object as specification. This is used to turn validate decorator arguments
        into validator objects. Check the examples and test scripts to understand how this is done.
        '''
        if isinstance(obj, Validator):
            return obj

        # Match any type...
        if type(obj) == object:
            return EmptyValidator()

        # Classes and built-in types.
        if isclass(obj):
            return TypeValidator((obj,))

        # Dictionaries
        if isinstance(obj, dict):
            return ValueValidator(obj)

        # Callables
        if _callable(obj):
            return UserValidator(obj)

        # Range objects
        if isinstance(obj, range):
            return RangeValidator(obj)

        # Iterables (only list, tuples, frozensets and sets)
        if isinstance(obj, (list, tuple, set, frozenset)):
            if any(map(isclass, obj)) or any(map(_iterable, obj)):
                return ComposedValidator([Validator.from_spec(item) for item in obj])
            return ValueValidator(obj)

        # Default validator
        return ValueValidator((obj,))


'''
Built-in validators
'''


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
            if not _iterable(types):
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

        types = tuple(frozenset(types))
        if len(types) == 0:
            raise ValueError()

        super().__init__()
        self.types = types
        self.check_subclasses = check_subclasses
        self.check_bool_subclasses = check_bool_subclasses

    def check(self, arg):
        cls = type(arg)
        if not self.check_subclasses or (not self.check_bool_subclasses and cls == bool):
            return cls in self.types
        return isinstance(arg, self.types)

    def error_message(self, arg):
        return 'Type {} expected but got {}'.format(
            ' or '.join([cls.__name__ for cls in self.types]),
            type(arg).__name__)

    def simplify(self):
        if self.check_subclasses and (object in self.types):
            return EmptyValidator()
        return self

    def __str__(self):
        return '<type validator: {}>'.format(', '.join([cls.__name__ for cls in self.types]))


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
        if not _iterable(values):
            raise TypeError()
        values = tuple(values)
        if len(values) == 0:
            raise ValueError()

        if not isinstance(values, (frozenset, tuple)):
            try:
                values = frozenset(values)
            except:
                values = tuple(values)

        self.values = values
        self.match_types = match_types

    def check(self, arg):
        for value in self.values:
            if arg == value and (not self.match_types or (type(arg) == type(value))):
                return True
        return False

    def error_message(self, arg):
        return 'Value {} expected but got {}'.format(
            ' or '.join([str(value) for value in self.values]),
            str(arg))

    def simplify(self):
        try:
            values = frozenset(self.values)
            if len(values) > 2 and all(map(lambda value: type(value) == int, values)):
                values = sorted(values)
                differences = [x-y for x, y in zip(islice(values, 1, len(values)), islice(values, 0, len(values)-1))]
                if len(frozenset(differences)) == 1:
                    step = next(iter(differences))
                    return RangeValidator(range(values[0], values[-1]+1, step))

            return ValueValidator(values, self.match_types)
        except:
            pass
        return self

    def __str__(self):
        return '<value validator: {}>'.format(', '.join([str(value) for value in self.values]))


class EmptyValidator(Validator):
    '''
    This is a special validator. Is an "empty" validator because all given arguments will pass
    its validation stage.
    '''
    def check(self, arg):
        return True

    def __copy__(self):
        return self

    def __str__(self):
        return "<empty validator>"


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

    def check(self, arg):
        return arg in self.interval and ((not self.match_types) or (type(arg) == int))

    def error_message(self, arg):
        return 'Value in {} expected but got {}'.format(self.interval, arg)

    def __str__(self):
        return '<range validator: {}>'.format(self.interval)


class UserValidator(Validator):
    '''
    Its a validator defined by the user (it calls a user defined function to validate the given argument).
    '''
    def __init__(self, func):
        '''
        Initializes this instance.
        :param predicate: It must be a callable object which accepts the argument to be validated. The result must be
        evaluated to True if the given argument is valid or something that evaluates to False otherwise.
        Also it can raise an exception. In such case, that will be equal as returning the value False
        '''
        super().__init__()
        if not _callable(func):
            raise TypeError()
        self.func = func

    def __call__(self, arg):
        try:
            result = self.check(arg)
            if result:
                return True, None
            return False, self.error_message(arg)
        except Exception as e:
            return False, str(e)

    def check(self, arg):
        return self.func(arg)

    def error_message(self, arg):
        func = self.func
        if hasattr(func, '__qualname__'):
            s = func.__qualname__
        elif hasattr(func, '__name__'):
            s = func.__name__
        else:
            s = None
        return 'Expression{} evaluated to False'.format(' {}'.format(s) if s is not None else '', str(arg))

    def __str__(self):
        # TODO
        return '<user validator: {}>'.format('')


class ComposedValidator(Validator):
    '''
    This a kind of validator which are build grouping other validators. The given argument is valid when any of the
    validators that are part of the group are evaluated to True. Otherwise, the argument is not valid.
    '''
    def __init__(self, items=()):
        '''
        Initializes this instance.
        :param items: It can be a list of instances of class Validator.
        '''
        super().__init__()
        if not _iterable(items):
            raise TypeError()
        items = tuple(items)
        if len(items) == 0:
            raise ValueError()

        self.validators = []
        self.extend(items)

    def add(self, item):
        '''
        Adds another validator.
        :param item: The validator to add (must be an instance of class Validator)
        '''
        if not isinstance(item, Validator):
            raise TypeError()
        if isinstance(item, ComposedValidator):
            self.extend(item)
        else:
            self.validators.append(item)

    def extend(self, items):
        '''
        Add a few more validators to this composed validator
        :param items: It must be an iterable where items must be instances of the class Validator
        :return:
        '''
        if not _iterable(items):
            raise TypeError()
        for item in items:
            self.add(item)

    def __copy__(self):
        '''
        Creates a copy of this instance.
        :return: A clone of this object
        '''
        return ComposedValidator(self)

    def __ior__(self, other):
        '''
        This is equivalent to method add() if the given argument is an instance of class Validator or
        the method extend() if its a sequence of validators or another ComposedValidator object.
        :param other: An instance of class Validator or an iterable of Validator objects.
        '''
        if isinstance(other, Validator):
            self.add(other)
        else:
            self.extend(other)
        return self


    def __iter__(self):
        '''
        It allows this instance to be iterable.
        :return: Returns an iterator that walks through all the validators that are part of this composed validator object.
        '''
        return iter(self.validators)

    def __len__(self):
        '''
        Returns the number of validators in this composed validator.
        :return:
        '''
        return len(self.validators)

    def check(self, arg):
        for validator in self:
            if validator.check(arg):
                return True
        return False

    def simplify(self):
        if len(self) == 1:
            return next(iter(self)).simplify()

        validators = [v.simplify() for v in self]

        if any(map(lambda v: isinstance(v, EmptyValidator), validators)):
            return EmptyValidator()

        value_validators = [v for v in validators if isinstance(v, ValueValidator)]
        type_validators = [v for v in validators if isinstance(v, TypeValidator)]
        other_validators = [v for v in validators if not isinstance(v, (ValueValidator, TypeValidator))]

        # Merge type validators if possible
        if len(type_validators) > 1:
            merged = []
            for params in product((False, True), (False, True)):
                types = reduce(tuple.__add__,
                               [tuple(v.types) for v in type_validators if (v.check_subclasses, v.check_bool_subclasses) == params], ())
                types = frozenset(types)
                if len(types) > 0:
                    merged.append(TypeValidator(types, *params))
            type_validators = merged


        # Merge value validators if possible
        if len(value_validators) > 1:
            merged = []
            for match_types in (False, True):
                values = reduce(list.__add__,
                                [list(v.values) for v in value_validators if v.match_types == match_types], [])
                if len(values) > 0:
                    merged.append(ValueValidator(values, match_types))
            value_validators = merged

        # Return the simplied version of this composed validator
        validators = value_validators + type_validators + other_validators
        if len(validators) == 1:
            return next(iter(validators))
        return ComposedValidator(validators)

    def __str__(self):
        return '{{{}}}'.format(' | '.join([str(validator) for validator in self]))




'''
REGEX validators
'''

class matchregex(Validator):
    def __init__(self, pattern, flags=0):
        super().__init__()
        self.prog = re.compile(pattern, flags)

    def check(self, arg):
        return isinstance(arg, str) and self.prog.match(arg)

    def error_message(self, arg):
        if not isinstance(arg, str):
            raise TypeValidator((str,)).error_message(arg)
        raise "\"{}\" string not matching the regex pattern \"{}\"".format(arg, self.prog.pattern)


class fullmatchregex(Validator):
    def __init__(self, pattern, flags=0):
        super().__init__()
        self.prog = re.compile(pattern, flags)

    def check(self, arg):
        return isinstance(arg, str) and self.prog.fullmatch(arg)

    def error_message(self, arg):
        if not isinstance(arg, str):
            raise TypeValidator((str,)).error_message(arg)
        raise "\"{}\" string not fully matching the regex pattern \"{}\"".format(arg, self.prog.pattern)



'''
Number validators
'''

class NumberValidator(TypeValidator):
    '''
    Validator that checks if the given argument is either of type int, float, Decimal
    '''
    def __init__(self):
        super().__init__((int, float, Decimal))

    def error_message(self, arg):
        return 'Numeric type expected but got {}'.format(type(arg).__name__)



class UnsignedIntValidator(TypeValidator):
    '''
    Validator that checks if the given argument is of integer type and greater or equal than 0
    '''
    def __init__(self):
        super().__init__([int])

    def check(self, arg):
        return super().check(arg) and arg >= 0

    def error_message(self, arg):
        return 'int value greater or equal than 0 expected but got {}'.format(type(arg).__name__)

number = NumberValidator()
uint = UnsignedIntValidator()




'''
Misc validators
'''


class iterable(Validator):
    def check(self, arg):
        return _iterable(arg)

    def error_message(self, arg):
        return 'Value {} is not iterable'.format(arg)

class callable(Validator):
    def check(self, arg):
        return _callable(arg)

    def error_message(self, arg):
        return 'Value {} is not callable'.format(arg)
