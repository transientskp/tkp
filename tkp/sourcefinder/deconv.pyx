from libc.math cimport M_PI
from libc.math cimport cos
from libc.math cimport sin
from libc.math cimport atan
from libc.math cimport sqrt
from libc.math cimport fabs

def deconv(double fmaj, double fmin, double fpa, double cmaj, double cmin, double cpa):
    """
    Deconvolve a Gaussian "beam" from a Gaussian component.

    When we fit an elliptical Gaussian to a point in our image, we are
    actually fitting to a convolution of the physical shape of the source with
    the beam pattern of our instrument. This results in the fmaj/fmin/fpa
    arguments to this function.

    Since the shape of the (clean) beam (arguments cmaj/cmin/cpa) is known, we
    can deconvolve it from the fitted parameters to get the "real" underlying
    physical source shape, which is what this function returns.

    This code uses Cython for speed.

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
    cdef:
        double HALF_RAD = 90.0/M_PI
        double cmaj2 = cmaj * cmaj
        double cmin2 = cmin * cmin
        double fmaj2 = fmaj * fmaj
        double fmin2 = fmin * fmin
        double theta = (fpa - cpa) / HALF_RAD
        double det = ((fmaj2 + fmin2) - (cmaj2 + cmin2)) / 2.0
        double rhoc = (fmaj2 - fmin2) * cos(theta) - (cmaj2 - cmin2)
        double sigic2 = 0.0
        double rhoa = 0.0
        short ierr = 0

    if fabs(rhoc) > 0.0:
        sigic2 = atan((fmaj2 - fmin2) * sin(theta) / rhoc)
        rhoa = (((cmaj2 - cmin2) - (fmaj2 - fmin2) * cos(theta)) /
                (2.0 * cos(sigic2)))

    cdef:
        double rpa = sigic2 * HALF_RAD + cpa
        double rmaj = det - rhoa
        double rmin = det + rhoa

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
    if not fabs(rmaj):
        rpa = 0.0
    elif not fabs(rmin) and (45.0 < fabs(rpa-fpa) < 135.0):
            rpa = (rpa + 450.0) % 180.0

    return rmaj, rmin, rpa, ierr
