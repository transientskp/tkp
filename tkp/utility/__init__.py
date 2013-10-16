import math

def nice_format(f):
    if f > 9999 or f < 0.01:
        return "%.2e" % f
    else:
        return "%.2f" % f

def substitute_nan(value, substitute=0.0):
    """
    If value is not NaN, return value. Otherwise, return substitute.
    """
    if math.isnan(value):
        return substitute
    else:
        return value
