"""
A computation distribution implementation using the build in multiprocessing
module. the Pool.map function only accepts one argument, so we need to
zip the iterable together with the arguments.
"""
import sys
from multiprocessing import Pool, cpu_count, log_to_stderr

import logging
import atexit

# use this for debugging. Will not fork processes but run everything threaded
THREADED = False

if THREADED:
    from multiprocessing.pool import ThreadPool
    pool = ThreadPool(processes=cpu_count())
else:
    pool = Pool(processes=cpu_count())

atexit.register(lambda: pool.terminate())

logger = log_to_stderr()
logger.setLevel(logging.WARNING)
logger.info("initialising multiprocessing module with "
            "{} cores".format(cpu_count()))


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
