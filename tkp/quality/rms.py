__author__ = 'gijs'

import math
import numpy
import scipy.constants

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


def wavelength(frequency):
    return scipy.constants.c/frequency


def frequency(wavelength):
    return scipy.constants.c/wavelength


def theoretical_max_rms(wavelength, bandwith, integration_time):
    # Boltzmann constant
    k = scipy.constants.k

    # T_s0 = 60 +/- 20 K for Galactic latitudes between 10 and 90 degrees.
    T_s0 = 60

    # For all LOFAR frequencies the sky brightness temperature is dominated by the Galactic radiation, which depends
    # strongly on the wavelength
    T_sky = T_s0 * wavelength ** 2.55

    #The instrumental noise temperature follows from measurements or simulations
    T_inst = 0 # ?

    T_sys = T_sky + T_inst

    # system efficiency factor (~ 1.0)
    n = 1

    #System Equivalent Flux Density
    S_sys = (2 * n * k / A_eff) * T_sys

    # distance to nearest dipole within the full array
    d =  0 # ?

    # Lower limit for the effective area for an LBA dipole
    A_eff_dipole = min(power(wavelength, 2) / 3, (math.pi * power(d, 2)) / 4)

    # Lower limit for the effective area for an LBA dipole
    A_eff_dipole = min(power(wavelength, 2) / 3, 1.5625)

    # The sensitivity D_S (in Jy) of a single dipole (or half an 'antenna')
    D_S_dipole = S_sys_dipole / (math.sqrt(2 * bandwith, integration_time))

    # An antenna that consists of two (equal) dipoles placed perpendicular to eac
    D_S_antenna = D_S_dipole / math.sqrt(2)

