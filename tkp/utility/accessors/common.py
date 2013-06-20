"""Parsing functions used by multiple DataAccessor sub-classes"""

from math import degrees
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


