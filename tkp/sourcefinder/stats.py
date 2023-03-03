"""
Generic utility routines for number handling and calculating (specific)
variances used by the TKP sourcefinder.
"""

import numpy
from numpy.ma import MaskedArray
from scipy.special import erf
from scipy.optimize import fsolve


# CODE & NUMBER HANDLING ROUTINES
#
def find_true_std(sigma, clip_limit, clipped_std):
    help1 = clip_limit/(sigma*numpy.sqrt(2))
    help2 = numpy.sqrt(2*numpy.pi)*erf(help1)
    return sigma**2*(help2-2*numpy.sqrt(2)*help1*numpy.exp(-help1**2))-clipped_std**2*help2

def indep_pixels(n, correlation_lengths):
    corlengthlong, corlengthshort = correlation_lengths
    correlated_area = 0.25 * numpy.pi * corlengthlong * corlengthshort
    return n / correlated_area


def sigma_clip(data, kappa=2.0, max_iter=100,
               centref=numpy.median, distf=numpy.var, my_iterations=0, limit=None):
    """Iterative clipping

    By default, this performs clipping of the standard deviation about the
    median of the data. But by tweaking centref/distf, it could be much
    more general.

    max_iter sets the maximum number of iterations used.

    my_iterations is a counter for recursive operation of the code; leave it
    alone unless you really want to pretend to jump into the middle of a loop.

    sigma is subtle: if a callable is given, it is passed a copy of the data
    array and can calculate a clipping limit. See, for e.g., unbiased_sigma()
    defined above. However, if it isn't callable, sigma is assumed to just set
    a hard limit.

    To do: Improve documentation
            -Returns???
            -How does it make use of the beam? (It estimates the noise correlation)
    """
    if my_iterations >= max_iter:
        # Exceeded maximum number of iterations; return
        return data, my_iterations

    # Numpy 1.1 breaks std() for MaskedArray: see
    # <http://www.scipy.org/scipy/numpy/wiki/MaskedArray>.
    # MaskedArray.compressed() returns a 1-D array of non-masked data.
    if isinstance(data, MaskedArray):
        data = data.compressed()
    centre = centref(data)
    n = numpy.size(data)
    if n < 1:
        # This chunk is too small for processing; return an empty array.
        return numpy.array([]), 0, 0, 0

    clipped_var = distf(data)

    std = numpy.sqrt(clipped_var)

    if limit is not None:
        std_corr_for_clipping_bias = fsolve(find_true_std, std,
                                            args=(limit, std))[0]
    else:
        std_corr_for_clipping_bias = std

    limit = kappa * std_corr_for_clipping_bias

    newdata = data.compress(abs(data - centre) <= limit)

    if len(newdata) != len(data) and len(newdata) > 0:
        my_iterations += 1
        return sigma_clip(newdata, kappa, max_iter, centref, distf,
                          my_iterations, limit=limit)
    else:
        return newdata, std_corr_for_clipping_bias, centre, my_iterations
