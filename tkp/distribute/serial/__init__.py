
def map(func, iterable, arguments):
    x = [func(i, *arguments) for i in iterable]
    return x
