

from validation import validate


@validate()
@validate(int)
def foo(x):
    pass

foo(True)
