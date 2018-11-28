'''
This module defines the classes Processor and ProcessorBundle
'''


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