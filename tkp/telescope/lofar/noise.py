"""
functions for calculating theoretical noise levels of LOFAR equipment.

For more information about the math used here read the `sensitivity of the
LOFAR array page
<http://www.astron.nl/radio-observatory/astronomers/lofar-imaging-capabilities-sensitivity/sensitivity-lofar-array/sensiti>`_.

To check the values calculated here one can use this `LOFAR image noise
calculator <http://www.astron.nl/~heald/test/sens.php>`_.

"""
import math
import logging
import warnings
import scipy.constants
import scipy.interpolate

from tkp.telescope.lofar import antennaarrays


logger = logging.getLogger(__name__)

ANTENNAE_PER_TILE = 16
TILES_PER_CORE_STATION = 24
TILES_PER_REMOTE_STATION = 48
TILES_PER_INTL_STATION = 96


def noise_level(freq_eff, bandwidth, tau_time, antenna_set, Ncore, Nremote,
                Nintl):
    """
    Returns the theoretical noise level (in Jy) given the supplied array
    antenna_set.

    :param bandwidth: in Hz
    :param tau_time: in seconds
    :param inner: in case of LBA, inner or outer
    :param antenna_set: LBA_INNER, LBA_OUTER, LBA_SPARSE, LBA or HBA
    """
    if antenna_set.startswith("LBA"):
        ds_core = antennaarrays.core_dipole_distances[antenna_set]
        Aeff_core = sum([Aeff_dipole(freq_eff, x) for x in ds_core])
        ds_remote = antennaarrays.remote_dipole_distances[antenna_set]
        Aeff_remote = sum([Aeff_dipole(freq_eff, x) for x in ds_remote])
        ds_intl = antennaarrays.intl_dipole_distances[antenna_set]
        Aeff_intl = sum([Aeff_dipole(freq_eff, x) for x in ds_intl])
    else:
        Aeff_core = ANTENNAE_PER_TILE * TILES_PER_CORE_STATION * \
                                                        Aeff_dipole(freq_eff)
        Aeff_remote = ANTENNAE_PER_TILE * TILES_PER_REMOTE_STATION * \
                                                        Aeff_dipole(freq_eff)
        Aeff_intl = ANTENNAE_PER_TILE * TILES_PER_INTL_STATION * \
                                                        Aeff_dipole(freq_eff)

    # c = core, r = remote, i = international
    # so for example cc is core-core baseline
    Ssys_c = system_sensitivity(freq_eff, Aeff_core)
    Ssys_r = system_sensitivity(freq_eff, Aeff_remote)
    Ssys_i = system_sensitivity(freq_eff, Aeff_intl)

    baselines_cc = (Ncore * (Ncore - 1)) / 2
    baselines_rr = (Nremote * (Nremote - 1)) / 2
    baselines_ii = (Nintl * (Nintl - 1)) / 2
    baselines_cr = (Ncore * Nremote)
    baselines_ci = (Ncore * Nintl)
    baselines_ri = (Nremote * Nintl)

    #baselines_total = baselines_cc + baselines_rr + baselines_ii +\
    #                    baselines_cr + baselines_ci + baselines_ri

    # baseline noise, for example cc is core-core
    temp_cc = Ssys_c
    temp_rr = Ssys_r
    temp_ii = Ssys_i

    #temp_cr = math.sqrt(SEFD_cc) * math.sqrt(SEFD_rr)
    #temp_ci = math.sqrt(SEFD_cc) * math.sqrt(SEFD_ii)
    #temp_ri = math.sqrt(SEFD_rr) * math.sqrt(SEFD_ii)

    # The noise level in a LOFAR image
    t_cc = baselines_cc / (temp_cc * temp_cc)
    t_rr = baselines_rr / (temp_rr * temp_cc)
    t_ii = baselines_ii / (temp_ii * temp_ii)
    t_cr = baselines_cr / (temp_cc * temp_rr)
    t_ci = baselines_ci / (temp_cc * temp_ii)
    t_ri = baselines_ri / (temp_rr * temp_ii)

    # factor for increase of noise due to the weighting scheme
    W = 1  # taken from PHP script

    image_sens = W / math.sqrt(4 * bandwidth * tau_time *
                               (t_cc + t_rr + t_ii + t_cr + t_ci + t_ri))

    return image_sens


def Aeff_dipole(freq_eff, distance=None):
    """
    The effective area of each dipole in the array is determined by its
    distance to the nearest dipole (d) within the full array.

    :param freq_eff: Frequency
    :param distance: Distance to nearest dipole, only required for LBA.
    """
    wavelength = scipy.constants.c/freq_eff
    if wavelength > 3:  # LBA dipole
        if not distance:
            msg = "Distance to nearest dipole required for LBA noise calculation"
            logger.error(msg)
            warnings.warn(msg)
            distance = 1
        return min(pow(wavelength, 2) / 3, (math.pi * pow(distance, 2)) / 4)
    else: # HBA dipole
        return min(pow(wavelength, 2) / 3, 1.5625)


def system_sensitivity(freq_eff, Aeff):
    """
    Returns the SEFD of a system, given the freq_eff and effective
    collecting area. Returns SEFD in Jansky's.
    """
    wavelength = scipy.constants.c / freq_eff

    # Ts0 = 60 +/- 20 K for Galactic latitudes between 10 and 90 degrees.
    Ts0 = 60

    # system efficiency factor (~ 1.0)
    n = 1

    # For all LOFAR frequencies the sky brightness temperature is dominated by
    # the Galactic radiation, which depends strongly on the wavelength
    Tsky = Ts0 * wavelength ** 2.55

    #The instrumental noise temperature follows from measurements or simulations
    # This is a quick & dirty approach based roughly on Fig 5 here
    #  <http://www.skatelescope.org/uploaded/59513_113_Memo_Nijboer.pdf>
    sensitivities = [
        (0, 0),
        (10e6, 0.1 * Tsky),
        (40e6, 0.7 * Tsky),
        (50e6, 0.85 * Tsky),
        (55e6, 0.9 * Tsky),
        (60e6, 0.85 * Tsky),
        (70e6, 0.6 * Tsky),
        (80e6, 0.3 * Tsky),
        (90e6, 0 * Tsky),
        (110e6, 0 * Tsky),
        (120e6, 200),
        (300e6, 200)
    ]
    x, y = zip(*sensitivities)
    sensitivity = scipy.interpolate.interp1d(x, y, kind='linear')
    Tinst = sensitivity(freq_eff)

    Tsys = Tsky + Tinst

    # SEFD or system sensitivity
    S = (2 * n * scipy.constants.k / Aeff) * Tsys

    # S is in Watts per square metre per Hertz.  One Jansky = 10**-26 Watts/sq
    # metre/Hz
    return S * 10**26
