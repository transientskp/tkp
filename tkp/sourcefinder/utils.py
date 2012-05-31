# -*- coding: utf-8 -*-
#
# LOFAR Transients Key Project
#
# discovery@transientskp.org
#
#
# Source finder utilities
#
"""

This module contain utilities for the source finding routines

"""

import numpy
import math
import scipy.integrate
from .gaussian import gaussian
tkp

def generate_result_maps(data, sourcelist):
    """Return a source and residual image
    
    Given a data array (image) and list of sources, return two images, one
    showing the sources themselves and the other the residual after the
    sources have been removed from the input data.
    """
    residual_map = numpy.array(data) # array constructor copies by default
    gaussian_map = numpy.zeros(residual_map.shape)
    for src in sourcelist:
        local_gaussian = gaussian(
            src.peak.value,
            src.x.value - 1, # FITS pixel vs
            src.y.value - 1, # numpy array coordinates
            src.smaj.value,
            src.smin.value,
            src.theta.value
        )(*numpy.indices(residual_map.shape))
        gaussian_map += local_gaussian
        residual_map -= local_gaussian
    return gaussian_map, residual_map


def calculate_correlation_lengths(semimajor, semiminor):
    """Calculate the Condon correlation length

    In order to derive the error bars from Gauss fitting from the
    Condon (1997, PASP 109, 116C) formulae, one needs the so called
    correlation length. The Condon formulae assumes a circular area
    with diameter theta_N (in pixels) for the correlation. This was
    later generalized by Hopkins et al. (2003, AJ 125, 465) for
    correlation areas which are not axisymmetric.

    Basically one has theta_N^2 = theta_B*theta_b.

    Good estimates in general are:

    + theta_B = 2.0 * semimajar

    + theta_b = 2.0 * semiminor
    """

    return (2.0 * semimajor, 2.0 * semiminor)


def calculate_beamsize(semimajor, semiminor):
    """Calculate the beamsize based on the semi major and minor axes"""

    return numpy.pi * semimajor * semiminor


def fudge_max_pix(semimajor, semiminor, theta):
    """Estimate peak flux correction at pixel of maximum flux
    
    Previously, we adopted Rengelink's correction for the
    underestimate of the peak of the Gaussian by the maximum pixel
    method: fudge_max_pix = 1.06. See the WENSS paper
    (1997A&AS..124..259R) or his thesis.  (The peak of the Gaussian
    is, of course, never at the exact center of the pixel, that's why
    the maximum pixel method will always underestimate it.)

    But, instead of just taking 1.06 one can make an estimate of the
    overall correction by assuming that the true peak is at a random
    position on the peak pixel and averaging over all possible
    corrections.  This overall correction makes use of the beamshape,
    so strictly speaking only accurate for unresolved sources.
    """

    # scipy.integrate.dblquad: Computes a double integral
    # from the scipy docs:
    #   Return the double (definite) integral of f1(y,x) from x=a..b
    #   and y=f2(x)..f3(x).

    log20 = numpy.log(2.0)
    cos_theta = numpy.cos(theta)
    sin_theta = numpy.sin(theta)

    def landscape(x, y):
        up = math.pow(((cos_theta * x + sin_theta * y) / semiminor ), 2)
        down = math.pow(((cos_theta * y - sin_theta * x) / semimajor ), 2)
        return numpy.exp(log20 * ( up + down ))

    (correction, abserr) = scipy.integrate.dblquad(landscape, -0.5, 0.5,
        lambda ymin: -0.5, lambda ymax: 0.5)

    return correction


def maximum_pixel_method_variance(semimajor, semiminor, theta):
    """Estimate variance for peak flux at pixel position of maximum
    
    When we use the maximum pixel method, with a correction
    fudge_max_pix, there should be no bias, unless the peaks of the
    Gaussians are not randomly distributed, but relatively close to
    the centres of the pixels due to selection effects from detection
    thresholds.

    Disregarding the latter effect and noise, we can compute the
    variance of the maximum pixel method by integrating (the true
    flux-the average true flux)^2 = (the true flux-fudge_max_pix)^2
    over the pixel area and dividing by the pixel area ( = 1).  This
    is just equal to integral of the true flux^2 over the pixel area
    - fudge_max_pix^2.
    """

    # scipy.integrate.dblquad: Computes a double integral
    # from the scipy docs:
    #   Return the double (definite) integral of f1(y,x) from x=a..b
    #   and y=f2(x)..f3(x).
    variance = (scipy.integrate.dblquad(
        lambda y, x: numpy.exp(2.0 * numpy.log(2.0) *
                               (((numpy.cos(theta) * x +
                                  numpy.sin(theta) * y) / semiminor) ** 2.0 +
                                ((numpy.cos(theta) * y -
                                  numpy.sin(theta) * x) / semimajor) ** 2.0)),
        -0.5,
        0.5,
        lambda ymin: -0.5,
        lambda ymax: 0.5)[0]
                - fudge_max_pix(semimajor, semiminor, theta) ** 2)

    return variance


def flatten(nested_list):
    """Flatten a nested list

    Nested lists are made in the deblending algorithm. They're
    awful. This is a piece of code I grabbed from
    http://www.daniweb.com/code/snippet216879.html.

    The output from this method is a generator, so make sure to turn
    it into a list, like this::

        flattened = list(flatten(nested)).
    """
    for elem in nested_list:
        if isinstance(elem, (tuple, list, numpy.ndarray)):
            for i in flatten(elem):
                yield i
        else:
            yield elem
