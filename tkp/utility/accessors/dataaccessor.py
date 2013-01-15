from tkp.utility.coordinates import WCS
import datetime

time_format = "%Y-%m-%d %H:%M:%S.%f"

def extract_metadata(dataaccessor):
    return {
        'tau_time': dataaccessor.tau_time,
        'freq_eff': dataaccessor.freq_eff,
        'freq_bw': dataaccessor.freq_bw,
        'taustart_ts': dataaccessor.taustart_ts,
        'url': dataaccessor.url,
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
        self.wcs = WCS()
        self.data = None

        self.beam = None # (bmaj (px), bmin (px), bpa (rad))
        self.tau_time = None  # integration seconds
        self.taustart_ts = None
        self.freq_bw = None
        self.freq_eff = None  # Hertz (? MHz?)
        self.subbandwidth = None
        self.url = None
        self.centre_ra = None
        self.centre_decl = None
        self.antenna_set = None
        self.subbands = None
        self.channels = None
        self.ncore = None
        self.nremote = None
        self.nintl = None
        self.position = None