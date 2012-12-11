from math import sqrt, sin, cos, pi


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