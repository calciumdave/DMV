from itertools import *

def flatMap(function, iterable):
    return chain.from_iterable(map(function, iterable))
