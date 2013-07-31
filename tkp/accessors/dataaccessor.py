import logging
import warnings
logger = logging.getLogger(__name__)

time_format = "%Y-%m-%d %H:%M:%S.%f"

class DataAccessor(object):
    """
    Base class for accessors used with :class:`..sourcefinder.image.ImageData`.

    Data accessors provide a uniform way for the ImageData class (ie, generic
    image representation) to access the various ways in which images may be
    stored (FITS files, arrays in memory, potentially HDF5, etc).

    The list of attributes represents the minimum working set we expect from
    input images.
    """

    def __init__(self):
        ## Note, these get shipped off to the database insertion routine directly,
        ## hence their units should match the database schema.
        self.telescope = None #Telescope name
        self.wcs = None #tkp.coordinates.WCS object
        self.data = None #Data array
        self.url = None #e.g. Filename
        self.pixelsize = None # (x,y) tuple, units of degrees
        self.tau_time = None  # integration time in seconds
        self.taustart_ts = None #observation start time
        self.centre_ra = None #Degrees (J2000)
        self.centre_decl = None #Degrees (J2000)
        self.freq_eff = None  # Hertz
        self.freq_bw = None # Hertz
        self.beam = None # (bmaj (px), bmin (px), bpa (rad))


    def not_set(self):
        """returns list of all params that are not set"""
        return [x for x in dir(self) if  not x.startswith('_') and getattr(self, x) == None]

    def ready(self):
        """checks if this accessor if ready for everything, if not give warning
        """
        not_set = self.not_set()
        if not_set:
            msg = "%s not set for image %s" % (", ".join(not_set), self.url)
            logging.error(msg)
            warnings.warn(msg)
            return False
        return True

    def extract_metadata(self):
        """Massage the class attributes into a flat dictionary with
        database-friendly values.

        While rather tedious, this is easy to
        serialize and store separately to the actual image data.

        NB. Gets extended by subclasses to return additional data.
        """
        return {
            'tau_time': self.tau_time,
            'freq_eff': self.freq_eff,
            'freq_bw': self.freq_bw,
            'taustart_ts': self.taustart_ts,
            'url': self.url,
            'beam_smaj_pix': float(self.beam[0]), ## NB We must cast to a standard python float
            'beam_smin_pix': float(self.beam[1]), ## as Monetdb converter cannot handle numpy.float64
            'beam_pa_rad': float(self.beam[2]),
            'centre_ra': self.centre_ra, #J2000 Degrees
            'centre_decl': self.centre_decl, #J2000 Degrees
            'deltax': self.pixelsize[0],
            'deltay': self.pixelsize[1],
        }

