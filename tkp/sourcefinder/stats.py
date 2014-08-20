"""
Generic utility routines for number handling and calculating (specific)
variances used by the TKP sourcefinder.
"""

import numpy
from numpy.ma import MaskedArray
from scipy.special import erf
from scipy.special import erfcinv
from .utils import calculate_correlation_lengths


# CODE & NUMBER HANDLING ROUTINES
#
def var_helper(N):
    """Correct for the fact the rms noise is computed from a clipped
    distribution.

    That noise will always be lower than the noise from the complete
    distribution.  The correction factor is a function of the computed
    rms noise only.
    """
    term1 = numpy.sqrt(2. * numpy.pi) * erf(N / numpy.sqrt(2.))
    term2 = 2. * N * numpy.exp(-N**2 / 2.)
    return term1 / (term1 - term2)


def indep_pixels(N, beam):
    corlengthlong, corlengthshort = calculate_correlation_lengths(
        beam[0], beam[1])
    correlated_area = 0.25 * numpy.pi * corlengthlong * corlengthshort
    return N / correlated_area


def unbiased_sigma(N_indep):
    """Calculate an unbiased sigma for using in sigma clipping.

    The formula below for cliplim is pretty subtle. Kappa, sigma
    clipping should be such that the noise is not biased by
    it. Consequently, the clipping boundaries should be such that
    exactly half an independent pixel should exceed it if the map were
    source free. A rigid boundary of 3 sigma is appropriate only if the
    number of independent pixels is about 185 (the number of
    independent pixels equals the number of pixels divided by the
    beamsize in pixels).

    The condition that kappa, sigma clipping may not bias the noise is
    translated in the formula below, using Gaussian statistics. A
    disadvantage of this is that more iterations of kappa, sigma
    clipping are needed, compared to 3 sigma clipping. However, the
    noise values derived are generally significantly different (lower)
    compared to 3 sigma clipping.
    """

    return 1.4142135623730951 * erfcinv(0.5 / N_indep)


def sigma_clip(data, beam, sigma=unbiased_sigma, max_iter=100,
               centref=numpy.median, distf=numpy.var, my_iterations=0,
               corr_clip=1.):
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
    N = numpy.size(data)
    N_indep = indep_pixels(N, beam)
    if N_indep < 1:
        # This chunk is too small for processing; return an empty array.
        return numpy.array([]), 0, 0, 0

    # If sigma is callable, use it to dynamically calculate the clipping
    # limits.
    if callable(sigma):
        my_sigma = sigma(N_indep)
    else:
        my_sigma = sigma

    # distf=numpy.var is a sample variance with the factor N/(N-1)
    # already built in, N being the number of pixels. So, we are
    # going to remove that and replace it by N_indep/(N_indep-1)
    clipped_var = distf(data) * (N - 1.) * N_indep / (N * (N_indep - 1.))
    unbiased_var = corr_clip * clipped_var

    # There is an extra factor c4 needed to get a unbiased standard
    # deviation, unbiased if we disregard clipping bias, see
    # http://en.wikipedia.org/wiki/Unbiased_estimation_of_standard_deviation\
    #         #Results_for_the_normal_distribution
    c4 = 1. - 0.25 / N_indep - 0.21875 / N_indep**2
    unbiased_std = numpy.sqrt(unbiased_var) / c4

    limit = my_sigma * unbiased_std

    newdata = data.compress(abs(data - centre) <= limit)

    if len(newdata) != len(data) and len(newdata) > 0:
        corr_clip = var_helper(my_sigma)
        my_iterations += 1
        return sigma_clip(newdata, beam, sigma, max_iter, centref, distf,
                          my_iterations, corr_clip)
    else:
        return newdata, unbiased_std, centre, my_iterations
