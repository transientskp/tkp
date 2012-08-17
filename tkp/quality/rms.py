__author__ = 'gijs'

import math
import numpy
import scipy.constants
import scipy.interpolate


SEFDcore_LBA_inner = {
    15 : 2783900,
    30 : 211270,
    45 : 47560,
    60 : 31600,
    75 : 50950,
}

SEFDcore_LBA_outer = {
    15 : 480170,
    30 : 88760,
    45 : 38160,
    60 : 29590,
    75 : 49330,
}

SEFDcore_HBA = {
    120 : 3570,
    150 : 2820,
    180 : 3230,
    200 : 3520,
    210 : 3660,
    240 : 4060,
}

SEFDremote_LBA_inner = {
    15 : 2783900,
    30 : 211270,
    45 : 47560,
    60 : 31600,
    75 : 50950,
}

SEFDremote_LBA_outer = {
    15 : 480170,
    30 : 88760,
    45 : 38160,
    60 : 29590,
    75 : 49330,
}

SEFDremote_HBA = {
    120 : 1790,
    150 : 1410,
    180 : 1620,
    200 : 1760,
    210 : 1830,
    240 : 2030,
}

SEFDintl_LBA_inner = {
    15 : 518740,
    30 : 40820,
    45 : 18840,
    60 : 14760,
    75 : 24660,
}

SEFDintl_LBA_outer = {
    15 : 518740,
    30 : 40820,
    45 : 18840,
    60 : 14760,
    75 : 24660
}

SEFDintl_HBA = {
    120 : 890,
    150 : 710,
    180 : 810,
    200 : 880,
    210 : 920,
    240 : 1020,
}


def interpolate(SEFD_dict, frequency):
    """interpolates between frequencies defined in SEFD dicts above"""
    items = SEFD_dict.items()
    items.sort(key=lambda tup: tup[0])
    freq, Aeff = zip(*items)
    freq = [x * 10**6 for x in freq]
    i = scipy.interpolate.interp1d(freq, Aeff)
    return i(frequency)


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


def SEFD(frequency, inner):
    """
    returns a tuple of SEFD's for core, remote and intl
    """
    if frequency > 100:
        SEFD_core = interpolate(SEFDcore_HBA, frequency)
    elif inner:
        SEFD_core = interpolate(SEFDcore_LBA_inner, frequency)
    else:
        SEFD_core = interpolate(SEFDcore_LBA_outer, frequency)

    if frequency > 100:
        SEFD_remote = interpolate(SEFDremote_HBA, frequency)
    elif inner:
        SEFD_remote = interpolate(SEFDremote_LBA_inner, frequency)
    else:
        SEFD_remote = interpolate(SEFDremote_LBA_outer, frequency)

    if frequency > 100:
        SEFD_intl = interpolate(SEFDintl_HBA, frequency)
    elif inner:
        SEFD_intl = interpolate(SEFDintl_LBA_inner, frequency)
    else:
        SEFD_intl = interpolate(SEFDintl_LBA_outer, frequency)

    return SEFD_core, SEFD_remote, SEFD_intl


def noise_level(frequency, subbandwidth, intgr_time, subbands=1, channels=64, Ncore=24, Nremote=16, Nintl=8, inner=True):
    """
    bandwidth - in Hz (should be 144042.96875 (144 kHz) or 180053.7109375 (180 kHz))
    intgr_time - in seconds
    inner - in case of LBA, inner or outer
    """
    bandwidth = subbandwidth * subbands
    channelwidth = subbandwidth / channels

    baselines_core = (Ncore * (Ncore - 1)) / 2
    baselines_remote = (Nremote * (Nremote - 1)) / 2
    baselines_intl = (Nintl * (Nintl - 1)) / 2
    baselines_cr = (Ncore * Nremote)
    baselines_ci = (Ncore * Nintl)
    baselines_ri = (Nremote * Nintl)

    SEFD_core, SEFD_remote, SEFD_intl = SEFD(frequency, inner)

    SEFD_cr = math.sqrt(SEFD_core) * math.sqrt(SEFD_remote)
    SEFD_ci = math.sqrt(SEFD_core) * math.sqrt(SEFD_intl)
    SEFD_ri = math.sqrt(SEFD_remote) * math.sqrt(SEFD_intl)

    # factor for increase of noise due to the weighting scheme
    W = 1 # taken from PHP script

    t_core = baselines_core / pow(SEFD_core, 2)
    t_remote = baselines_remote / pow(SEFD_remote, 2)
    t_intl = baselines_intl / pow(SEFD_intl, 2)
    t_cr = baselines_cr / pow(SEFD_cr, 2)
    t_ci = baselines_ci / pow(SEFD_ci, 2)
    t_ri = baselines_ri / pow(SEFD_ri, 2)

    # The noise level in a LOFAR image
    image_sens = W / math.sqrt(4 * bandwidth * intgr_time * ( t_core + t_remote + t_intl + t_cr + t_ci + t_ri))
    channel_sens = W / math.sqrt(4 * channelwidth * intgr_time * ( t_core + t_remote + t_intl + t_cr + t_ci + t_ri))
    return image_sens


def Aeff_dipole(wavelength, distance):
    if wavelength > 3:
    # LBA dipole
        Aeff_dipole = min(pow(wavelength, 2) / 3, (math.pi * power(distance, 2)) / 4)
    else:
        # HBA dipole
        Aeff_dipole = min(pow(wavelength, 2) / 3, 1.5625)


def system_sensitivity(frequency, bandwidth, intgr_time, channels, inner=True, Ncore=24, Nremote = 16):
    wavelength = scipy.constants.c/frequency

    # Ts0 = 60 +/- 20 K for Galactic latitudes between 10 and 90 degrees.
    Ts0 = 60

    # system efficiency factor (~ 1.0)
    n = 1


    # For all LOFAR frequencies the sky brightness temperature is dominated by the Galactic radiation, which depends
    # strongly on the wavelength
    Tsky = Ts0 * wavelength ** 2.55

    #The instrumental noise temperature follows from measurements or simulations
    Tinst = 1 # ?

    Tsys = Tsky + Tinst

    # the total collecting area
    Aeff = 1 # ?

    # The sensitivity DS (in Jy) of a single dipole (or half an 'antenna')
    DS_dipole = Ssys_dipole / (math.sqrt(2 * bandwidth, intgr_time))

    # An antenna that consists of two (equal) dipoles placed perpendicular to eac
    DS_antenna = DS_dipole / math.sqrt(2)

    # For one station, the overlap in effective area from different dipoles has to be taken into account.
    DS_station = Ssys_station / (math.sqrt(2 * bandwith, intgr_time))

    # SEFD or system sensitivity
    S = (2 * n * scipy.constants.k / Aeff) * Tsys

    return S


