"""
Parsing functions used by multiple DataAccessor sub-classes
"""

from math import degrees, sqrt, sin, pi, cos


def parse_pixelsize(wcs):
    """
    Arguments:
      - wcs: A tkp.coordinates.wcs.WCS object

    Returns:
      - deltax: pixel size along the x axis in degrees
      - deltay: pixel size along the x axis in degrees

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
    """
    Convert beam in degrees to beam in pixels and radians.
    For example Fits beam parameters are in degrees.

    Arguments:
      - bmaj:   Beam major axis in degrees
      - bmin:   Beam minor axis in degrees
      - bpa:    Beam position angle in degrees
      - deltax: Pixel size along the x axis in degrees
      - deltay: Pixel size along the y axis in degrees

    Returns:
      - semimaj: Beam semi-major axis in pixels
      - semimin: Beam semi-minor axis in pixels
      - theta:   Beam position angle in radians
    """
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



def unique_column_values(table, column_name):
    """
    Find all the unique values in a particular column of a CASA table.

    Arguments:
      - table:       ``pyrap.tables.table``
      - column_name: ``str``

    Returns:
      - ``numpy.ndarray`` containing unique values in column.
    """
    return table.query(
        columns=column_name, sortlist="unique %s" % (column_name)
    ).getcol(column_name)
