import tkp.quality
from tkp.utility import nice_format


def undersampled(semibmaj, semibmin):
    """
    We want more than 2 pixels across the beam major and minor axes.

    :param Semibmaj/semibmin: describe the beam size in pixels
    :returns: True if beam is undersampled, False otherwise
    """
    return semibmaj * 2 <= 1 or semibmin * 2 <= 1


def oversampled(semibmaj, semibmin, x=30):
    """
    It has been identified that having too many pixels across the restoring
    beam can lead to bad images, however further testing is required to
    determine the exact number.

    :param Semibmaj/semibmin: describe the beam size in pixels
    :returns: True if beam is oversampled, False otherwise
    """
    return semibmaj > x or semibmin > x


def highly_elliptical(semibmaj, semibmin, x=2.0):
    """
    If the beam is highly elliptical it can cause source association
    problems within TraP. Again further testing is required to determine
    exactly where the cut needs to be.

    :param Semibmaj/semibmin: describe the beam size in pixels
    :returns: True if the beam is highly elliptical, False otherwise
    """
    return semibmaj / semibmin > x


def not_full_fieldofview(nx, ny, cellsize, fov):
    """
    This has been raised as an interesting test, as if the full field of
    view (FOV) has not been imaged we may want to image the full dataset.
    The imaged FOV information can be estimated using the number of pixels
    and the size of the pixels.

    :param nx: number of pixels in x direction
    :param ny: number of pixels in y direction
    :returns: True if the full FOV is imaged, False otherwise
    """
    return nx * ny * (cellsize/3600) * (cellsize/3600) < fov


def infinite(smaj, smin, bpa):
    """
    If the beam is not correctly fitted by AWimager, one or more parameters
    will be recorded as infinite.

    :param smaj: Semi-major axis (arbitrary units)
    :param smin: Semi-minor axis
    :param bpa: Postion angle
    """
    return smaj == float('inf') or smin == float('inf') or bpa == float('inf')


def beam_invalid(semibmaj, semibmin, theta, oversampled_x=30, elliptical_x=2.0):
    """ Are the beam shape properties ok?

    :param semibmaj/semibmin: size of the beam in pixels

    :returns: True/False
    """

    formatted = "bmaj=%s and bmin=%s (pixels)" % (nice_format(semibmaj),
                                                 nice_format(semibmin))

    if tkp.quality.restoringbeam.infinite(semibmaj, semibmin, theta):
        return "Beam infinte. %s" % formatted
    if tkp.quality.restoringbeam.undersampled(semibmaj, semibmin):
        return "Beam undersampled. %s" % formatted
    elif tkp.quality.restoringbeam.oversampled(semibmaj, semibmin,
        oversampled_x):
        return "Beam oversampled. %s" % formatted
    elif tkp.quality.restoringbeam.highly_elliptical(semibmaj, semibmin, elliptical_x):
        return "Beam too elliptical. %s" % formatted

    #TODO: this test has been disabled untill antonia solves issue discribed in #3802
    #elif not tkp.quality.restoringbeam.full_fieldofview(nx, ny, cellsize, fov):
    #    return "Full field of view not imaged. Imaged FoV=XXdegrees, Observed FoV=XXdegrees"

    else:
        return False
