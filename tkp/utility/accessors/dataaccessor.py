
from tkp.utility.coordinates import WCS
import datetime


	
def extract_metadata(dataaccessor):
    return {
        'tau_time': dataaccessor.inttime,
        'freq_eff': dataaccessor.freqeff,
        'freq_bw': dataaccessor.freqbw,
        'taustart_ts': dataaccessor.obstime.strftime("%Y-%m-%d %H:%M:%S.%f"),
        'url': dataaccessor.filename,
        'band': 0,    # not yet clearly defined
        'bsmaj': float(dataaccessor.beam[0]), ## NB We must cast to a standard python float
        'bsmin': float(dataaccessor.beam[1]), ## as Monetdb converter cannot handle numpy.float64
        'bpa': float(dataaccessor.beam[2]),
        }



class DataAccessor(object):
    """
    Base class for accessors used with :class:`..sourcefinder.image.ImageData`.

    Data accessors provide a uniform way for the ImageData class (ie, generic
    image representation) to access the various ways in which images may be
    stored (FITS files, arrays in memory, potentially HDF5, etc).
    """

    def __init__(self):
        self.beam = (None, None, None)
        self.wcs = WCS()
        self.inttime = 0.  # seconds
        self.obstime = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.freqbw = None
        self.freqeff = None  # Hertz (? MHz?)
        self.filename = "not set"
        self.data = None
        self.plane = 0
