"""
functions for calculating statistical properties of LOFAR images
"""
import numpy

def rms(data):
    """
    returns the clipped RMS of an image
    """
    clipped_data = clip(data.ravel())
    clipped_data -= numpy.median(clipped_data)
    return numpy.sqrt(numpy.power(clipped_data, 2).sum()/len(clipped_data))

def clip(data, sigma=3):
    """
    remove all values above a threshold from the array
    uses iterative clipping at sigma value until nothing more is getting clipped.
    """
    median = numpy.median(data)
    std = numpy.std(data)
    newdata = data[numpy.abs(data-median) <= sigma*std]
    if len(newdata) and len(newdata) != len(data):
        return clip(newdata, sigma)
    else:
        return newdata

def clip_mask(data, sigma=3):
    """
    returns a mask for values above threshold defined by sigma from median
    uses iterative clipping at sigma value until nothing more is getting clipped.
    """
    mask = numpy.zeros(data.shape, bool)
    new_mask = numpy.zeros(data.shape, bool)
    masked = data
    while True:
        median = numpy.median(masked)
        std = numpy.std(masked)
        new_mask[numpy.abs(data - median) > sigma * std] = True
        diff = new_mask & ~mask
        mask = mask | new_mask
        if not diff.any():
            return mask
        masked = data[~mask]
        new_mask[:,:] = False
