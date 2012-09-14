"""
functions for calculating statistical properties of LOFAR images
"""
import math
import numpy

def clip(data, sigma=3):
    """
    returns a mask for values above threshold defined by sigma from median
    """
    median = numpy.median(data)
    std = numpy.std(data)
    threshold = median + sigma * std

    mask = numpy.ones(data.shape)
    mask[data > threshold] = 0
    return mask

def rms(data, mask=None):
    """
    returns the RMS of an image, you can optionally supply a mask
    """
    if mask:
        data = data * mask
    n = data.sum()
    return math.sqrt(numpy.power(data, 2).sum()/n)

