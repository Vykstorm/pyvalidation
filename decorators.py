
from itertools import count, chain, repeat
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
        if not iterable(items) and not callable(items):
            raise TypeError()

        self.items = chain(items, repeat(lambda arg: arg)) if iterable(items) else repeat(items)

    def parse(self, *args):
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate(self, *args):
        for item, index, arg in zip(self.items, count(start=1), args):
            try:
                result = item(arg)
                if isinstance(result, (list, tuple)):
                    result = tuple(result)
                    if len(result) >= 2:
                        result = result[:3]
                    elif len(result) == 1:
                        result = result[0]
                    else:
                        result = None

                if type(result) != tuple:
                    valid = result
                    if not valid:
                        raise Exception()
                else:
                    valid, error = result
                    if not valid:
                        raise Exception(error)

            except Exception as e:
                raise Exception('Invalid argument at position {}{}'.format(
                    index,
                    ': {}'.format(e) if len(str(e)) > 0 else ''))

    def parse(self, *args):
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
        return ValidateInput(map(Validator.from_object, args))


class ParseInputDecorator(Decorator):
    empty_arg = None

    def create_processor(self, *args):
        return ParseInput([arg if arg is not None else lambda arg: arg for arg in args])



# Alias of few class decorators
validate = ValidateInputDecorator
parse = ParseInputDecorator

