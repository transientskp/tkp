"""
functions for calculating statistical properties of LOFAR images
"""
import numpy

def rms(data):
    """returns the clipped RMS of an image
    Args:
        data: a numpy array
    """
    clipped_data = clip(data.ravel())
    clipped_data -= numpy.median(clipped_data)
    return numpy.sqrt(numpy.power(clipped_data, 2).sum()/len(clipped_data))

def clip(data, sigma=3):
    """remove all values above a threshold from the array.
    uses iterative clipping at sigma value until nothing more is getting clipped.
    Args:
        data: a numpy array
    """
    median = numpy.median(data)
    std = numpy.std(data)
    newdata = data[numpy.abs(data-median) <= sigma*std]
    if len(newdata) and len(newdata) != len(data):
        return clip(newdata, sigma)
    else:
        return newdata

def subregion(data, f=4):
    """returns the inner region of a image, according to f.
    if f is for example 4, the returned region will be 1/4th of the total.
    Args:
        data: a numpy array
    """
    x,y = data.shape
    return data[(x/2 - x/f):(x/2 + x/f), (y/2 - y/f):(y/2 + y/f)]
