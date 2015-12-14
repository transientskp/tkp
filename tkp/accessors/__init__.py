"""
Data accessors.

These can be used to populate ImageData objects based on some data source
(FITS file, array in memory... etc).
"""

import os
import astropy.io.fits as pyfits
from tkp.sourcefinder.image import ImageData
from tkp.accessors.dataaccessor import DataAccessor
from tkp.accessors.fitsimage import FitsImage
from tkp.accessors.casaimage import CasaImage
from tkp.accessors.aartfaaccasaimage import AartfaacCasaImage
from tkp.accessors.lofarfitsimage import LofarFitsImage
from tkp.accessors.lofarcasaimage import LofarCasaImage
import tkp.accessors.detection



def sourcefinder_image_from_accessor(image, **args):
    """Create a source finder ImageData object from an image 'accessor'

    Args:

        - image (DataAccessor): FITS/AIPS/HDF5 image available through
          an accessor.

    Returns:
        (:class:`tkp.sourcefinder.image.ImageData`): a source finder image.
    """
    image = ImageData(image.data, image.beam, image.wcs, **args)
    return image


def writefits(data, filename, header = {}):
    """
    Dump a NumPy array to a FITS file.

    Key/value pairs for the FITS header can be supplied in the optional
    header argument as a dictionary.
    """
    if header.__class__.__name__ == 'Header':
        pyfits.writeto(filename, data.transpose(), header)
    else:
        hdu = pyfits.PrimaryHDU(data.transpose())
        for key in header.iterkeys():
            hdu.header.update(key, header[key])
        hdu.writeto(filename)


def open(path, *args, **kwargs):
    """
    Returns an accessor object (if available) for the file or directory 'path'.

    We try all the possible accessors in order from most specific to least
    specific. That is, if possible, we prefer an accessor providing
    LofarAccessor to one providing DataAccessor, but we accept the latter if
    that's the only possible match.

    Will raise an exception if something went wrong or no matching accessor
    class is found.
    """
    if not os.access(path, os.F_OK):
        raise IOError("%s does not exist!" % path)
    if not os.access(path, os.R_OK):
        raise IOError("Don't have permission to read %s!" % path)
    Accessor = tkp.accessors.detection.detect(path)
    if not Accessor:
        raise IOError("no accessor found for %s" % path)
    return Accessor(path, *args, **kwargs)
