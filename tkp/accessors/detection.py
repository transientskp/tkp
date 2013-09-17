import os.path
import pyfits
import logging
from collections import namedtuple
from pyrap.tables import table as pyrap_table
from pyrap.images import image as pyrap_image
from tkp.accessors.lofarcasaimage import LofarCasaImage
from tkp.accessors.lofarhdf5image import LofarHdf5Image
from tkp.accessors.fitsimage import FitsImage
from tkp.accessors.lofarfitsimage import LofarFitsImage
from tkp.accessors.kat7casaimage import Kat7CasaImage


logger = logging.getLogger(__name__)


# files that should be contained by a casa table
casafiles = ("table.dat", "table.f0", "table.f0_TSM0", "table.info",
             "table.lock")

# We will take the first accessor for which the test returns True.
FitsTest  = namedtuple('FitsTest', ['accessor', 'test'])
fits_type_mapping = [
    FitsTest(
        accessor=LofarFitsImage,
        test=lambda hdr: 'TELESCOP' in hdr and 'ANTENNA' in hdr and hdr.get('TELESCOP') == "LOFAR"
    )
]

casa_telescope_keyword_mapping = {
    'LOFAR': LofarCasaImage,
    'KAT-7': Kat7CasaImage,
}


def isfits(filename):
    """returns True if filename is a fits file"""
    if not os.path.isfile(filename):
        return False
    if filename[-4:].lower() != 'fits':
        return False
    try:
        pyfits.open(filename)
    except IOError:
        return False
    return True


def iscasa(filename):
    """returns True if filename is a lofar casa directory"""
    if not os.path.isdir(filename):
        return False
    for file in casafiles:
        casafile = os.path.join(filename, file)
        if not os.path.isfile(casafile):
            logger.debug("%s doesn't contain %s" % file)
            return False
    try:
        table = pyrap_table(filename.encode(), ack=False)
    except RuntimeError:
        return False
    return True


def islofarhdf5(filename):
    """returns True if filename is a hdf5 container"""
    if not os.path.isfile(filename):
        return False
    if filename[-2:].lower() != 'h5':
        return False
    try:
        pyrap_image(filename)
    except RuntimeError:
        return False
    return True


def fits_detect(filename):
    """
    Detect which telescope produced FITS data, return corresponding accessor.

    Checks for known FITS image types where we expect additional metadata.
    If the telescope is unknown we default to a regular FitsImage.
    """
    hdu = pyfits.open(filename)
    hdr = hdu[0].header
    for fits_test in fits_type_mapping:
        if fits_test.test(hdr):
            return fits_test.accessor
    return FitsImage


def casa_detect(filename):
    """
    Detect which telescope produced CASA data, return corresponding accessor.

    Checks for known CASA table types where we expect additional metadata.
    If the telescope is unknown we return nothing.
    """
    table = pyrap_table(filename.encode(), ack=False)
    telescope = table.getkeyword('coords')['telescope']
    return casa_telescope_keyword_mapping.get(telescope, None)


def detect(filename):
    """returns the accessor class that should be used to process filename"""
    if isfits(filename):
        return fits_detect(filename)
    elif iscasa(filename):
        return casa_detect(filename)
    elif islofarhdf5(filename):
        return LofarHdf5Image
    else:
        raise IOError("unsupported format: %s" % filename)
