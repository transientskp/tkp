"""
A computation distribution implementation using the build in multiprocessing
module. the Pool.map function only accepts one argument, so we need to
zip the iterable together with the arguments.
"""
from multiprocessing import Pool, cpu_count

pool = Pool(processes=cpu_count())


def map(func, iterable, args):
    zipped = ((i, args) for i in iterable)
    return pool.map(func, zipped)

