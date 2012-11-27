import os.path
import pyfits
from pyrap.tables import table as pyrap_table
from pyrap.images import image as pyrap_image
from tkp.utility.accessors.lofarcasaimage import LofarCasaImage, subtable_names
from tkp.utility.accessors.casaimage import CasaImage
from tkp.utility.accessors.lofarhdf5image import LofarHdf5Image
from tkp.utility.accessors.fitsimage import FitsImage

# files that should be contained by a casa table
casafiles = ["table.dat", "table.f0", "table.f0_TSM0", "table.info", "table.lock"]

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
        table = pyrap_table(filename)
    except RuntimeError:
        return False
    return True

def islofarcasa(filename):
    """returns True if filename is a lofar casa directory"""
    if not iscasa(filename):
        return False
    table = pyrap_table(filename)
    if not 'ATTRGROUPS' in table.getkeywords():
        return False
    attrgroups = table.getkeyword('ATTRGROUPS').keys()
    for subtable in subtable_names:
        if subtable not in attrgroups:
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

mapping = (
    (islofarcasa, LofarCasaImage),
    (isfits,  FitsImage),
    (iscasa, CasaImage),
    (islofarhdf5, LofarHdf5Image),
)

def detect(filename):
    """returns the accessor class that should be used to process filename"""
    for func, class_ in mapping:
        if func(filename): return class_
