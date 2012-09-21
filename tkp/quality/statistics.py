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
    mask = numpy.zeros(data.shape, dtype=bool)
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
    b = numpy.median(data)
    if mask is not None:
        data = data * mask
        n = mask.sum()
        median = numpy.median(data)
        normalized = data - median
        normalized[normalized <= 0] = 0
        p = numpy.power(normalized, 2)
        o = p.sum()
        q = o/n
        return math.sqrt(q)
        #return math.sqrt(numpy.power(normalized, 2).sum()/n)
    else:
        n = len(data)
        median = numpy.median(data)
        normalized = data - median
        p = numpy.power(normalized, 2)
        o = p.sum()
        q = o/n
        return math.sqrt(q)
        # return math.sqrt(numpy.power(normalized, 2).sum()/n)


# probably correct stuff supplied by john below

def sigma_clip(data, sigma=3):
    """
    returns a mask for values above threshold defined by sigma from median
    iterative means keep clipping at 3 sigma until nothing more is getting clipped.
    """
    median = numpy.median(data)
    std = numpy.std(data)
    newdata = data[numpy.abs(data-median) <= sigma*std]
    if len(newdata) and len(newdata) != len(data):
        return sigma_clip(newdata, sigma)
    else:
        return newdata

def clipped_rms(data):
    clipped_data = sigma_clip(data.ravel())
    clipped_data -= numpy.median(clipped_data)
    return numpy.sqrt(numpy.power(clipped_data, 2).sum()/len(clipped_data))