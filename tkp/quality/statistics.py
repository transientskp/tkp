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
    mask = numpy.zeros(data.shape)
    mask[data < threshold] = 1
    return mask

def iterative_clip(data, sigma=3):
    """
    returns a mask for values above threshold defined by sigma from median
    iterative means keep clipping at 3 sigma until nothing more is getting clipped.
    """
    median = numpy.median(data)
    std = numpy.std(data)
    threshold = median + sigma * std

    mask = numpy.zeros(data.shape)
    while True:
        new_mask = numpy.zeros(data.shape)
        new_mask[data < threshold] = 1
        mask = numpy.logical_or(mask, new_mask)
        diff = numpy.logical_and(new_mask, numpy.logical_not(mask))
        if not diff.sum(): # stop if there are no new mask pixels
            break
    return mask

def rms(data, mask=None):
    """
    returns the RMS of an image, you can optionally supply a mask
    """
    if mask:
        data = data * mask
    n = data.sum()
    median = numpy.median(data)
    return math.sqrt(numpy.power(data-median, 2).sum()/n)

