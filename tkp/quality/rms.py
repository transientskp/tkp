__author__ = 'gijs'

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

    Kwargs:

        data (2D numpy.ndarray): actual image data

    Returns:

        (float): RMS value of image
    """
    return math.sqrt(numpy.power(data, 2).sum())
