import abc
import logging
import warnings

logger = logging.getLogger(__name__)

class DataAccessor(object):
    __metaclass__ = abc.ABCMeta
    """
    Base class for accessors used with :class:`..sourcefinder.image.ImageData`.

    Data accessors provide a uniform way for the ImageData class (ie, generic
    image representation) to access the various ways in which images may be
    stored (FITS files, arrays in memory, potentially HDF5, etc).

    This class cannot be instantiated directly, but should be subclassed and
    the abstract properties provided. Note that all abstract properties are
    required to provide a valid accessor.

    Additional properties may also be provided by subclasses. However, Trap
    components are required to degrade gracefully in the absence of this
    optional properties.
    """
    @abc.abstractproperty
    def beam(self):
        """
        Restoring beam. Tuple of three floats: semi-major axis (in pixels),
        semi-minor axis (pixels) and position angle (radians).
        """

    @abc.abstractproperty
    def centre_ra(self):
        """
        Right ascension at the central pixel of the image. J2000 decimal
        degrees.
        """

    @abc.abstractproperty
    def centre_decl(self):
        """
        Declination at the central pixel of the image. J2000 decimal degrees.
        """

    @abc.abstractproperty
    def data(self):
        """
        Two dimensional numpy.ndarray of floating point pixel values.
        TODO: Definitive statement on orientation/transposing.
        """

    @abc.abstractproperty
    def freq_bw(self):
        """
        The frequency bandwidth of this image in Hz.
        """

    @abc.abstractproperty
    def freq_eff(self):
        """
        Effective frequency of the image in Hz. That is, the mean frequency of
        all the visibility data which comprises this image.
        """

    @abc.abstractproperty
    def pixelsize(self):
        """
        (x, y) tuple representing the size of a pixel along each axis in units
        of degrees.
        """

    @abc.abstractproperty
    def tau_time(self):
        """
        Total time on sky in seconds.
        """

    @abc.abstractproperty
    def taustart_ts(self):
        """
        Timestamp of the first integration which constitutes part of this
        image. MJD in seconds.
        """

    @abc.abstractproperty
    def url(self):
        """
        A (string) URL representing the location of the image at time of
        processing.
        """

    @abc.abstractproperty
    def wcs(self):
        """
        An instance of tkp.coordinates.WCS.
        """

    def extract_metadata(self):
        """
        Massage the class attributes into a flat dictionary with
        database-friendly values.

        While rather tedious, this is easy to serialize and store separately
        to the actual image data.

        May be extended by subclasses to return additional data.
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
            'centre_ra': self.centre_ra,
            'centre_decl': self.centre_decl,
            'deltax': self.pixelsize[0],
            'deltay': self.pixelsize[1],
        }
