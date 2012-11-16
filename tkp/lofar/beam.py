"""
Beam characterization

more info:
http://www.astron.nl/radio-observatory/astronomers/lofar-imaging-capabilities-sensitivity/lofar-imaging-capabilities/lofa
"""

import math

def fwhm(lambda_, d, alpha1=1.3):
    """
    The nominal Full Width Half Maximum (FWHM) of a LOFAR Station beam

    Args:
        lambda_: wavelength in meters
        d: station diameter.
        alpha1: depends on the tapering intrinsic to the layout of the station,
                and any additional tapering which may be used to form the
                station beam. No electronic tapering is presently applied to
                LOFAR station beamforming. For a uniformly illuminated circular
                aperture, alpha1 takes the value of 1.02, and the value increases
                with tapering (Napier 1999).
    return: the nominal Full Width Half Maximum (FWHM)
    """
    return alpha1 * lambda_ / d


def fov(fwhm):
    """The Field of View (FoV) of a LOFAR station"""
    return math.pi * ((fwhm / 2) ** 2)