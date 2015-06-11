"""
Source fitting routines.
"""

import math
import numpy
import scipy.optimize
from .gaussian import gaussian
from .stats import indep_pixels
import utils

FIT_PARAMS = ('peak', 'xbar', 'ybar', 'semimajor', 'semiminor', 'theta')

def moments(data, beam, threshold=0):
    """Calculate source positional values using moments

    Args:

        data (numpy.ndarray): Actual 2D image data

        beam (3-tuple): beam (psf) information, with semi-major and
            semi-minor axes

    Returns:
        dict: peak, total, x barycenter, y barycenter, semimajor
            axis, semiminor axis, theta

    Raises:
        exceptions.ValueError: in case of NaN in input.

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

    # Theta is not affected by the cut-off at the threshold (see Spreeuw 2010,
    # page 45).
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


def fitgaussian(pixels, params, fixed=None, maxfev=0):
    """Calculate source positional values by fitting a 2D Gaussian

    Args:
        pixels (numpy.ma.MaskedArray): Pixel values (with bad pixels masked)

        params (dict): initial fit parameters (possibly estimated
            using the moments() function, above)

    Kwargs:
        fixed (dict): parameters & their values to be kept frozen (ie, not
            fitted)

        maxfev (int): maximum number of calls to the error function

    Returns:
        dict: peak, total, x barycenter, y barycenter, semimajor,
            semiminor, theta (radians)

    Raises:
        exceptions.ValueError: In case of a bad fit.

    Perform a least squares fit to an elliptical Gaussian.

    If a dict called fixed is passed in, then parameters specified within the
    dict with the same names as fit_params (below) will be "locked" in the
    fitting process.
    """
    fixed = fixed or {}

    # Collect necessary values from parameter dict; only those which aren't
    # fixed.
    initial = []
    for param in FIT_PARAMS:
        if param not in fixed:
            if hasattr(params[param], "value"):
                initial.append(params[param].value)
            else:
                initial.append(params[param])

    def residuals(paramlist):
        """Error function to be used in chi-squared fitting

        :argument paramlist: fitting parameters
        :type paramlist: numpy.ndarray
        :argument fixed: parameters to be held frozen
        :type fixed: dict

        :returns: 2d-array of difference between estimated Gaussian function
            and the actual pixels
        """
        paramlist = list(paramlist)
        gaussian_args = []
        for param in FIT_PARAMS:
            if param in fixed:
                gaussian_args.append(fixed[param])
            else:
                gaussian_args.append(paramlist.pop(0))

        # gaussian() returns a function which takes arguments x, y and returns
        # a Gaussian with parameters gaussian_args evaluated at that point.
        g = gaussian(*gaussian_args)

        # The .compressed() below is essential so the Gaussian fit will not
        # take account of the masked values (=below threshold) at the edges
        # and corners of pixels (=(masked) array, so rectangular in shape).
        pixel_resids = numpy.ma.MaskedArray(
            data = numpy.fromfunction(g, pixels.shape) - pixels,
            mask = pixels.mask)
        return pixel_resids.compressed()

    # maxfev=0, the default, corresponds to 200*(N+1) (NB, not 100*(N+1) as
    # the scipy docs state!) function evaluations, where N is the number of
    # parameters in the solution.
    # Convergence tolerances xtol and ftol established by experiment on images
    # from Paul Hancock's simulations.
    soln, success = scipy.optimize.leastsq(
        residuals, initial, maxfev=maxfev, xtol=1e-4, ftol=1e-4
    )

    if success > 4:
        raise ValueError("leastsq returned %d; bailing out" % (success,))

    # soln contains only the variable parameters; we need to merge the
    # contents of fixed into the soln list.
    # leastsq() returns either a numpy.float64 (if fitting a single value) or
    # a numpy.ndarray (if fitting multiple values); we need to turn that into
    # a list for the merger.
    try:
        # If an ndarray (or other iterable)
        soln = list(soln)
    except TypeError:
        soln = [soln]
    results = fixed.copy()
    for param in FIT_PARAMS:
        if param not in results:
            results[param] = soln.pop(0)

    if results['semiminor'] > results['semimajor']:
        # Swapped axis order is a perfectly valid fit, but inconvenient for
        # the rest of our codebase.
        results['semimajor'], results['semiminor'] = results['semiminor'], results['semimajor']
        results['theta'] += numpy.pi/2

    # Negative axes are a valid fit, since they are squared in the definition
    # of the Gaussian.
    results['semimajor'] = abs(results['semimajor'])
    results['semiminor'] = abs(results['semiminor'])

    return results

def goodness_of_fit(masked_residuals, noise, beam):
    """
    Calculates the goodness-of-fit values, `chisq` and `reduced_chisq`.

    .. Warning::
        We do not use the `standard chi-squared
        formula <https://en.wikipedia.org/wiki/Goodness_of_fit#Regression_analysis>`_
        for calculating these goodness-of-fit
        values, and should probably rename them in the next release.
        See below for details.


    These goodness-of-fit values are related to, but not quite the same as
    reduced chi-squared.
    Strictly speaking the reduced chi-squared is statistically
    invalid for a Gaussian model from the outset
    (see `arxiv:1012.3754 <http://arxiv.org/abs/1012.3754>`_).
    We attempt to provide a resolution-independent estimate of goodness-of-fit
    ('reduced chi-squared'), by using the same 'independent pixels' correction
    as employed when estimating RMS levels, to normalize the chi-squared value.
    However, as applied to the standard formula this will sometimes
    imply that we are fitting a fractional number of datapoints less than 1!
    As a result, it doesn't really make sense to try and apply the
    'degrees-of-freedom' correction, as this would likely result in a
    negative ``reduced_chisq`` value.
    (And besides, the 'degrees of freedom' concept is invalid for non-linear
    models.) Finally, note that when called from
    :func:`.source_profile_and_errors`, the noise-estimate at the peak-pixel
    is supplied, so will typically over-estimate the noise and
    hence under-estimate the chi-squared values.

    Args:
        masked_residuals(numpy.ma.MaskedArray): The pixel-residuals from the fit
        noise (float): An estimate of the noise level. Could also be set to
            a masked numpy array matching the data, for per-pixel noise
            estimates.
        beam (tuple): Beam parameters

    Returns:
        tuple: chisq, reduced_chisq

    """
    gauss_resid_normed = (masked_residuals / noise).compressed()
    chisq = numpy.sum(gauss_resid_normed*gauss_resid_normed)
    n_fitted_pix = len(masked_residuals.compressed().ravel())
    n_indep_pix = indep_pixels(n_fitted_pix, beam)
    reduced_chisq = chisq / n_indep_pix
    return chisq, reduced_chisq