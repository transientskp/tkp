import math

def nice_format(f):
    if f > 9999 or f < 0.01:
        return "%.2e" % f
    else:
        return "%.2f" % f

def substitute(value, sub, test_f):
    if test_f(value):
        return sub
    else:
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
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__