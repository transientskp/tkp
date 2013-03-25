"""
Beam characterization calculations.

For more information and the math behind this code go to the `LOFAR imaging
capabilities page
<http://www.astron.nl/radio-observatory/astronomers/lofar-imaging-capabilities-sensitivity/lofar-imaging-capabilities/lofa>`_.
"""

import math

def fwhm(lambda_, d, alpha1=1.3):
    """
    The nominal Full Width Half Maximum (FWHM) of a LOFAR Station beam.

    :param lambda_: wavelength in meters
    :param d: station diameter.
    :param alpha1: depends on the tapering intrinsic to the layout of the station,
                and any additional tapering which may be used to form the
                station beam. No electronic tapering is presently applied to
                LOFAR station beamforming. For a uniformly illuminated circular
                aperture, alpha1 takes the value of 1.02, and the value increases
                with tapering (Napier 1999).
    :returns: the nominal Full Width Half Maximum (FWHM)
    """
    return alpha1 * lambda_ / d


def fov(fwhm):
    """
    The Field of View (FoV) of a LOFAR station

    :param fwhm: nominal Full Width Half Maximum, caulculated with :func:`fwhm`.

    """
    return math.pi * ((fwhm / 2) ** 2)