"""
Data accessors.

These can be used to populate ImageData objects based on some data source
(FITS file, array in memory... etc).
"""

# Todo: use of numpy.squeeze() appears a bad idea, in the case of
# (unlikely, but not impossible) [1, Y] or [X, 1] shaped images...


import pyfits
from tkp.database import Image as DBImage
from tkp.utility.accessors.dataaccessor import extract_metadata
from tkp.sourcefinder.image import ImageData
import tkp.utility.accessors.detection
from tkp.utility.accessors.dataaccessor import DataAccessor
from tkp.utility.accessors.fitsimage import FitsImage
from tkp.utility.accessors.casaimage import CasaImage


def dbimage_from_accessor(dataset, dataccessor):
    """Create an entry in the database images table from an image 'accessor'

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
    data = extract_metadata(dataccessor)
    image = DBImage(data=data, dataset=dataset)
    return image


def sourcefinder_image_from_accessor(image):
    """Create a source finder ImageData object from an image 'accessor'

    Args:

        - image (DataAccessor): FITS/AIPS/HDF5 image available through
          an accessor.

    Returns:

        (sourcefinder.ImageData): a source finder image.
    """
    image = ImageData(image.data, image.beam, image.wcs)
    return image


def writefits(data, filename, header = {}):
    """
    Dump a NumPy array to a FITS file.

    Key/value pairs for the FITS header can be supplied in the optional
    header argument as a dictionary.
    """
    if header.__class__.__name__=='Header':
        pyfits.writeto(filename,data.transpose(),header)
    else:
        hdu = pyfits.PrimaryHDU(data.transpose())
        for key in header.iterkeys():
            hdu.header.update(key, header[key])
        hdu.writeto(filename)


def open(path):
    """
    Returns an accessor object (if available) for the file or directory 'path'
    """
    Accessor = tkp.utility.accessors.detection.detect(path)
    if not Accessor:
        raise IOError("no accessor found for %s" % path)
    return Accessor(path)
