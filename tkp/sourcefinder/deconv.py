"""
Gaussian deconvolution.
"""

from math import sin, cos, atan, sqrt, pi

def deconv(fmaj, fmin, fpa, cmaj, cmin, cpa):
    """
    Deconvolve a Gaussian "beam" from a Gaussian component.

    When we fit an elliptical Gaussian to a point in our image, we are
    actually fitting to a convolution of the physical shape of the source with
    the beam pattern of our instrument. This results in the fmaj/fmin/fpa
    arguments to this function.

    Since the shape of the (clean) beam (arguments cmaj/cmin/cpa) is known, we
    can deconvolve it from the fitted parameters to get the "real" underlying
    physical source shape, which is what this function returns.

    Args:
        fmaj (float): Fitted major axis
        fmin (float): Fitted minor axis
        fpa (float):  Fitted position angle of major axis
        cmaj (float): Clean beam major axis
        cmin (float): Clean beam minor axis
        cpa (float):  Clean beam position angle of major axis

    Returns:
        rmaj (float): Real major axis
        rmin (float): Real minor axis
        rpa (float):  Real position angle of major axis
        ierr (int):   Number of components which failed to deconvolve
    """
    HALF_RAD = 90.0 / pi
    cmaj2 = cmaj * cmaj
    cmin2 = cmin * cmin
    fmaj2 = fmaj * fmaj
    fmin2 = fmin * fmin
    theta = (fpa - cpa) / HALF_RAD
    det = ((fmaj2 + fmin2) - (cmaj2 + cmin2)) / 2.0
    rhoc = (fmaj2 - fmin2) * cos(theta) - (cmaj2 - cmin2)
    sigic2 = 0.0
    rhoa = 0.0
    ierr = 0

    if abs(rhoc) > 0.0:
        sigic2 = atan((fmaj2 - fmin2) * sin(theta) / rhoc)
        rhoa = (((cmaj2 - cmin2) - (fmaj2 - fmin2) * cos(theta)) /
                (2.0 * cos(sigic2)))

    rpa = sigic2 * HALF_RAD + cpa
    rmaj = det - rhoa
    rmin = det + rhoa

    if rmaj < 0:
        ierr += 1
        rmaj = 0
    if rmin < 0:
        ierr += 1
        rmin = 0

    rmaj = sqrt(rmaj)
    rmin = sqrt(rmin)
    if rmaj < rmin:
        rmaj, rmin = rmin, rmaj
        rpa += 90

    rpa = (rpa + 900) % 180
    if not abs(rmaj):
        rpa = 0.0
    elif not abs(rmin) and (45.0 < abs(rpa-fpa) < 135.0):
        rpa = (rpa + 450.0) % 180.0

    return rmaj, rmin, rpa, ierr
