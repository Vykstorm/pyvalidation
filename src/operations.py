
from re import sub, search
import operator


class Operation:
    '''
    Objects of this instance represents some kind of transformation for any given input value.
    x -> f(x)
    '''
    def __init__(self, expr):
        '''
        Initializes this instance.
        :param expr: This argument is used to stringify this instance with a nice format. It must be a string value.
        For example:
        "(x // 20) + 10 >> (x // 4)"
        The symbol x is used as a placeholder so that when converting this object to string, it is replaced by the given input
        value.
        '''
        if not isinstance(expr, str):
            raise TypeError()
        if search('{}', expr):
            raise ValueError()

        self.expr = expr

    def __call__(self, x):
        '''
        Evaluates this operation for the given input x and returns the result
        Must be overriden by subclasses.
        '''
        raise NotImplementedError()

    # Stringify

    def format(self, x):
        '''
        Returns a formatted string version of this instance for the given input x
        :param x:
        :return:
        '''
        s = sub('^x(.*)$', '{}\\1', self.expr)
        s = sub('^(.*)x$', '\\1{}', s)
        s = sub('([^\'\"])x([^\'\"])', '\\1{}\\2', s)
        return s.replace('{}', str(x) if not isinstance(x, str) else "'{}'".format(x))

    def __str__(self):
        return self.expr

    def __repr__(self):
        return str(self)


    # Arithmetic operations

    def __add__(self, other):
        return BinaryOperation(Operator.__add__, self, other)

    def __sub__(self, other):
        return BinaryOperation(Operator.__sub__, self, other)

    def __floordiv__(self, other):
        return BinaryOperation(Operator.__floordiv__, self, other)

    def __mod__(self, other):
        return BinaryOperation(Operator.__mod__, self, other)

    def __mul__(self, other):
        return BinaryOperation(Operator.__mul__, self, other)

    def __matmul__(self, other):
        return BinaryOperation(Operator.__matmul__, self, other)

    def __pow__(self, power):
        return BinaryOperation(Operator.__pow__, self, power)

    def __truediv__(self, other):
        return BinaryOperation(Operator.__truediv__, self, other)

    def __neg__(self):
        return UnaryOperation(Operator.__neg__, self)

    def __pos__(self):
        return UnaryOperation(Operator.__pos__, self)

    def __abs__(self):
        return UnaryOperation(Operator.__abs__, self)



    # Bitwise operations

    def __and__(self, other):
        return BinaryOperation(Operator.__and__, self, other)

    def __or__(self, other):
        return BinaryOperation(Operator.__or__, self, other)

    def __xor__(self, other):
        return BinaryOperation(Operator.__xor__, self, other)

    def __lshift__(self, other):
        return BinaryOperation(Operator.__lshift__, self, other)

    def __rshift__(self, other):
        return BinaryOperation(Operator.__rshift__, self, other)

    def __invert__(self):
        return UnaryOperation(Operator.__invert__, self)


    # Container operations

    def __getitem__(self, item):
        return BinaryOperation(Operator.__getitem__, self, item)


    # Comparision operators

    def __lt__(self, other):
        return BinaryOperation(Operator.__lt__, self, other)

    def __le__(self, other):
        return BinaryOperation(Operator.__le__, self, other)

    def __eq__(self, other):
        return BinaryOperation(Operator.__eq__, self, other)

    def __ne__(self, other):
        return BinaryOperation(Operator.__ne__, self, other)

    def __ge__(self, other):
        return BinaryOperation(Operator.__ge__, self, other)

    def __gt__(self, other):
        return BinaryOperation(Operator.__gt__, self, other)


class Operator:
    '''
    Instances of this class describes an operator; A function that accepts one ore more input values and return a unique
    output value.
    f: x1, x2, ..., xn -> y
    e.g:
    an example of operator could be the binary sum operation:
    f(a, b) = a + b
    '''
    def __init__(self, expr, func):
        '''
        Initializes this instance.
        :param expr: It must be a string used when converting this instance to string.
        e.g:
        "{} + {}" can be used to stringify the operator f(a, b) = a + b
        "{}" substrings will be replaced by the input values.

        :param func: This argument must be a callable object, lambda or regular function. func(...) will actually implement
        the operation.
        For example, when defining the binary sum operator f(a, b) = a + b,
        func could be set as "lambda a, b: a + b"
        '''
        if not isinstance(expr, str):
            raise TypeError()
        if not callable(func):
            raise TypeError()

        self.func = func
        self.expr = expr

    def __call__(self, *args):
        '''
        Evaluates this operator for the given input operands and returns the output.
        '''
        return self.func(*args)


    def format(self, *args):
        '''
        Returns a formatted string version of this instance for the given input values.
        '''
        args = [arg.expr if not isinstance(arg, BinaryOperation) else '({})'.format(arg.expr) for arg in args]
        return self.expr.format(*args)

    def __str__(self):
        return self.expr

    def __repr__(self):
        return str(self)

class BinaryOperator(Operator):
    '''
    Defines any operator with two input operands.
    '''
    def __init__(self, expr, func):
        if not isinstance(expr, str):
            raise TypeError()
        super().__init__(expr if search('{}.*{}', expr) else ' '.join(('{}', expr, '{}')), func)


class UnaryOperator(Operator):
    '''
    Defines any operator with only one input operand
    '''
    def __init__(self, expr, func):
        super().__init__(expr if search('{}', expr) else expr+'{}', func)



class Identity(Operation):
    '''
    Special transformation which is defined like f(x) = x
    '''
    def __init__(self):
        super().__init__(expr='x')

    def __call__(self, x):
        return x


class Constant(Operation):
    '''
    Special transformation which is defined like: f(x) = k
    '''
    def __init__(self, k):
        super().__init__(expr=str(k) if not isinstance(k, str) else "'{}'".format(k))
        self.k = k

    def __call__(self, x):
        return self.k



class BinaryOperation(Operation):
    '''
    Transformation which is defined like f(x) = op(g(x), h(x))
    Where op is any binary operator and g, h are also operations.
    e.g:
    f(x) = binary_sum(g(x), h(x)) with g(x) = x, h(x) = 1 will be interpreted as
    f(x) = x + 1
    '''
    def __init__(self, op, g, h):
        '''
        Initializes this instance.
        :param op: Must be any instance of the class BinaryOperator
        :param g: Must be an instance of class Operation
        :param h: Must be an instance of class Operation
        '''
        if not isinstance(op, BinaryOperator):
            raise TypeError()

        if not isinstance(g, Operation):
            g = Constant(g)

        if not isinstance(h, Operation):
            h = Constant(h)

        super().__init__(
            expr=op.format(g, h)
        )
        self.op = op
        self.g, self.h = g, h

    def __call__(self, x):
        return self.op(self.g(x), self.h(x))



class UnaryOperation(Operation):
    '''
    Operation which is defined like f(x) = op(g(x))
    Where op is any unary operator and g(x) is other operation.
    e.g:
    f(x) = negate(g(x)) where negate(x) = -x
    if for example g(x) = x, f(x) will be interpreted as
    f(x) = -x
    '''
    def __init__(self, op, g):
        '''
        Initializes this instance.
        :param op: Instance of class UnaryOperator
        :param g: Instance of class Operation
        '''
        if not isinstance(op, UnaryOperator):
            raise TypeError()
        if not isinstance(g, Operation):
            g = Constant(g)

        super().__init__(
            expr=op.format(g)
        )
        self.op = op
        self.g = g

    def __call__(self, x):
        return self.op(self.g(x))


# Arithmetic operations

Operator.__add__ = BinaryOperator('+', operator.__add__)
Operator.__sub__ = BinaryOperator('-', operator.__sub__)
Operator.__floordiv__ = BinaryOperator('//', operator.__floordiv__)
Operator.__mod__ = BinaryOperator('%', operator.__mod__)
Operator.__mul__ = BinaryOperator('*', operator.__mul__)
Operator.__matmul__ = BinaryOperator('@', operator.__matmul__)
Operator.__pow__ = BinaryOperator('**', operator.__pow__)
Operator.__truediv__ = BinaryOperator('/', operator.__truediv__)
Operator.__neg__ = UnaryOperator('-', operator.__neg__)
Operator.__pos__ = UnaryOperator('+', operator.__pos__)
Operator.__abs__ = UnaryOperator('|{}|', operator.__abs__)


# Bitwise operations
Operator.__and__ = BinaryOperator('&', operator.__and__)
Operator.__or__ = BinaryOperator('|', operator.__or__)
Operator.__xor__ = BinaryOperator('^', operator.__xor__)
Operator.__lshift__ = BinaryOperator('<<', operator.__lshift__)
Operator.__rshift__ = BinaryOperator('>>', operator.__rshift__)
Operator.__invert__ = UnaryOperator('~', operator.__invert__)

# Container operations
Operator.__getitem__ = BinaryOperator('{}[{}]', operator.__getitem__)

# Comparision validators
Operator.__lt__ = BinaryOperator('<', operator.__lt__)
Operator.__le__ = BinaryOperator('<=', operator.__le__)
Operator.__eq__ = BinaryOperator('==', operator.__eq__)
Operator.__ne__ = BinaryOperator('!=', operator.__ne__)
Operator.__ge__ = BinaryOperator('>=', operator.__ge__)
Operator.__gt__ = BinaryOperator('>', operator.__gt__)



# This import statement is defined here to avoid dependency cycles
from .validators import UserValidator

# Identity aliases
placeholder = Identity()
arg = placeholder
