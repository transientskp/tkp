"""
functions for calculating statistical properties of LOFAR images
"""
import math
import numpy

def clip(data, sigma=3):
    """
    returns a mask for values above threshold defined by sigma from median
    iterative means keep clipping at 3 sigma until nothing more is getting clipped.
    """
    mask = numpy.zeros(data.shape, bool)
    new_mask = numpy.zeros(data.shape, bool)
    diff = numpy.zeros(data.shape, bool)
    while True:
        median = numpy.median(data[numpy.logical_not(mask)])
        std = numpy.std(data[numpy.logical_not(mask)])
        new_mask[:,:] = False
        new_mask[numpy.abs(data - median) > sigma * std] = True
        diff[:,:] = new_mask & numpy.logical_not(mask)
        mask[:,:] = numpy.logical_or(mask, new_mask)
        if not diff.any():
            break
    return mask

def rms(data, mask=None):
    """
    returns the RMS of an image, you can optionally supply a mask
    """
    if mask is not None:
        data = data[~mask]
    n = data.size
    median = numpy.median(data)
    return math.sqrt(numpy.ma.power(data - median, 2).sum()/n)

def john_rms(data):
    clipped_data = john_clip(data.ravel())
    clipped_data -= numpy.median(clipped_data)
    return numpy.sqrt(numpy.power(clipped_data, 2).sum()/len(clipped_data))

def john_clip(data, sigma=3):
    median = numpy.median(data)
    std = numpy.std(data)
    newdata = data[numpy.abs(data-median) <= sigma*std]
    if len(newdata) and len(newdata) != len(data):
        return john_clip(newdata, sigma)
    else:
        return newdata
