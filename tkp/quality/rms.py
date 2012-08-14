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


def theoretical_max_rms():

    # Boltzmann constant
    k = 1.3806503 × 10-23

    # Ts0= 60 ± 20 K for Galactic latitudes between 10 and 90 degrees.
    T_s0 = 60

    T_sky = T_s0 * lamda ^ 2.55

    T_sys = T_sky + T_inst

    #System Equivalent Flux Density
    S_sys = (2 * n * k / A_eff) * T_sys