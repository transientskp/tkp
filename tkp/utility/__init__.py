"""
Root level :mod:`tkp.utility` functions that don't justify a submodule:
"""
import math

def nice_format(f):
    if f > 9999 or f < 0.01:
        return "%.2e" % f
    else:
        return "%.2f" % f


def substitute(value, sub, test_f):
    try:
        if test_f(value):
            return sub
    except TypeError:
        pass
    return value


def substitute_inf(value, sub="Infinity"):
    """
    If value is not infinite, return value. Otherwise, return sub.
    """
    return substitute(value, sub, math.isinf)


def substitute_nan(value, sub=0.0):
    """
    If value is not NaN, return value. Otherwise, return sub.

    """
    return substitute(value, sub, math.isnan)


class adict(dict):
    """
    Accessing dict keys like an attribute.
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            msg = "can't find %s, please check your settings file"
            raise AttributeError(msg % key)

    __setattr__ = dict.__setitem__
