import abc
import logging
from tkp.quality.statistics import rms_with_clipped_subregion

logger = logging.getLogger(__name__)


class DataAccessor(object):
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        """
        Base class for accessors used with
        :class:`tkp.sourcefinder.image.ImageData`.

        Data accessors provide a uniform way for the ImageData class (ie,
        generic image representation) to access the various ways in which
        images may be stored (FITS files, arrays in memory, potentially HDF5,
        etc).

        This class cannot be instantiated directly, but should be subclassed
        and the abstract properties provided. Note that all abstract
        properties are required to provide a valid accessor.

        Additional properties may also be provided by subclasses. However,
        TraP components are required to degrade gracefully in the absence of
        this optional properties.
        """
        # Initialise the `sigma` and `f` properties used for calculating the
        # RMS value of the data. See `tkp.quality.statistics` for details.
        self.sigma = 3
        self.f = 4


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

    def rms_qc(self):
        """
        RMS for quality-control.

        Root mean square value calculated from central region of this image.
        We sigma-clip the input-data in an attempt to exclude source-pixels
        and keep only background-pixels.
        """
        return rms_with_clipped_subregion(self.data, sigma=self.sigma, f=self.f)

    def extract_metadata(self):
        """
        Massage the class attributes into a flat dictionary with
        database-friendly values.

        While rather tedious, this is easy to serialize and store separately
        to the actual image data.

        May be extended by subclasses to return additional data.
        """
        # some values are casted to a standard float since MonetDB cannot
        # handle numpy.float64
        return {
            'tau_time': self.tau_time,
            'freq_eff': self.freq_eff,
            'freq_bw': self.freq_bw,
            'taustart_ts': self.taustart_ts,
            'url': self.url,
            'beam_smaj_pix': self.beam[0],
            'beam_smin_pix': self.beam[1],
            'beam_pa_rad': self.beam[2],
            'centre_ra': self.centre_ra,
            'centre_decl': self.centre_decl,
            'deltax': self.pixelsize[0],
            'deltay': self.pixelsize[1],
            'rms_qc': self.rms_qc(),
        }
