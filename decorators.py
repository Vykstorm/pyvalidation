
from itertools import count, chain, repeat, islice
from inspect import signature, isclass
from utils import iterable
import types
from types import MethodType
from validators import Validator, EmptyValidator
from functools import update_wrapper

class Processor:
    def process_input(self, *args):
        return args

    def process_output(self, *args):
        return args


class ProcessorBundle(Processor):
    def __init__(self):
        super().__init__()
        self.processors = []

    def append(self, processor):
        if not isinstance(processor, Processor):
            raise TypeError()
        self.processors.append(processor)

    def process_input(self, *args):
        for level, processor in zip(count(start=1), reversed(self.processors)):
            try:
                args = processor.process_input(*args)
            except Exception as e:
                if len(self.processors) > 1:
                    raise Exception('{} (at level {})'.format(e, level))
                raise e
        return args

    def process_output(self, *args):
        for level, processor in zip(map(lambda x: len(self.processors) - x + 1, count(start=1)),
                                    self.processors):
            try:
                args = processor.process_output(*args)
            except Exception as e:
                if len(self.processors) > 1:
                    raise Exception('{} (at level {})'.format(e, level))
                raise e
        return args

    def __iadd__(self, processor):
        self.append(processor)
        return self


class Wrapper(ProcessorBundle):
    def __init__(self, func):
        super().__init__()
        self.wrapped_func = func
        self.signature = signature(func, follow_wrapped=True)
        update_wrapper(self, func)

    def call_wrapped(self, *args, **kwargs):
        return self.wrapped_func(*args, **kwargs)

    def __call__(self, *args, **kwargs):
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
        if instance is None:
            return self
        return MethodType(self, instance)

    def __str__(self):
        return str(self.wrapped_func)

    def __repr__(self):
        return repr(self.wrapped_func)

class Parser:
    def __init__(self, items):
        if not iterable(items):
            raise TypeError()
        if not all(map(lambda item: callable(item), items)):
            raise TypeError()
        self.items = tuple(items)

    def parse(self, *args):
        if len(self.items) != len(args):
            raise ValueError()

        result = []
        for item, index, arg in zip(self.items, count(start=1), args):
            try:
                result.append(item(arg))
            except Exception as e:
                raise Exception('Error parsing argument with {}() at position {}{}'.format(
                    item.__name__,
                    index,
                    ': {}'.format(e) if len(str(e)) > 0 else ''))
        return result



class ParseInput(Parser, Processor):
    def __init__(self, items):
        Processor.__init__(self)
        Parser.__init__(self, items)

    def process_input(self, *args):
        return self.parse(*args)


class ParseOutput(Parser, Processor):
    def __init__(self, items):
        Processor.__init__(self)
        Parser.__init__(self, items)

    def process_output(self, *args):
        return self.parse(*args)


class ValidateInput(ParseInput):
    def __init__(self, items):
        if not iterable(items) and not isinstance(items, Validator):
            raise TypeError()
        if isinstance(items, Validator) and not all(map(lambda item: isinstance(item, Validator), items)):
            raise TypeError()
        validators = items
        super().__init__([validator for validator in validators])

    def validate(self, *args):
        for validator, index, arg in zip(self.items, count(start=1), args):
            valid, error = validator(arg)
            if not valid:
                raise Exception('Invalid argument at position {}{}'.format(
                    index,
                    ': {}'.format(error) if len(error) > 0 is not None else ''))

    def parse(self, *args):
        if len(self.items) != len(args):
            raise ValueError()
        self.validate(*args)
        return args


class Decorator:
    empty_arg = None

    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs

    def __call__(self, f):
        if not callable(f):
            raise TypeError()

        s = signature(f, follow_wrapped=True)
        s = s.replace(parameters=[param.replace(default=self.empty_arg) for param in s.parameters.values()])
        bounded_args = s.bind(*self.args, **self.kwargs)
        bounded_args.apply_defaults()

        processor = self.create_processor(*bounded_args.args)
        wrapper = Wrapper(f) if not isinstance(f, Wrapper) else f
        wrapper.append(processor)
        return wrapper

    def create_processor(self, *args):
        raise NotImplementedError()


class ValidateInputDecorator(Decorator):
    empty_arg = EmptyValidator()

    def create_processor(self, *args):
        return ValidateInput(map(Validator.from_spec, args))


class ParseInputDecorator(Decorator):
    empty_arg = None

    def create_processor(self, *args):
        return ParseInput([arg if arg is not None else lambda arg: arg for arg in args])



# Alias of few class decorators
validate = ValidateInputDecorator
parse = ParseInputDecorator

