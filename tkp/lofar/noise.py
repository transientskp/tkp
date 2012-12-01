"""
functions for calculating theoretical noise levels of LOFAR equipment

more info:
http://www.astron.nl/radio-observatory/astronomers/lofar-imaging-capabilities-sensitivity/sensitivity-lofar-array/sensiti
"""
import os
import math
import scipy.constants
import scipy.interpolate
import tkp
import tkp.lofar.antennaarrays


def noise_level(freqeff, subbandwidth, intgr_time, antenna_set, subbands=1, channels=64, Ncore=24, Nremote=16, Nintl=8):
    """ Returns the theoretical noise level given the supplied array antenna_set

    Args:
        subbandwidth: in Hz (should be 144042.96875 (144 kHz) or 180053.7109375 (180 kHz))
        intgr_time: in seconds
        inner: in case of LBA, inner or outer
        antenna_set: LBA_INNER, LBA_OUTER, LBA_SPARSE, LBA or HBA
    """
    bandwidth = subbandwidth * subbands

    if antenna_set.startswith("LBA"):
        ds_core = tkp.lofar.antennaarrays.core_dipole_distances[antenna_set]
        Aeff_core = sum([tkp.lofar.noise.Aeff_dipole(freqeff, x) for x in ds_core])
        ds_remote = tkp.lofar.antennaarrays.remote_dipole_distances[antenna_set]
        Aeff_remote = sum([tkp.lofar.noise.Aeff_dipole(freqeff, x) for x in ds_remote])
        ds_intl = tkp.lofar.antennaarrays.intl_dipole_distances[antenna_set]
        Aeff_intl = sum([tkp.lofar.noise.Aeff_dipole(freqeff, x) for x in ds_intl])
    else:
        # todo: check if this is correct. There are 16 antennae per tile. There are 24 tiles per core station
        Aeff_core = 16 * 24 * tkp.lofar.noise.Aeff_dipole(freqeff)
        Aeff_remote = 16 * 24 * tkp.lofar.noise.Aeff_dipole(freqeff)
        Aeff_intl = 16 * 24 * tkp.lofar.noise.Aeff_dipole(freqeff)

    # c = core, r = remote, i = international. So for example cc is core-core baseline
    Ssys_cc = system_sensitivity(freqeff, Aeff_core)
    Ssys_rr = system_sensitivity(freqeff, Aeff_remote)
    Ssys_ii = system_sensitivity(freqeff, Aeff_intl)

    SEFD_cc = Ssys_cc
    SEFD_rr = Ssys_rr
    SEFD_ii = Ssys_ii

    SEFD_cr = math.sqrt(SEFD_cc) * math.sqrt(SEFD_rr)
    SEFD_ci = math.sqrt(SEFD_cc) * math.sqrt(SEFD_ii)
    SEFD_ri = math.sqrt(SEFD_rr) * math.sqrt(SEFD_ii)

    baselines_cc = (Ncore * (Ncore - 1)) / 2
    baselines_rr = (Nremote * (Nremote - 1)) / 2
    baselines_ii = (Nintl * (Nintl - 1)) / 2
    baselines_cr = (Ncore * Nremote)
    baselines_ci = (Ncore * Nintl)
    baselines_ri = (Nremote * Nintl)
    baselines_total = baselines_cc + baselines_rr + baselines_ii + baselines_cr + baselines_ci + baselines_ri

    # factor for increase of noise due to the weighting scheme
    W = 1 # taken from PHP script

    # The noise level in a LOFAR image
    t_cc = baselines_cc / pow(SEFD_cc, 2)
    t_rr = baselines_rr / pow(SEFD_rr, 2)
    t_ii = baselines_ii / pow(SEFD_ii, 2)
    t_cr = baselines_cr / pow(SEFD_cr, 2)
    t_ci = baselines_ci / pow(SEFD_ci, 2)
    t_ri = baselines_ri / pow(SEFD_ri, 2)

    image_sens = W / math.sqrt(4 * bandwidth * intgr_time * ( t_cc + t_rr + t_ii + t_cr + t_ci + t_ri))

    #channelwidth = subbandwidth / channels
    #channel_sens = W / math.sqrt(4 * channelwidth * intgr_time * ( t_cc + t_rr + t_ii + t_cr + t_ci + t_ri))

    return image_sens


def Aeff_dipole(freqeff, distance=None):
    """The effective area of each dipole in the array is determined by its distance to the nearest dipole (d)
    within the full array. Distance is distance to nearest dipole, only required for LBA.
    """
    wavelength = scipy.constants.c/freqeff
    if wavelength > 3: # LBA dipole
        return min(pow(wavelength, 2) / 3, (math.pi * pow(distance, 2)) / 4)
    else: # HBA dipole
        return min(pow(wavelength, 2) / 3, 1.5625)


def system_sensitivity(freqeff, Aeff):
    """ Returns the SEFD of a system, given the freqeff and effective collecting area. Returns SEFD in Jansky's.
    """
    wavelength = scipy.constants.c/freqeff

    # Ts0 = 60 +/- 20 K for Galactic latitudes between 10 and 90 degrees.
    Ts0 = 60

    # system efficiency factor (~ 1.0)
    n = 1

    # For all LOFAR frequencies the sky brightness temperature is dominated by the Galactic radiation, which depends
    # strongly on the wavelength
    Tsky = Ts0 * wavelength ** 2.55

    #The instrumental noise temperature follows from measurements or simulations
    # TODO: we can try to mimic the results in Fig 5 here http://www.skatelescope.org/uploaded/59513_113_Memo_Nijboer.pdf
    Tinst = 1 # ?

    Tsys = Tsky + Tinst

    # SEFD or system sensitivity
    S = (2 * n * scipy.constants.k / Aeff) * Tsys

    # S is in Watts per square metre per Hertz.  One Jansky = 10**-26 Watts/sq metre/Hz
    return S * 10**26
