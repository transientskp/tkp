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

#def parse_pixel_scale(wcs):
#    """Returns pixel width in degrees.
#
#    Valid for both 'lofarcasaimage' and 'fitsimage'.
#
#    Checks that we have square pixels and that the wcs units are degrees-
#    If this is not the case, this must be non-standard (non-LOFAR?) data,
#    so we can safely throw an exception and tell the user to add handling logic.
#    """
#    if wcs.cunit != ('deg', 'deg'):
#        raise ValueError("Image WCS header info not in degrees "
#                         "- unsupported use case")
#    #NB. What's a reasonable epsilon here? 
#    eps = 1e-7
#    if abs(abs(wcs.cdelt[0]) - abs(wcs.cdelt[1])) > eps:
#        raise ValueError("Image WCS header suggests non-square pixels "
#                         "- unsupported use case")
#    return abs(wcs.cdelt[0])

