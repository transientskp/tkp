"""
A computation distribution implementation using the build in multiprocessing
module. the Pool.map function only accepts one argument, so we need to
zip the iterable together with the arguments.
"""
import sys
from multiprocessing import Pool, cpu_count, log_to_stderr
import logging

pool = Pool(processes=cpu_count())

logger = log_to_stderr()
logger.setLevel(logging.WARNING)


def set_cores(cores=0):
    """
    set the number of cores to use. 0 = autodetect
    """
    global pool
    if not cores:
        cores = cpu_count()
    pool = Pool(cores)


def map(func, iterable, args):
    zipped = ((i, args) for i in iterable)
    try:
        return pool.map_async(func, zipped).get(9999999)
    except KeyboardInterrupt:
        pool.terminate()
        print "You pressed CTRL-C, exiting"
        sys.exit(1)
