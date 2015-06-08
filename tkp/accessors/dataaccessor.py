import logging
from tkp.quality.statistics import rms_with_clipped_subregion
from tkp.accessors.requiredatts import RequiredAttributesMetaclass
from math import degrees, sqrt, sin, pi, cos

logger = logging.getLogger(__name__)

class DataAccessor(object):
    __metaclass__ = RequiredAttributesMetaclass

    _required_attributes = [
            'beam',
            'centre_ra',
            'centre_decl',
            'data',
            'freq_bw',
            'freq_eff',
            'pixelsize',
            'tau_time',
            'taustart_ts',
            'url',
            'wcs',
        ]

    def __init__(self):
        # Sphinx only picks up the class docstring if it's under an __init__
        # *le sigh*
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

        The required attributes are as follows:

        Attributes:
            beam (tuple): Restoring beam. Tuple of three floats:
                semi-major axis (in pixels), semi-minor axis (pixels)
                and position angle (radians).
            centre_ra (float): Right ascension at the central pixel of the image.
                Units of J2000 decimal degrees.
            centre_decl (float): Declination at the central pixel of the image.
                Units of J2000 decimal degrees.
            data(numpy.ndarray): Two dimensional numpy.ndarray of floating point
                pixel values.
                (TODO: Definitive statement on orientation/transposing.)
            freq_bw(float): The frequency bandwidth of this image in Hz.
            freq_eff(float): Effective frequency of the image in Hz.
                That is, the mean frequency of all the visibility data which
                comprises this image.
            pixelsize(tuple): (x, y) tuple representing the size of a pixel
                along each axis in units of degrees.
            tau_time(float): Total time on sky in seconds.
            taustart_ts(float): Timestamp of the first integration which
                constitutes part of this image. MJD in seconds.
            url(string): A (string) URL representing the location of the image
                at time of processing.
            wcs(:class:`tkp.utility.coordinates.WCS`): An instance of
                :py:class:`tkp.utility.coordinates.WCS`,
                describing the mapping from data pixels to sky-coordinates.

        The class also provides some common functionality:
        static methods used for parsing datafiles, and an 'extract_metadata'
        function which provides key info in a simple dict format.
        """

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
        }

    def parse_pixelsize(self):
        """

        Returns:
          - deltax: pixel size along the x axis in degrees
          - deltay: pixel size along the x axis in degrees

        """
        wcs = self.wcs
        # Check that pixels are square
        # (Would have to be pretty strange data for this not to be the case)
        assert wcs.cunit[0] == wcs.cunit[1]
        if wcs.cunit[0] == "deg":
            deltax = wcs.cdelt[0]
            deltay = wcs.cdelt[1]
        elif wcs.cunit[0] == "rad":
            deltax = degrees(wcs.cdelt[0])
            deltay = degrees(wcs.cdelt[1])
        else:
            raise ValueError("Unrecognised WCS co-ordinate system")

        #NB. What's a reasonable epsilon here?
        eps = 1e-7
        if abs(abs(deltax) - abs(deltay)) > eps:
            raise ValueError("Image WCS header suggests non-square pixels."
                     "This is an untested use case, and may break things -"
                     "specifically the skyregion tracking but possibly other stuff too.")
        return deltax, deltay

    @staticmethod
    def degrees2pixels(bmaj, bmin, bpa, deltax, deltay):
        """
        Convert beam in degrees to beam in pixels and radians.
        For example Fits beam parameters are in degrees.

        Arguments:
          - bmaj:   Beam major axis in degrees
          - bmin:   Beam minor axis in degrees
          - bpa:    Beam position angle in degrees
          - deltax: Pixel size along the x axis in degrees
          - deltay: Pixel size along the y axis in degrees

        Returns:
          - semimaj: Beam semi-major axis in pixels
          - semimin: Beam semi-minor axis in pixels
          - theta:   Beam position angle in radians
        """
        semimaj = (bmaj / 2.) * (sqrt(
            (sin(pi * bpa / 180.)**2) / (deltax**2) +
            (cos(pi * bpa / 180.)**2) / (deltay**2))
        )
        semimin = (bmin / 2.) * (sqrt(
            (cos(pi * bpa / 180.)**2) / (deltax**2) +
            (sin(pi * bpa / 180.)**2) / (deltay**2))
        )
        theta = pi * bpa / 180
        return (semimaj, semimin, theta)

