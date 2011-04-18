#
# LOFAR Transients Key Project
#
# Memoization.
#
from weakref import WeakKeyDictionary
from functools import update_wrapper


class Memoize(object):
    """Decorator to cache the results of methods.

    Examples in e.g. image.py::

        @Memoize
        def _grids(self):
            return self.__grids()
        grids = property(fget=_grids, fdel=_grids.delete)

    """

    def __init__(self, funct):
        self.funct = funct
        self.memo = WeakKeyDictionary()
        update_wrapper(self, self.funct)

    def __call__(self, instance):
        if instance not in self.memo:
            self.memo[instance] = self.funct(instance)
        return self.memo[instance]

    def delete(self, instance):
        """Forget a memoized value"""
        try:
            del(self.memo[instance])
        except KeyError:
            pass
