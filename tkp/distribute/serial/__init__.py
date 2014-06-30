
def map(func, iterable, arguments=[]):
    x = [func(i, *arguments) for i in iterable]
    return x


def set_cores(cores=0):
    """
    doesn't do anything for serial
    """
    pass