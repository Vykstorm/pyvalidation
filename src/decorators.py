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

    # This argument is used to fill unespecified arguments in the decorator
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

        # Special object used to mark unespecified arguments in the decorator.
        class Placeholder:
            pass

        def parse_ellipsis(args, s):
            '''
            Auxiliar method to parse ellipsis when its specified in decorator positional arguments
            '''
            if Ellipsis not in args:
                # Ellipsis is not in positional args, leave args unchanged.
                return args

            if len(args) == 1:
                # Only Ellipsis value is specified, but not more positional arguments are present.
                # This is equivalent as not indicating any positional argument at all.
                return []

            if args.count(Ellipsis) > 1:
                # Ellipsis value cannot appear more than one time
                raise ValueError('Ellipsis cannot be specified more than one time')

            k = args.index(Ellipsis)

            # Split args in two lists, before and after ellipsis
            a, b = list(args[:k]), list(args[k+1:])
            if len(b) == 0:
                # Ellipsis is the last positional argument.
                # This is equivalent as indicating the positional arguments before the ellipsis
                return a
            n = len(args) - 1

            # How much positional parameters are there?
            m = len([param for param in s.parameters.values() if param.kind == Parameter.POSITIONAL_OR_KEYWORD])
            if n > m:
                # More positional arguments than even positional/keyword parameters.
                # That will raise an exception when binding the arguments to the signature later.
                # Just return the arguments unchanged
                return args

            # Replace ellipsis with a sequence of placeholders such that the number of positional arguments are equal to the number
            # of positional/keyword parameters in the function signature.
            c = [Placeholder] * (m - n)
            return a + c + b

        def merge_args(A, B):
            '''
            Merge two sequences of positional arguments into one.
            '''
            merged = []
            for a, b in zip(A, B):
                if (a == Placeholder) ^ (b == Placeholder):
                    # Only one of the arguments is a placeholder.
                    merged.append(a if a != Placeholder else b)
                elif a == Placeholder and b == Placeholder:
                    # Both arguments are placeholders
                    merged.append(Placeholder)
                else:
                    # None of the arguments are placeholders (Multiple values specified)
                    raise Exception()
            return merged


        if not callable(f):
            raise TypeError()


        # Grab decorator arguments
        args, kwargs = self.args, self.kwargs

        # Fetch wrapped function signature
        s = signature(f, follow_wrapped=True)

        # Parse ellipsis value if needed
        args = parse_ellipsis(args, s)

        # A placeholder is assigned to each parameter as its default value.
        s = s.replace(parameters=[param.replace(default=Placeholder) for param in s.parameters.values()])

        # Bind positional arguments to the function signature (apply also default values)
        bounded_args = s.bind(*args)
        bounded_args.apply_defaults()

        # Bind keyword arguments to the function signature (apply also default values)
        bounded_kwargs = s.bind(**kwargs)
        bounded_kwargs.apply_defaults()

        # Merge the result of both binding processes
        try:
            args = merge_args(bounded_args.args, bounded_kwargs.args)
        except:
            # Merged failed (because of setting multiple values for a single argument)
            s.bind(*args, **kwargs)

        # Replace unespecified arguments with a defualt value
        args = [arg if arg != Placeholder else self.empty_arg for arg in args]

        # Create the function wrapper and return it
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

