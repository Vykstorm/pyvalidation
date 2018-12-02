'''
This module defines the classes Decorator, ValidateInputDecorator and ParseInputDecorator.
validate is an alias of ValidateInputDecorator class, and parse is an alias of ParseInputDecorator
'''

from inspect import signature, Parameter
from .validators import Validator
from .processors import ValidateInput, ParseInput
from .wrappers import FuncWrapper


class Decorator:
    '''
    Base class for ValidateinputDecorator and ParseInputDecorator
    '''
    empty_arg = None

    def __init__(self, *args, **kwargs):
        '''
        Initializes this instance.
        :param args: Positional arguments indicated in the decorator.
        :param kwargs: Keyword arguments indicated in the decorator.
        '''
        self.args, self.kwargs = args, kwargs

    def __call__(self, f):
        '''
        This is called when this decorator is used to decorate the given function.
        :param f: The function to decorate (Must be a callable object)
        :return: Returns a function wrapper (instance of the class Wrapper)
        '''

        class Placeholder:
            pass

        def parse_ellipsis(args, s):
            if Ellipsis not in args:
                return args
            k = args.index(Ellipsis)

            a, b = list(args[:k]), list(args[k+1:])
            if len(b) == 0:
                return a
            n = len(args) - 1

            params = [param for param in s.parameters.values() if param.kind == Parameter.POSITIONAL_OR_KEYWORD]
            m = len(params)
            if n > m:
                return args

            c = [Placeholder] * (m - n)
            return a + c + b

        def merge_args_kwargs(A, B):
            merged = []
            for a, b in zip(A, B):
                if (a == Placeholder) ^ (b == Placeholder):
                    merged.append(a if a != Placeholder else b)
                elif a == Placeholder and b == Placeholder:
                    merged.append(Placeholder)
                else:
                    raise Exception()
            return merged


        if not callable(f):
            raise TypeError()

        args, kwargs = self.args, self.kwargs

        s = signature(f, follow_wrapped=True)

        args = parse_ellipsis(args, s)
        s = s.replace(parameters=[param.replace(default=Placeholder) for param in s.parameters.values()])
        bounded_args = s.bind(*args)
        bounded_args.apply_defaults()

        bounded_kwargs = s.bind(**kwargs)
        bounded_kwargs.apply_defaults()

        try:
            args = merge_args_kwargs(bounded_args.args, bounded_kwargs.args)
        except:
            s.bind(*args, **kwargs)
        args = [arg if arg != Placeholder else self.empty_arg for arg in args]
        processor = self.create_processor(*args)
        wrapper = FuncWrapper(f) if not isinstance(f, FuncWrapper) else f
        wrapper.append(processor)
        return wrapper

    def create_processor(self, *args):
        raise NotImplementedError()


class ValidateInputDecorator(Decorator):
    '''
    A decorator to add input values validation feature.
    '''
    empty_arg = object

    def create_processor(self, *args):
        return ValidateInput(map(Validator.from_spec, args))


class ParseInputDecorator(Decorator):
    '''
    A decorator to add input values parsing feature
    '''
    empty_arg = None

    def create_processor(self, *args):
        return ParseInput([arg if arg is not None else lambda arg: arg for arg in args])



# Alias of class ValidateInputDecorator
validate = ValidateInputDecorator

# Alias of class ParseInputDecorator
parse = ParseInputDecorator

