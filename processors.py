'''
This module defines the classes Processor, ProcessorBundle, ValidateInput, ParseInput and ParseOutput
'''

from utils import iterable
from exceptions import ParsingError, ValidationError
from itertools import count
from validators import Validator

class Processor:
    '''
    Represents an object bounded to an arbitrary function which can process its input and output values.
    '''
    def process_input(self, *args):
        '''
        Process input values in some way. Should be implemented by subclasses.
        :param args: The input values to be processed
        :return: Returns a tuple with the processed input values. Must have the same length as the number of input values.
        '''
        return args

    def process_output(self, *args):
        '''
        Process output values. Should be implemented by subclasses.
        :param args: The output values to be processed.
        :return: Returns a tuple with the processed output values. Must have the same size as the number of output values
        indicated.
        '''
        return args


class ProcessorBundle(Processor):
    '''
    Represents a stack of processors (its also a processor)
    '''
    def __init__(self):
        super().__init__()
        self.processors = []

    def append(self, processor):
        '''
        Adds a new processor to the stack.
        :param processor: Must be an instance of the class Processor.
        :return:
        '''
        if not isinstance(processor, Processor):
            raise TypeError()
        self.processors.append(processor)

    def process_input(self, *args):
        for level, processor in zip(count(start=0), reversed(self.processors)):
            try:
                args = processor.process_input(*args)
            except ParsingError as e:
                if len(self.processors) > 1:
                    e.level = level
                raise e
        return args

    def process_output(self, *args):
        for level, processor in zip(map(lambda x: len(self.processors) - x + 1, count(start=0)),
                                    self.processors):
            try:
                args = processor.process_output(*args)
            except ParsingError as e:
                if len(self.processors) > 1:
                    e.level = level
                raise e
        return args

    def __iadd__(self, processor):
        self.append(processor)
        return self




class Parse:
    '''
    Base class for ParseInput and ParseOutput
    '''
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
        for item, index, arg in zip(self.items, count(start=0), args):
            try:
                if isinstance(arg, InputValueWrapper):
                    if not arg.parse:
                        result.append(arg)
                        continue
                    arg = arg.wrapped_value
                result.append(item(arg))
            except Exception as e:
                raise ParsingError(index, str(e))
        return result



class ParseInput(Parse, Processor):
    '''
    Represents a processor which parses inputs values with the given items.
    '''
    def __init__(self, items):
        Processor.__init__(self)
        Parse.__init__(self, items)

    def process_input(self, *args):
        return self.parse(*args)


class ParseOutput(Parse, Processor):
    '''
    Represents a processor which parses output values with the given items.
    '''
    def __init__(self, items):
        Processor.__init__(self)
        Parse.__init__(self, items)

    def process_output(self, *args):
        return self.parse(*args)


class ValidateInput(ParseInput):
    '''
    Its a processor which validates the input values using the given validators.
    '''
    def __init__(self, items):
        '''
        Initializes this instance.
        :param items: Must be an iterable list with Validator instance objects to validate the input values.
        '''
        if not iterable(items) and not isinstance(items, Validator):
            raise TypeError()
        if isinstance(items, Validator) and not all(map(lambda item: isinstance(item, Validator), items)):
            raise TypeError()
        validators = items
        super().__init__([validator.simplify() for validator in validators])

    def validate(self, *args):
        for validator, index, arg in zip(self.items, count(start=0), args):
            if isinstance(arg, InputValueWrapper):
                if not arg.validate:
                    continue
                arg = arg.wrapped_value
            valid, error = validator(arg)
            if not valid:
                raise ValidationError(index, error)

    def parse(self, *args):
        if len(self.items) != len(args):
            raise ValueError()
        self.validate(*args)
        return args

# This import is written here because of cyclic import issues
from wrappers import InputValueWrapper