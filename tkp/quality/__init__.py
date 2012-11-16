"""
placeholder for all quality checking related code.

The quality checks are described in the "LOFAR Transients Key Science Project
Quality Control Document V1.1"

"""

import tkp.quality.restoringbeam


def nice_format(f):
    if f > 9999 or f < 0.01:
        return "%.2e" % f
    else:
        return "%.2f" % f


def rms_invalid(rms, noise, low_bound=1, high_bound=50):
    """ Is the RMS value of an image too high?
    Args:
        rms: RMS value of an image, can be computed with
             tkp.quality.statistics.rms
        noise: Theoretical noise level of instrument, can be calculated with
               tkp.lofar.noise.noise_level
        low_bound: multiplied with noise to define lower threshold
        high_bound: multiplied with noise to define upper threshold
    """
    if (rms < noise * low_bound) or (rms > noise * high_bound):
        ratio = rms / noise
        return "rms value (%s) is %s times theoretical noise (%s)" % \
                    (nice_format(rms), nice_format(ratio), nice_format(noise))
    else:
        return False


def beam_invalid(semibmaj, semibmin):
    """ Are the beam shape propperties ok?
    Args:
        semibmaj, semibmin: size of the beam in pixels
    """

    formatted = "semibmaj=%s and semibmin=%s" % (nice_format(semibmaj),
                                                 nice_format(semibmin))
    if tkp.quality.restoringbeam.undersampled(semibmaj, semibmin):
        return "Beam oversampled. %s" % formatted
    elif tkp.quality.restoringbeam.undersampled(semibmaj, semibmin):
        return "Beam undersampled. %s" % formatted
    elif tkp.quality.restoringbeam.highly_elliptical(semibmaj, semibmin):
        return "Beam too elliptical. %s" % formatted

    #TODO: this test has been disabled untill antonia solves issue discribed in #3802
    #elif not tkp.quality.restoringbeam.full_fieldofview(nx, ny, cellsize, fov):
    #    return "Full field of view not imaged. Imaged FoV=XXdegrees, Observed FoV=XXdegrees"

    else:
        return False