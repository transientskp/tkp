import os.path
import astropy.io.fits as pyfits
import logging
from collections import namedtuple
from casacore.tables import table as casacore_table
from casacore.images import image as casacore_image
from tkp.accessors.lofarcasaimage import LofarCasaImage
from tkp.accessors.lofarhdf5image import LofarHdf5Image
from tkp.accessors.fitsimage import FitsImage
from tkp.accessors.amicasaimage import AmiCasaImage
from tkp.accessors.lofarfitsimage import LofarFitsImage
from tkp.accessors.kat7casaimage import Kat7CasaImage
from tkp.accessors.aartfaaccasaimage import AartfaacCasaImage


logger = logging.getLogger(__name__)


# files that should be contained by a casa table
casafiles = ("table.dat", "table.f0", "table.f0_TSM0", "table.info",
             "table.lock")

# We will take the first accessor for which the test returns True.
FitsTest = namedtuple('FitsTest', ['accessor', 'test'])
fits_type_mapping = [
    FitsTest(
        accessor=LofarFitsImage,
        test=lambda hdr: 'TELESCOP' in hdr and 'ANTENNA' in hdr and hdr.get('TELESCOP') == "LOFAR"
    )
]

casa_telescope_keyword_mapping = {
    'LOFAR': LofarCasaImage,
    'KAT-7': Kat7CasaImage,
    'AARTFAAC': AartfaacCasaImage,
    'AMI-LA': AmiCasaImage,
}


def isfits(filename):
    """returns True if filename is a fits file"""
    if not os.path.isfile(filename):
        return False
    if filename[-4:].lower() != 'fits':
        return False
    try:
        with pyfits.open(filename):
            pass
    except IOError:
        return False
    return True


def iscasa(filename):
    """returns True if filename is a lofar casa directory"""
    if not os.path.isdir(filename):
        return False
    for file_ in casafiles:
        casafile = os.path.join(filename, file_)
        if not os.path.isfile(casafile):
            logger.debug("%s doesn't contain %s" % (filename, file_))
            return False
    try:
        table = casacore_table(filename.encode(), ack=False)
        table.close()
    except RuntimeError as e:
        logger.debug("directory looks casacore, but cannot open: %s" % str(e))
        return False
    return True


def islofarhdf5(filename):
    """returns True if filename is a hdf5 container"""
    if not os.path.isfile(filename):
        return False
    if filename[-2:].lower() != 'h5':
        return False
    try:
        casacore_image(filename)
    except RuntimeError:
        return False
    return True


def fits_detect(filename):
    """
    Detect which telescope produced FITS data, return corresponding accessor.

    Checks for known FITS image types where we expect additional metadata.
    If the telescope is unknown we default to a regular FitsImage.
    """
    with pyfits.open(filename) as hdulist:
        hdr = hdulist[0].header
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
    table = casacore_table(filename.encode(), ack=False)
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
