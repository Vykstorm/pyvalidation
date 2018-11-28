
'''
This module includes the definition of the class Wrapper
'''

from processors import ProcessorBundle
from functools import update_wrapper
from inspect import signature
from utils import iterable
from types import MethodType


class Wrapper(ProcessorBundle):
    '''
    A instance of this class encapsulates a method (Acts like a function wrapper)
    wrappers
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
        self.signature = signature(func, follow_wrapped=True)
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
        output = self.call_wrapped(*self.process_input(*args))

        if not iterable(output):
            output = tuple() if output is None else (output, )

        output = self.process_output(*output)

        if iterable(output):
            if len(output) == 0:
                return None
            return tuple(output) if len(output) > 1 else next(iter(output))
        return output

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
