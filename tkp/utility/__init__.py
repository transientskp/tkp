def nice_format(f):
    if f > 9999 or f < 0.01:
        return "%.2e" % f
    else:
        return "%.2f" % f