
'''
This module includes the definition of the class Wrapper
'''

from .processors import ProcessorBundle
from functools import update_wrapper
from inspect import signature, Parameter
from .utils import iterable
from types import MethodType


class FuncWrapper(ProcessorBundle):
    '''
    An instance of this class encapsulates a method:
    When invoked, It can process input argument values before calling the wrapped method.
    '''
    def __init__(self, func):
        '''
        Initializes this instance.
        :param func: Must be a callable object. A regular function, lambda or a class object with the instance method
        __call__
        '''
        if not callable(func):
            raise TypeError()

        super().__init__()
        self.wrapped_func = func
        s = signature(func, follow_wrapped=True)
        s = s.replace(parameters=[param.replace(
            default=InputValueWrapper(param.default, validate=False, parse=False) if param.default != Parameter.empty else param.default)
            for param in s.parameters.values()])
        self.signature = s

        update_wrapper(self, func) # This method sets some attributes to introspect the wrapper object like __qualname__

    def call_wrapped(self, *args, **kwargs):
        '''
        Calls the wrapped function with the given arguments.
        :param args:
        :param kwargs:
        :return:
        '''
        return self.wrapped_func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        '''
        This method make instances of this class callable.
        When called, first it processes its input values calling process_input() as if the wrapped function was called
        with such arguments.

        After that, the wrapped method is called with the processed input values.
        Finally, the output values are processed and returned by this function.

        :param args: Positional arguments to be passed to the wrapped method (they will be processed using the method
        process_input() )
        :param kwargs: Keyword arguments to be passed to the wrapped method (they will be processed using the method
        process_input() )
        :return: Returns what the wrapped function outputs but before that, those values will be processed using the method
        process_output()
        '''
        bounded_args = self.signature.bind(*args, **kwargs)
        bounded_args.apply_defaults()

        args = bounded_args.args
        return self.call_wrapped(*self.process_input(*args))

    def process_input(self, *args):
        args = super().process_input(*args)
        return tuple([arg if not isinstance(arg, InputValueWrapper) else arg.wrapped_value for arg in args])

    def __get__(self, instance, owner):
        '''
        Turns instances of this class to non-data descriptors. This is used when this class is returned when decorating
        a class or instance method. When calling the decorated function, __get__ is called and it will return a method bounded
        to the given instance.
        :param instance:
        :param owner:
        :return:
        '''
        if instance is None:
            return self
        return MethodType(self, instance)

    def __str__(self):
        return str(self.wrapped_func)

    def __repr__(self):
        return repr(self.wrapped_func)




class InputValueWrapper:
    '''
    Instances of this class encapsulates a function input argument.
    '''
    def __init__(self, value, validate=True, parse=True):
        '''
        Initializes this instance.
        :param value: The argument value to be wrapped.
        :param validate: Its a boolean value. If set to False, validators will not check the argument value this instance holds.
        By default is set to True
        :param parse: Its a boolean value. If set to False, parsers will not process the argument value this instance holds.
        By default is set to True
        '''
        if not isinstance(validate, bool):
            raise TypeError()
        if not isinstance(parse, bool):
            raise TypeError()

        self.wrapped_value = value
        self.validate = validate
        self.parse = parse

    def __str__(self):
        return str(self.wrapped_value)

    def __repr__(self):
        return repr(self.wrapped_value)
