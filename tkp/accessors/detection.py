import os.path
import pyfits
from pyrap.tables import table as pyrap_table
from pyrap.images import image as pyrap_image
from tkp.accessors.lofarcasaimage import LofarCasaImage, subtable_names
from tkp.accessors.casaimage import CasaImage
from tkp.accessors.lofarhdf5image import LofarHdf5Image
from tkp.accessors.fitsimage import FitsImage
from tkp.accessors.lofarfitsimage import LofarFitsImage
from tkp.accessors.kat7casaimage import Kat7CasaImage

# files that should be contained by a casa table
casafiles = ("table.dat", "table.f0", "table.f0_TSM0", "table.info", "table.lock")

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

fits_telescope_keyword_mapping = {'LOFAR': LofarFitsImage}
casa_telescope_keyword_mapping = {
    'LOFAR': LofarCasaImage,
    'KAT7': Kat7CasaImage,
}

def detect(filename):
    """returns the accessor class that should be used to process filename"""
    if isfits(filename):
        return fits_detect(filename)
    elif iscasa(filename):
        return casa_detect(filename)
    elif islofarhdf5(filename):
        return LofarHdf5Image
    else:
        raise IOError("This data appears to be in unsupported format:\n%s",
                           filename)

def fits_detect(filename):
    """
    Detect which telescope produced FITS data, return corresponding accessor.
    
    Checks for known FITS image types where we expect additional metadata.
    If the telescope is unknown we default to a regular FitsImage.
    """
    hdu = pyfits.open(filename)
    hdr = hdu[0].header
    telescope = hdr.get('TELESCOP')
    return fits_telescope_keyword_mapping.get(telescope, FitsImage)

def casa_detect(filename):
    """
    Detect which telescope produced CASA data, return corresponding accessor.
    
    Checks for known CASA table types where we expect additional metadata.
    If the telescope is unknown we default to a regular CasaImage.
    """
    table = pyrap_table(filename.encode(), ack=False)
    telescope = table.getkeyword('coords')['telescope']
    return casa_telescope_keyword_mapping.get(telescope, CasaImage)
