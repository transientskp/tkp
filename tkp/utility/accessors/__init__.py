"""
Data accessors.

These can be used to populate ImageData objects based on some data source
(FITS file, array in memory... etc).
"""

import os
import pyfits
from tkp.db.orm import Image as DBImage
from tkp.sourcefinder.image import ImageData
from tkp.utility.accessors.dataaccessor import DataAccessor
from tkp.utility.accessors.fitsimage import FitsImage
from tkp.utility.accessors.casaimage import CasaImage
from tkp.utility.accessors.lofarfitsimage import LofarFitsImage
from tkp.utility.accessors.lofarcasaimage import LofarCasaImage
import tkp.utility.accessors.detection


def dbimage_from_accessor(dataset, dataccessor, extraction_radius):
    """Create an entry in the database image table from an image 'accessor'

    Args:

        - dataset (dataset.DataSet): DataSet for the image. Also
          provides the database connection.
        - image (DataAccessor): FITS/AIPS/HDF5 image available through
          an accessor

    Returns:

        (dataset.Image): a dataset.Image instance.
    """
    if dataccessor.freq_eff is None or dataccessor.freq_bw is None:
        raise ValueError("cannot create database image: frequency information missing")
    data = dataccessor.extract_metadata()
    data['xtr_radius'] = extraction_radius
    image = DBImage(data=data, dataset=dataset)
    return image


def sourcefinder_image_from_accessor(image, **args):
    """Create a source finder ImageData object from an image 'accessor'

    Args:

        - image (DataAccessor): FITS/AIPS/HDF5 image available through
          an accessor.

    Returns:

        (sourcefinder.ImageData): a source finder image.
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


def open(path):
    """
    Returns an accessor object (if available) for the file or directory 'path'.

    Will raise an exception if something went wrong.
    """
    if not os.access(path, os. F_OK):
        raise IOError("%s does not exist!" % path)
    if not os.access(path, os. R_OK):
        raise IOError("Don't have permission to read %s!" % path)
    Accessor = tkp.utility.accessors.detection.detect(path)
    if not Accessor:
        raise IOError("no accessor found for %s" % path)
    return Accessor(path)
