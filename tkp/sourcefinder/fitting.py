# -*- coding: utf-8 -*-
#
# LOFAR Transients Key Project
#
# Hanno Spreeuw
#
# discovery@transientskp.org
#
#
# Source fitting algorithms
#

import math
import numpy
import scipy.optimize
from .gaussian import gaussian
from ..utility.uncertain import Uncertain
import utils


FIT_PARAMS = ('peak', 'xbar', 'ybar', 'semimajor', 'semiminor', 'theta')


def moments(data, beam, threshold=0):
    """Calculate source positional values using moments

    Args:

        data (numpy.ndarray): Actual 2D image data

        beam (3-tuple): beam (psf) information, with semi-major and
            semi-minor axes

    Returns:

        (dict): peak, total, x barycenter, y barycenter, semimajor
            axis, semiminor axis, theta

    Raises:

        ValueError (in case of NaN in input)

    Use the first moment of the distribution is the barycenter of an
    ellipse. The second moments are used to estimate the rotation angle
    and the length of the axes.
    """

    # Are we fitting a -ve or +ve Gaussian?
    if data.mean() >= 0:
        # The peak is always underestimated when you take the highest pixel.
        peak = data.max() * utils.fudge_max_pix(beam[0], beam[1], beam[2])
    else:
        peak = data.min()
    ratio = threshold / peak
    total = data.sum()
    x, y = numpy.indices(data.shape)
    xbar = float((x * data).sum()/total)
    ybar = float((y * data).sum()/total)
    xxbar = (x * x * data).sum()/total - xbar**2
    yybar = (y * y * data).sum()/total - ybar**2
    xybar = (x * y * data).sum()/total - xbar * ybar

    working1 = (xxbar + yybar) / 2.0
    working2 = math.sqrt(((xxbar - yybar)/2)**2 + xybar**2)
    beamsize = utils.calculate_beamsize(beam[0], beam[1])

    # Some problems arise with the sqrt of (working1-working2) when they are
    # equal, this happens with islands that have a thickness of only one pixel
    # in at least one dimension.  Due to rounding errors this difference
    # becomes negative--->math domain error in sqrt.
    if len(data.nonzero()[0]) == 1:
        # This is the case when the island (or more likely subisland) has
        # a size of only one pixel.
        semiminor = numpy.sqrt(beamsize/numpy.pi)
        semimajor = numpy.sqrt(beamsize/numpy.pi)
    else:
        semimajor_tmp = (working1 + working2) * 2.0 * math.log(2.0)
        semiminor_tmp = (working1 - working2) * 2.0 * math.log(2.0)
        # ratio will be 0 for data that hasn't been selected according to a
        # threshold.
        if ratio != 0:
            # The corrections below for the semi-major and semi-minor axes are
            # to compensate for the underestimate of these quantities
            # due to the cutoff at the threshold.
            semimajor_tmp /= (1.0 + math.log(ratio) * ratio / (1.0 - ratio))
            semiminor_tmp /= (1.0 + math.log(ratio) * ratio / (1.0 - ratio))
        semimajor = math.sqrt(semimajor_tmp)
        semiminor = math.sqrt(semiminor_tmp)
        if semiminor == 0:
            # A semi-minor axis exactly zero gives all kinds of problems.
            # For instance wrt conversion to celestial coordinates.
            # This is a quick fix.
            semiminor = beamsize / (numpy.pi * semimajor)

    if (numpy.isnan(xbar) or numpy.isnan(ybar) or
        numpy.isnan(semimajor) or numpy.isnan(semiminor)):
        raise ValueError("Unable to estimate Gauss shape")

    # Not sure if theta is affected in any way by the cutoff at the threshold.
    if abs(semimajor - semiminor) < 0.01:
        # short circuit!
        theta = 0.
    else:
        theta = math.atan(2. * xybar / (xxbar - yybar))/2.
        if theta * xybar > 0.:
            if theta < 0.:
                theta += math.pi / 2.0
            else:
                theta -= math.pi / 2.0

    ## NB: a dict should give us a bit more flexibility about arguments;
    ## however, all those here are ***REQUIRED***.
    return {
        "peak": peak,
        "flux": total,
        "xbar": xbar,
        "ybar": ybar,
        "semimajor": semimajor,
        "semiminor": semiminor,
        "theta": theta
        }


def fitgaussian(data, params, fixed=None):
    """
    Calculate source positional values by fitting a 2D Gaussian

    Args:

        data (numpy.ndarray): Actual 2D data

        params (dict): initial fit parameters (possibly estimated
            using the moments function)

    Kwargs:

        fixed (dict): parameters to be kept frozen (ie, not fitted)

    Returns:

        (dict): peak, x barycenter, y barycenter, semimajor, semiminor, theta

    Raises:

        ValueError (in case of a bad fit)

    Perform a least squares fit to an elliptical Gaussian.

    If a dict called fixed is passed in, then parameters specified within the
    dict with the same names as fit_params (below) will be "locked" in the
    fitting process.
    """
    bounds=[
        (None, None), # Peak
        (None, None), # xbar
        (None, None), # ybar
        (0, None),    # semimajor
        (0, None),    # semiminor
        (None, None)  # theta
    ]

    initial = []
    for key in FIT_PARAMS:
        if hasattr(params[key], "value"):
            initial.append(params[key].value)
        else:
            initial.append(params[key])

    for key, value in fixed.iteritems():
        if key not in FIT_PARAMS:
            raise ValueError("Fixed parameter %s not recognized" % key)
        index = FIT_PARAMS.index(key)
        try:
            iter(value)
            # value is a range
            bounds[index] = (value[0], value[1])
        except TypeError:
            # value is a single parameter
            bounds[index] = (value, value)

    def errorfunction(paramlist):
        # Returns the sum of the squares of the difference between a gaussian
        # parameterized by paramlist and our data.
        g = (gaussian(*paramlist)(*numpy.indices(data.shape)) - data).compressed()
        return numpy.sum(g**2)

    solution, value, d = scipy.optimize.fmin_l_bfgs_b(
        errorfunction, initial,
        fprime=None, approx_grad=True, bounds=bounds
    )

    if d['warnflag'] > 0:
        raise ValueError("Minimization failed: %d, %s" % (d['warnflag'], d['task']))

    if solution[4] > solution[3]:
        # Swapped axis order is a perfectly valid fit, but inconvenient for
        # the rest of our codebase.
        solution[3], solution[4] = solution[4], solution[3]
        solution[5] += numpy.pi/2

    return {
        "peak": solution[0],
        "xbar": solution[1],
        "ybar": solution[2],
        "semimajor": solution[3],
        "semiminor": solution[4],
        "theta": solution[5]
        }
