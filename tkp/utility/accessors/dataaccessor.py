
from tkp.utility.coordinates import WCS
import datetime
import numpy

class DataAccessor(object):
    """
    Base class for accessors used with :class:`..sourcefinder.image.ImageData`.

    Data accessors provide a uniform way for the ImageData class (ie, generic
    image representation) to access the various ways in which images may be
    stored (FITS files, arrays in memory, potentially HDF5, etc).
    """

    def __init__(self, *args, **kwargs):
        self.beam = kwargs.pop('beam', (None, None, None))
        self.wcs = kwargs.pop('wcs', WCS())
        super(DataAccessor, self).__init__(*args, **kwargs)
        # Set defaults
        self.inttime = 0.  # seconds
        self.obstime = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.freqbw = None
        self.freqeff = None  # Hertz (? MHz?)

    def _beamsizeparse(self, bmaj, bmin, bpa):
        """Calculate beam in pixels and radians.
        Needs beam parameters, no defaults."""

        semimaj = (bmaj / 2.) * (numpy.sqrt(
            (numpy.sin(numpy.pi * bpa / 180.)**2) /
            (self.wcs.cdelt[0]**2) +
            (numpy.cos(numpy.pi * bpa / 180.)**2) /
            (self.wcs.cdelt[1]**2)))
        semimin = (bmin / 2.) * (numpy.sqrt(
            (numpy.cos(numpy.pi * bpa / 180.)**2) /
            (self.wcs.cdelt[0]**2) +
            (numpy.sin(numpy.pi * bpa / 180.)**2) /
            (self.wcs.cdelt[1]**2)))
        theta = numpy.pi * bpa / 180
        self.beam = (semimaj, semimin, theta)
