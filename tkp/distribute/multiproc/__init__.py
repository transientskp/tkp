from multiprocessing import Pool, cpu_count

pool = Pool(processes=cpu_count())


def map(func, iterable, args):
    partial = lambda i: func(i, *args)
    pool.map(partial, iterable)
