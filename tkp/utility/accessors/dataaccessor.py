from tkp.utility.coordinates import WCS
import datetime

time_format = "%Y-%m-%d %H:%M:%S.%f"

def extract_metadata(dataaccessor):
    return {
        'tau_time': dataaccessor.tau_time,
        'freq_eff': dataaccessor.freq_eff,
        'freq_bw': dataaccessor.freq_bw,
        'taustart_ts': dataaccessor.taustart_ts.strftime(time_format),
        'url': dataaccessor.url,
        'band': 0,    # not yet clearly defined
        'bsmaj': float(dataaccessor.beam[0]), ## NB We must cast to a standard python float
        'bsmin': float(dataaccessor.beam[1]), ## as Monetdb converter cannot handle numpy.float64
        'bpa': float(dataaccessor.beam[2]),
        'centre_ra': dataaccessor.centre_ra,
        'centre_decl': dataaccessor.centre_decl,
        'subbandwidth': dataaccessor.subbandwidth,
        'antenna_set': dataaccessor.antenna_set,
        'subbands': dataaccessor.subbands,
        'channels': dataaccessor.channels,
        'ncore': dataaccessor.ncore,
        'nremote': dataaccessor.nremote,
        'nintl': dataaccessor.nintl,
        'position': dataaccessor.position,
    }

class DataAccessor(object):
    """
    Base class for accessors used with :class:`..sourcefinder.image.ImageData`.

    Data accessors provide a uniform way for the ImageData class (ie, generic
    image representation) to access the various ways in which images may be
    stored (FITS files, arrays in memory, potentially HDF5, etc).
    """

    def __init__(self):
        self.beam = (None, None, None) # bmaj (px), bmin (px), bpa (rad)
        self.wcs = WCS()
        self.tau_time = 0.  # integration seconds
        self.taustart_ts = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.freq_bw = 0.
        self.freq_eff = 0.  # Hertz (? MHz?)
        self.subbandwidth = 0.
        self.url = "not set"
        self.data = None
        self.centre_ra = 0
        self.centre_decl = 0
        self.antenna_set = None
        self.subbands = 0
        self.channels = 0
        self.ncore = 0
        self.nremote = 0
        self.nintl = 0
        self.position = None
