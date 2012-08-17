"""
functions for calculating statistical properties of LOFAR images
"""

import math
import numpy

def clip(data, sigma=3):
    """
    Clips values in array above defined sigma from median
    """
    median = numpy.median(data)
    std = numpy.std(data)
    copy = data.copy()
    threshold = median + sigma * std
    copy[data > threshold] = threshold
    return copy


def rms(data):
    """
    returns the RMS of an image
    """
    return math.sqrt(numpy.power(data, 2).sum())

