"""
`tkp.distribute` implement various computation distribution methods. All
sub modules should communicate with the other parts of TKP through the
`tkp.steps` submodule.
"""

import importlib
import logging


logger = logging.getLogger(__name__)


class Runner(object):
    def __init__(self, distributor):
        """
        Args:
            distributor: the name of the distribution method, example multiproc
        """
        logger.debug("Using %s distribution method" % distributor)
        self.distributor = distributor
        mod_path = __name__ + '.' + distributor
        try:
            self.module = importlib.import_module(mod_path)
            self.tasks = importlib.import_module(mod_path + '.tasks')
        except ImportError:
            raise NotImplementedError("%s not found" % mod_path)
        if not hasattr(self.module, 'map'):
            raise NotImplementedError("%s misses map function" % mod_path)

    def run(self, func_name, *args, **kwargs):
        logger.debug("Running %s in %s" % (func_name, self.dist_module))
        func = getattr(self.dist_module, func_name)
        func(*args, **kwargs)

    def map(self, func_name, iterable, args):
        """
        args:
            func: The function to be called
            iterable: a list of objects to iterate over
            arguments: list of arguments to give to the function
        returns:
            the results of all mapped functions
        """
        func = self.get_func(func_name)
        return self.module.map(func, iterable, args)

    def get_func(self, func_name):
        return getattr(self.tasks, func_name)

    def __getattr__(self, item):
        return self.get_func(item)