
'''
This module defines all kinds of validators that can be used to validate your function arguments.
'''


from .utils import iterable as _iterable, hashable as _hashable, format_sequence, format_range, islambda
from .operations import Operation
from inspect import isclass
import re
from decimal import Decimal



class Validator:
    '''
    Instances of this class represents validators that verifies if function input arguments are correct or not.
    '''

    def __call__(self, arg):
        '''
        Validates the input argument with this validator instance:
        Raises an exception if the given argument is not valid, otherwise it just returns True
        '''
        if not self.validate(arg):
            raise Exception(self.error_message(arg))
        return True

    def validate(self, arg):
        '''
        Validates the input argument with this validator instance.
        This method will return something that evaluates to true if the input argument is valid. Otherwise returns something
        that evaluates to false
        Must be implemented by subclasses.
        '''
        raise NotImplementedError()

    def error_message(self, arg):
        '''
        This is called to generate an error message to be displayed with information telling why the input argument
        is not valid.
        '''
        return ''

    # Operators to created composed validators

    def __or__(self, other):
        return DisjunctValidator((self, other))

    def __and__(self, other):
        return ConjunctValidator((self, other))

    def __invert__(self):
        return InvertedValidator(self)

    def __xor__(self, other):
        return self & ~other | ~self & other

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return str(self)


    @staticmethod
    def from_spec(obj):
        # Match any type...
        if obj is object:
            return EmptyValidator()

        # Match any callable object
        if obj is callable:
            return CallableValidator()

        if isinstance(obj, Validator):
            return obj

        # Expressions
        if isinstance(obj, Operation):
            return UserValidator(obj)


        # Classes and built-in types.
        if isclass(obj):
            return TypeValidator((obj,))

        # Dictionaries
        if isinstance(obj, dict):
            return ValueValidator(obj)

        # Callables
        if callable(obj):
            return UserValidator(obj)

        # Range objects
        if isinstance(obj, range):
            return RangeValidator(obj)

        # Iterables (only list, tuples, frozensets and sets)
        if isinstance(obj, (list, tuple, set, frozenset)):
            if any(map(isclass, obj)) or any(map(_iterable, obj)):
                return DisjunctValidator([Validator.from_spec(item) for item in obj])
            return ValueValidator(obj)

        # Default validator
        return ValueValidator((obj,))


class UserValidator(Validator):
    '''
    Validators defined by the user.
    '''
    def __init__(self, func):
        '''
        Initializes this instance. A function or callable object must be passed as argument
        That function will be invoked when an input argument must be validated with this instance.
        It must accept one argument and return something that evaluates to True if such argument is valid or something
        that evaluates to false or raise an exception otherwise.
        '''
        if not callable(func):
            raise TypeError()

        super().__init__()
        self.func = func

    def __call__(self, arg):
        try:
            if self.func(arg):
                return True
        except Exception as e:
            if len(str(e)) > 0:
                raise e
        raise Exception(self.error_message(arg))

    def validate(self, arg):
        try:
            return self.func(arg)
        except:
            return False

    def error_message(self, arg):
        func = self.func
        if isinstance(func, Operation):
            return 'Expression {} evaluated to false'.format(func.format(arg))

        if not islambda(func):
            if hasattr(func, '__qualname__'):
                s = func.__qualname__
            elif hasattr(func, '__name__'):
                s = func.__name__
            else:
                s = None
        else:
            s = None
        return 'Expression{} evaluated to false'.format(' {}({})'.format(s, arg) if s is not None else '', str(arg))


class EmptyValidator(Validator):
    '''
    Validator that matches any input argument.
    '''
    def validate(self, arg):
        return True


class DisjunctValidator(Validator):
    '''
    This validator is composed by a set of different validators (at least 1).
    An input argument is considered valid if its also valid for at least one of the validators that
    this instance is composed with.
    '''
    def __init__(self, items):
        if not _iterable(items):
            raise TypeError()
        validators = tuple([item if isinstance(item, Validator) else Validator.from_spec(item) for item in items])
        if len(validators) == 0:
            raise ValueError()

        self.validators = tuple(validators)

    def validate(self, arg):
        for validator in self.validators:
            if validator.validate(arg):
                return True
        return False


class ConjunctValidator(Validator):
    '''
    This validator is composed by a set of different validators (at least 1)
    An input argument is considered valid if its also valid for all of the validators that this instance
    is composed with
    '''

    def __init__(self, items):
        if not _iterable(items):
            raise TypeError()
        validators = tuple([item if isinstance(item, Validator) else Validator.from_spec(item) for item in items])
        if len(validators) == 0:
            raise ValueError()

        self.validators = tuple(validators)

    def validate(self, arg):
        for validator in self.validators:
            if not validator.validate(arg):
                return False
        return True


class InvertedValidator(Validator):
    '''
    This validator is the inverted version of other validator instance.
    An input argument is considered valid if its not valid for the other validator.
    '''

    def __init__(self, item):
        if not isinstance(item, Validator):
            validator = Validator.from_spec(item)
        else:
            validator = item

        self.validator = validator

    def validate(self, arg):
        if self.validator.validate(arg):
            return False
        return True



class TypeValidator(Validator):
    '''
    A validator that checks if the given input arguments has a expected type.
    '''
    def __init__(self, types):
        if not _iterable(types):
            raise Exception()
        if not all(map(isclass, types)):
            raise TypeError()

        types = tuple(frozenset(types))
        if len(types) == 0:
            raise ValueError()

        super().__init__()
        self.types = types

    def validate(self, arg):
        if object in self.types:
            return True
        if type(arg) == bool:
            return bool in self.types
        return isinstance(arg, self.types)

    def error_message(self, arg):
        return 'Type {} expected but got {}'.format(
            ' or '.join([cls.__name__ for cls in self.types]),
            type(arg).__name__)



class ValueValidator(Validator):
    '''
    Validator that checks if a given argument takes a discrete value within a set or list of predefined values.
    '''
    def __init__(self, values):
        if not _iterable(values):
            raise TypeError()
        values = tuple(values)
        if len(values) == 0:
            raise ValueError()

        super().__init__()
        try:
            values = frozenset(values)
        except:
            pass
        self.values = values

    def validate(self, arg):
        cls = type(arg)
        for value in self.values:
            if cls == type(value) and arg == value:
                return True
        return False

    def error_message(self, arg):
        return 'Value in {} expected but got {}'.format(
            format_sequence(self.values),
            arg)


class RangeValidator(Validator):
    '''
    Validator that checks if the given argument is of integer type and its within some range
    '''
    def __init__(self, interval):
        if not isinstance(interval, range):
            raise TypeError()
        self.interval = interval

    def validate(self, arg):
        return type(arg) == int and arg in self.interval

    def error_message(self, arg):
        return 'Value in {} expected but got {}'.format(format_range(self.interval), arg)


class MatchRegexValidator(TypeValidator):
    '''
    Validator that checks if input arguments are strings and also matches some regex pattern.
    '''
    def __init__(self, pattern, flags=0):
        super().__init__(types=(str,))
        self.prog = re.compile(pattern, flags)

    def validate(self, arg):
        if not super().validate(arg):
            return False
        return self.prog.match(arg)

    def error_message(self, arg):
        if not super().validate(arg):
            return super().error_message(arg)
        return "\"{}\" string not matching the regex pattern \"{}\"".format(arg, self.prog.pattern)


class FullMatchRegexValidator(TypeValidator):
    '''
    Validator that checks if input arguments are strings and also fully matches some regex pattern.
    '''
    def __init__(self, pattern, flags=0):
        super().__init__(types=(str,))
        self.prog = re.compile(pattern, flags)

    def validate(self, arg):
        if not super().validate(arg):
            return False
        return self.prog.fullmatch(arg)

    def error_message(self, arg):
        if not super().validate(arg):
            return super().error_message(arg)
        return "\"{}\" string not fully matching the regex pattern \"{}\"".format(arg, self.prog.pattern)


class IterableValidator(Validator):
    '''
    Validator that checks if the given argument is iterable or not.
    '''
    def validate(self, arg):
        return _iterable(arg)

    def error_message(self, arg):
        return 'Value {} is not iterable'.format(arg)


class CallableValidator(Validator):
    '''
    Validator that checks if the given argument is callable or not
    '''
    def validate(self, arg):
        return callable(arg)

    def error_message(self, arg):
        return 'Value {} is not callable'.format(arg)


class HashableValidator(Validator):
    '''
    Validator that checks if the given argument is hashable or not (if it implements the method __hash__)
    '''
    def validate(self, arg):
        return _hashable(arg)

    def error_message(self, arg):
        return 'Value {} is not hashable'.format(arg)


class NumberValidator(TypeValidator):
    '''
    This validator matches any numeric value (instances of int, float or Decimal classes)
    '''
    def __init__(self):
        super().__init__(types=(int, float, Decimal))

    def error_message(self, arg):
        return 'Numeric type expected but got {}'.format(type(arg).__name__)


class NdarrayValidator(TypeValidator):
    '''
    This validators matches only ndarrays (numpy arrays). Also filters for the shape, size or dtype properties of the array can
    be indicated.
    This validator can only be used if numpy module is avaliable.
    '''
    def __init__(self, dtype=None, ndim=None, size=None, shape=None):
        '''
        Initializes this instance. If numpy module is not avaliable, this will raise an import error.
        :param dtype: Is the expected dtype of the ndarray, must be a ninstance of class np.dtype or a subclass of np.generic
        :param ndim: Is the expected dimensions of the ndarray. Must be an int >= 1
        :param size: Number of total items expected on ndarray. Must be an int >= 0
        :param shape: Expected shape of the ndarray. Must be a tuple or list of ints. Each dim size must be >= 1
        This parameter cannot be used when indicating ndim neither size parameters.
        '''
        import numpy as np
        from numpy import ndarray

        if dtype is not None and ((not isclass(dtype) or not issubclass(dtype, np.generic)) and not isinstance(dtype, np.dtype)):
            raise TypeError('dtype must be a valid numpy type')

        if ndim is not None and shape is not None:
            raise ValueError('ndim and shape arguments cannot be specified together')

        if size is not None and shape is not None:
            raise ValueError('size and shape arguments cannot be specified together')

        if ndim is not None:
            if not isinstance(ndim, int):
                raise TypeError('ndim must be an int value')
            if ndim < 1:
                raise ValueError('ndim must be greater or equal than 1')

        if size is not None:
            if not isinstance(size, int):
                raise TypeError('size must be an int value')
            if size < 0:
                raise ValueError('size must be greater or equal than 0')

        if shape is not None:
            if not isinstance(shape, (list, tuple)):
                raise TypeError('shape must be a tuple or a list object')

            if not all(map(lambda dim: isinstance(dim, int) and dim >= 1, shape)):
                raise ValueError('shape dimensions must be int values greater or equal than 1')

            shape = tuple(shape)

            if len(shape) == 0:
                raise ValueError('At least one dimension must be specified')

        super().__init__(types=(ndarray,))

        self.dtype = dtype
        self.ndim = ndim
        self.size = size
        self.shape = shape

    def __call__(self, *args, **kwargs):
        if len(kwargs) > 0:
            return NdarrayValidator(**kwargs)
        return super().__call__(*args)

    def validate(self, arg):
        if not super().validate(arg):
            return False

        if self.dtype is not None and arg.dtype != self.dtype:
            return False

        if self.shape is None:
            if self.ndim is not None and arg.ndim != self.ndim:
                return False
            if self.size is not None and arg.size != self.size:
                return False
        else:
            if arg.shape != self.shape:
                return False

        return True

    def error_message(self, arg):
        import numpy as np

        if not super().validate(arg):
            return super().error_message(arg)

        if self.dtype is not None and arg.dtype != self.dtype:
            return 'Expected ndarray {} dtype but got {}'.format(
                str(self.dtype) if isinstance(self.dtype, np.dtype) else self.dtype.__name__,
                arg.dtype)

        if self.shape is None:
            if self.ndim is not None and arg.ndim != self.ndim:
                return 'Expected {}D-array but got {}D-array'.format(self.ndim, arg.ndim)

            if self.size is not None and arg.size != self.size:
                return 'Expected ndarray with {} elements but got {} instead'.format(self.size, arg.size)

        else:
            if arg.shape != self.shape:
                return 'Expected {} array but got {} array'.format(
                    'x'.join(map(str, self.shape)),
                    'x'.join(map(str, arg.shape))
                )

        return ''




# Validator aliases and singletons

matchregex = MatchRegexValidator
fullmatchregex = FullMatchRegexValidator

iterable = IterableValidator()
hashable = HashableValidator()

number = NumberValidator()
Number = number

array = NdarrayValidator()
Array = array

# Single type validators

Int = TypeValidator((int,))
Float = TypeValidator((float,))
Bool = TypeValidator((bool,))
Complex = TypeValidator((complex,))
Str = TypeValidator((str,))

Bytes = TypeValidator((bytes,))
ByteArray = TypeValidator((bytearray,))

List = TypeValidator((list,))
Tuple = TypeValidator((tuple,))
Set = TypeValidator((set,))
FrozenSet = TypeValidator((frozenset,))

Dict = TypeValidator((dict,))