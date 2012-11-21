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


def fitgaussian(data, params, fixed=None, maxfev=0):
    """Calculate source positional values by fitting a 2D Gaussian

    Args:

        data (numpy.ndarray): Actual 2D data

        params (dict): initial fit parameters (possibly estimated
            using the moments function

    Kwargs:

        fixed (dict): parameters to be kept frozen (ie, not fitted)

        maxfew (int): maximum number of calls to the error function

    Returns:

        (dict): peak, total, x barycenter, y barycenter, semimajor,
            semiminor, theta

    Raises:

        ValueError (in case of a bad fit)

    Perform a least squares fit to an elliptical Gaussian. Uses the
    moments() method to generate an initial estimate of the solution. Based on
    code from SciPy cookbook, but modified to take account of rotation of
    ellipse relative to axes.

    If a dict called fixed is passed in, then parameters specified within the
    dict with the same names as fit_params (below) will be "locked" in the
    fitting process.

    input: numpy array of pixel values, initial parameters for fit (a dict, as
    generated by moments(), above.
    output: max value, barycenter pixel x, y, length of semimajor & minor
    axes, angle between x axis and semi-major axis in radians. In a dict, as
    above.
    """
    fixed = fixed or {}
    # Collect necessary values from parameter dict; only those which aren't
    # fixed.
    my_pars = []
    for param in FIT_PARAMS:
        if param not in fixed:
            if isinstance(params[param], Uncertain):
                my_pars.append(params[param].value)
            else:
                my_pars.append(params[param])

    def errorfunction(paramlist, fixed):
        """Error function to be used in chi-squared fitting

        :argument paramlist: fitting parameters
        :type paramlist: dict
        :argument fixed: parameters to be held frozen
        :type fixed: dict

        :returns: 2d-array of difference between estimated Gaussian function
            and the actual data
        """

        paramlist = list(paramlist)
        gaussian_args = []
        for param in FIT_PARAMS:
            if param in fixed:
                gaussian_args.append(fixed[param])
            else:
                gaussian_args.append(paramlist.pop(0))

        # The .compressed() below is essential so the Gaussian fit
        # will not take account of the masked values (=below
        # threshold) at the edges and corners of data (=(masked)
        # array, so rectangular in shape).
        return (gaussian(*gaussian_args)(*numpy.indices(data.shape)) -
                data ).compressed()

    # maxfev=0, the default, corresponds to 200*(N+1) (NB, not 100*(N+1) as
    # the scipy docs state!) function evaluations, where N is the number of
    # parametrs in the solution.
    # Convergence tolerances xtol and ftol established by experiment on images
    # from Paul Hancock's simulations.
    solution, icov_x, infodict, mesg, success = scipy.optimize.leastsq(
        errorfunction, my_pars, fixed, full_output=True, maxfev=maxfev,
        xtol=1e-4, ftol=1e-4
    )

    # solution contains only the variable parameters; we need to merge the
    # contents of fixed into the solution list.
    try:
        tmp_solution = list(solution)
    except TypeError:
        tmp_solution = [solution]
    solution = []
    for param in FIT_PARAMS:
        if param in fixed:
            solution.append(fixed[param])
        else:
            solution.append(tmp_solution.pop(0))

    if success in [5, 6, 7, 8]:
        raise ValueError("leastsq returned %d (%s)" % (success, mesg))

    if solution[4] > solution[3]:
        # Swapped axis order is a perfectly valid fit, but inconvenient for
        # the rest of our codebase.
        solution[3], solution[4] = solution[4], solution[3]
        solution[5] += numpy.pi/2

    # Negative axes are a valid fit, since they are squared in the definition
    # of the Gaussian.
    solution[3] = abs(solution[3])
    solution[4] = abs(solution[4])

    return {
        "peak": solution[0],
        "xbar": solution[1],
        "ybar": solution[2],
        "semimajor": solution[3],
        "semiminor": solution[4],
        "theta": solution[5]
    }
