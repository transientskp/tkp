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


def theoretical_max_rms(frequency, bandwidth, integration_time):
    """
    calculates the maximum possible RMS value as described here:

    http://www.astron.nl/radio-observatory/astronomers/lofar-imaging-capabilities-sensitivity/sensitivity-lofar-array/sensiti
    """

    wavelength = scipy.constants.c/frequency

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

    # the total collecting area
    A_eff = 1 # ?

    #System Equivalent Flux Density
    S_sys = (2 * n * scipy.constants.k / A_eff) * T_sys

    # distance to nearest dipole within the full array
    d =  0 # ?

    # Lower limit for the effective area
    if wavelength > 3:
         # LBA dipole
        A_eff_dipole = min(pow(wavelength, 2) / 3, (math.pi * power(d, 2)) / 4)
    else:
        # HBA dipole
        A_eff_dipole = min(pow(wavelength, 2) / 3, 1.5625)

    # The sensitivity D_S (in Jy) of a single dipole (or half an 'antenna')
    #D_S_dipole = S_sys_dipole / (math.sqrt(2 * bandwidth, integration_time))

    # An antenna that consists of two (equal) dipoles placed perpendicular to eac
    #D_S_antenna = D_S_dipole / math.sqrt(2)

    # For one station, the overlap in effective area from different dipoles has to be taken into account.
    #D_S_station = S_sys_station / (math.sqrt(2 * bandwith, integration_time))

    # SEFD for core stations
    S_core = (2 * n * scipy.constants.k / A_eff) * T_sys # ?

    # SEFD for remote stations
    S_remote = (2 * n * scipy.constants.k / A_eff) * T_sys # ?

    # a factor for increase of noise due to the weighting scheme (which depends on the type of weighting: natural, uniform, robust, ...)
    W = 0 # ?

    # Number of core stations
    Nc = 36 # ?

    # Number of remote stations
    Nr = 8 # ?

    # The noise level in a LOFAR image
    t1 = (Nc * (Nc - 1) / 2) / pow(S_core, 2)
    t2 = (Nc * Nr) / (S_core * S_remote)
    t3 = (Nr * (Nr - 1) / 2) / pow(S_remote, 2)
    D_S = W / (math.sqrt(2 * 2 * bandwidth * integration_time * (t1 + t2 + t3)))
