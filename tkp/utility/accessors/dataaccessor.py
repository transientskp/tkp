
from tkp.utility.coordinates import WCS
import datetime


class DataAccessor(object):
    """
    Base class for accessors used with :class:`..sourcefinder.image.ImageData`.

    Data accessors provide a uniform way for the ImageData class (ie, generic
    image representation) to access the various ways in which images may be
    stored (FITS files, arrays in memory, potentially HDF5, etc).
    """

    def __init__(self):
        self.beam = None
        self.wcs = WCS()
        self.inttime = 0.  # seconds
        self.obstime = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.freqbw = None
        self.freqeff = None  # Hertz (? MHz?)
        self.filename = "not set"
        self.data = None
        self.plane = 0
