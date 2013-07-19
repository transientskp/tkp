"""
Parsing functions used by multiple DataAccessor sub-classes
"""

from math import degrees, sqrt, sin, pi, cos


def parse_pixelsize(wcs):
    """
    Args:
      - wcs: A tkp.coordinates.wcs.WCS object

    Returns: 
        pixelsize, as an (x,y) tuple, in units of degrees

    """
    #Would have to be pretty strange data for this not to be the case
    assert wcs.cunit[0] == wcs.cunit[1]
    if wcs.cunit[0] == "deg":
        deltax = wcs.cdelt[0]
        deltay = wcs.cdelt[1]
    elif wcs.cunit[0] == "rad":
        deltax = degrees(wcs.cdelt[0])
        deltay = degrees(wcs.cdelt[1])
    else:
        raise ValueError("Unrecognised WCS co-ordinate system")

    #NB. What's a reasonable epsilon here? 
    eps = 1e-7
    if abs(abs(deltax) - abs(deltay)) > eps:
        raise ValueError("Image WCS header suggests non-square pixels."
                 "This is an untested use case, and may break things -"
                 "specifically the skyregion tracking but possibly other stuff too.")
    return deltax, deltay


def degrees2pixels(bmaj, bmin, bpa, deltax, deltay):
    """convert beam in degrees to beam in pixels and radians.
    For example Fits beam parameters are in degrees."""
    semimaj = (bmaj / 2.) * (sqrt(
        (sin(pi * bpa / 180.)**2) / (deltax**2) +
        (cos(pi * bpa / 180.)**2) / (deltay**2))
    )
    semimin = (bmin / 2.) * (sqrt(
        (cos(pi * bpa / 180.)**2) / (deltax**2) +
        (sin(pi * bpa / 180.)**2) / (deltay**2))
    )
    theta = pi * bpa / 180
    return (semimaj, semimin, theta)


def arcsec2degrees(bmaj, bmin, bpa):
    """converts beam paramets from arcsec to degrees.
    For example CASAtable beam parameters are in arcsec"""
    return (bmaj / 3600, bmin / 3600, bpa)