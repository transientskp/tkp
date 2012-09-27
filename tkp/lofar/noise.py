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


def noise_level(frequency, subbandwidth, intgr_time, configuration, subbands=1, channels=64, Ncore=24, Nremote=16, Nintl=8):
    """ Returns the theoretical noise level given the supplied array configuration

    Args:
        subbandwidth: in Hz (should be 144042.96875 (144 kHz) or 180053.7109375 (180 kHz))
        intgr_time: in seconds
        inner: in case of LBA, inner or outer
        configuration: LBA_INNER, LBA_OUTER, LBA_SPARSE, LBA or HBA
    """
    bandwidth = subbandwidth * subbands
    channelwidth = subbandwidth / channels

    if configuration.startswith("LBA"):
        ds = tkp.lofar.antennaarrays.dipole_distances[configuration]
        Aeff = sum([tkp.lofar.noise.Aeff_dipole(frequency, x) for x in ds])
    else:
        # todo: check if this is correct. There are 16 antennae per tile. There are 24 tiles per core station
        Aeff = 16 * 24 * tkp.lofar.noise.Aeff_dipole(frequency)

    Ssys = system_sensitivity(frequency, Aeff)

    baselines_core = (Ncore * (Ncore - 1)) / 2
    baselines_remote = (Nremote * (Nremote - 1)) / 2
    baselines_intl = (Nintl * (Nintl - 1)) / 2
    baselines_cr = (Ncore * Nremote)
    baselines_ci = (Ncore * Nintl)
    baselines_ri = (Nremote * Nintl)

    # todo: not sure if this is correct
    SEFD_core = Ssys
    SEFD_remote = Ssys
    SEFD_intl = Ssys

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

    # TODO: do we need this?
    #channel_sens = W / math.sqrt(4 * channelwidth * intgr_time * ( t_core + t_remote + t_intl + t_cr + t_ci + t_ri))

    return image_sens

def Aeff_dipole(frequency, distance=None):
    """The effective area of each dipole in the array is determined by its distance to the nearest dipole (d)
    within the full array. Distance is distance to nearest dipole, only required for LBA.
    """
    wavelength = scipy.constants.c/frequency
    if wavelength > 3: # LBA dipole
        return min(pow(wavelength, 2) / 3, (math.pi * pow(distance, 2)) / 4)
    else: # HBA dipole
        return min(pow(wavelength, 2) / 3, 1.5625)

def system_sensitivity(frequency, Aeff):
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

    # SEFD or system sensitivity
    S = (2 * n * scipy.constants.k / Aeff) * Tsys

    return S

def delta_sensitivity(Ssys_dipole,Ssys_station, bandwidth, intgr_time):

    # The sensitivity DS (in Jy) of a single dipole (or half an 'antenna')
    DS_dipole = Ssys_dipole / (math.sqrt(2 * bandwidth, intgr_time))

    # An antenna that consists of two (equal) dipoles placed perpendicular to eac
    DS_antenna = DS_dipole / math.sqrt(2)

    # For one station, the overlap in effective area from different dipoles has to be taken into account.
    DS_station = Ssys_station / (math.sqrt(2 * bandwidth, intgr_time))

