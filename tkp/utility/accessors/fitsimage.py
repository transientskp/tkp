import datetime
import numpy
import pytz
import dateutil.parser
import logging
import warnings
import re

import pyfits

from tkp.utility.accessors.beam import degrees2pixels
from tkp.utility.accessors.dataaccessor import DataAccessor, parse_pixel_scale
from tkp.utility.coordinates import WCS


logger = logging.getLogger(__name__)


# AIPS FITS file; stored in the history section
beam_regex = re.compile(r'''
    BMAJ
    \s*=\s*
    (?P<bmaj>[-\d\.eE]+)
    \s*
    BMIN
    \s*=\s*
    (?P<bmin>[-\d\.eE]+)
    \s*
    BPA
    \s*=\s*
    (?P<bpa>[-\d\.eE]+)
    ''', re.VERBOSE)


class FitsImage(DataAccessor):
    """
    Use PyFITS to pull image data out of a FITS file.

    Provide standard attributes, as per :class:`DataAccessor`. Also, if we're
    passed a request for an unknown attribute, we try to pull it out of the
    FITS header.
    If beam info is not present in the header, it HAS to be provided as a
    tuple: (bmaj, bmin, bpa) in degrees.
    """
    def __init__(self, source, plane=False, beam=False, hdu=0):
        # NB: pyfits bogs down reading parameters from FITS files with very
        # long headers. This code should run in a fraction of a second on most
        # files, but can take several seconds given a huge header.
        super(FitsImage, self).__init__()  # Set defaults

        self.plane = plane

        self.url = source
        hdulist = pyfits.open(source)
        hdu = hdulist[hdu]

        self.header = hdu.header.copy()
        self._read_data(hdu)
        self._coordparse(hdu)
        self.pixel_scale = parse_pixel_scale(self.wcs)
        self._othersparse(hdu)
        self._freqparse(hdu)

        if not beam:
            self._beamsizeparse(hdu)
        else:
            (bmaj, bmin, bpa) = beam
            deltax = self.wcs.cdelt[0]
            deltay = self.wcs.cdelt[1]
            self.beam = degrees2pixels(bmaj, bmin, bpa, deltax, deltay)
            self.pixelsize = (deltax, deltay)

        self._timeparse(hdu)

        hdulist.close()

        # check if everything is okay!
        self.ready()


    def _timeparse(self, hdu):
        # Attempt to do something sane with timestamps.

        timezone = pytz.utc
        try:
            #First parse the timestamp
            try:
                timestamp = dateutil.parser.parse(hdu.header['date-obs'])
            except AttributeError:
                # Maybe it's a float, Westerbork-style?
                if isinstance(hdu.header['date-obs'], float):
                    logger.warn("Non-standard date specified in FITS file!")
                    frac, year = numpy.modf(hdu.header['date-obs'])
                    timestamp = datetime.datetime(int(year), 1, 1)
                    delta = datetime.timedelta(365.242199 * frac)
                    timestamp += delta
                else:
                    raise KeyError("Timestamp in fits file unreadable")
            #Now try and figure out the timezone
            try:
                timezone = pytz.timezone(hdu.header['timesys'])
            except (pytz.UnknownTimeZoneError, KeyError):
                logger.debug(
                    "Timezone not specified in FITS file: assuming UTC already")
            timestamp = timestamp.replace(tzinfo=timezone)
            self.utc = pytz.utc.normalize(timestamp.astimezone(pytz.utc))
        except KeyError:
            logger.warn("Timestamp not specified in FITS file; using now")
            self.utc = datetime.datetime.now().replace(tzinfo=pytz.utc)
        #For simplicity, the database requires naive datetimes, we assume these
        # all refer implicitly to UTC:
        self.taustart_ts = self.utc.replace(tzinfo=None)
        try:
            endtime = dateutil.parser.parse(hdu.header['end_utc'])
            endtime = endtime.replace(tzinfo=timezone)
            self.utc_end = pytz.utc.normalize(endtime.astimezone(pytz.utc))
            delta = self.utc_end - self.utc
            # In Python 2.7, we can use delta.total_seconds instead
            self.tau_time = (delta.days*86400 + delta.seconds +
                            delta.microseconds/1e6)
        except KeyError:
            logger.warn("End time not specified or unreadable")
            self.tau_time = 0.


        # check if everything is okay!
        self.ready()

    def _coordparse(self, hdu):
        """Set some 'shortcut' variables for access to the coordinate
        parameters in the FITS file header.
        """
        # These are maintained for legacy reasons -- better to access by
        # header name through __getattr__?
        self.wcs = WCS()
        header = hdu.header
        try:
            self.wcs.crval = header['crval1'], header['crval2']
            self.wcs.crpix = header['crpix1'], header['crpix2']
            self.wcs.cdelt = header['cdelt1'], header['cdelt2']
        except KeyError:
            logger.warn("Coordinate system not specified in FITS")
            raise
        try:
            self.wcs.ctype = header['ctype1'], header['ctype2']
        except KeyError:
            self.wcs.ctype = 'unknown', 'unknown'
        try:
            self.wcs.crota = float(header['crota1']), float(header['crota2'])
        except KeyError:
            self.wcs.crota = 0., 0.
        try:
            self.wcs.cunit = header['cunit1'], header['cunit2']
        except KeyError:
            # Blank values default to degrees.
            logger.warning("WCS units unknown; using defaults")
            self.wcs.cunit = '', ''

        self.wcs.wcsset()

        x, y = self.data.shape
        self.centre_ra, self.centre_decl = self.wcs.p2s((x/2, y/2))



    def _freqparse(self, hdu):
        """
        Set some 'shortcut' variables for access to the frequency parameters
        in the FITS file header.

        @param hdulist: hdulist to parse
        @type hdulist: hdulist
        """
        try:
            if hdu.header['TELESCOP'] == 'LOFAR':
                self.freq_eff = hdu.header['RESTFRQ']
                self.freq_bw = 0.0 # TODO: We need this in the header as well...
            else:
                if hdu.header['ctype3'] in ('FREQ', 'VOPT'):
                    self.freq_eff = hdu.header['crval3']
                    self.freq_bw = hdu.header['cdelt3']
                elif hdu.header['ctype4'] in ('FREQ', 'VOPT'):
                    self.freq_eff = hdu.header['crval4']
                    self.freq_bw = hdu.header['cdelt4']
                else:
                    self.freq_eff = hdu.header['restfreq']
                    self.freq_bw = 0.0
        except KeyError:
            logger.warn("Frequency not specified in FITS")



    def _read_data(self, hdu):
        """
        Read and store data from our FITS file.

        NOTE: PyFITS reads the data into an array indexed as [y][x]. We
        take the transpose to make this more intuitively reasonable and
        consistent with (eg) ds9 display of the FitsFile. Transpose back
        before viewing the array with RO.DS9, saving to a FITS file,
        etc.
        """
        data = numpy.float64(hdu.data.squeeze())
        if not isinstance(self.plane, bool) and len(data.shape) > 2:
            data = data[self.plane].squeeze()
        planes = len(data.shape)
        if planes != 2:
            logger.warn("received datacube with %s planes, assuming Stokes I and taking plane 0" % planes)
            data=data[0,:,:]
        self.data = data.transpose()


    def _beamsizeparse(self, hdu):
        """Read and return the beam properties bmaj, bmin and bpa values from
        the fits header

        Only Miriad and AIPS cleaned images can be handled by this method.
        If no (key) values can be read we use the WENSS values.
        """

        header = hdu.header
        bmaj, bmin, bpa = None, None, None
        try:
            # MIRIAD FITS file
            bmaj = header['BMAJ']
            bmin = header['BMIN']
            bpa = header['BPA']
        except KeyError:

            for i, key in enumerate(header.ascardlist().keys()):
                if key == 'HISTORY':
                    results = beam_regex.search(header[i])
                    if results:
                        bmaj, bmin, bpa = [float(results.group(key)) for
                                           key in ('bmaj', 'bmin', 'bpa')]
                        break
        if bmaj is None:
            msg = "Can't extract beam information from image %s" % self.url
            warnings.warn(msg)
            logging.error(msg)
            return

        deltax = self.wcs.cdelt[0]
        deltay = self.wcs.cdelt[1]
        self.beam = degrees2pixels(bmaj, bmin, bpa, deltax, deltay)
        self.pixelsize = (deltax, deltay)


    def _othersparse(self, hdu):
        """ Parse missing stuff from headers that should be injected by trap-inject
        """
        header = hdu.header

        # this may have been set already by _timeparse, but if defined here
        # it is set by our inject script and should be used
        if 'TAU_TIME' in header:
            self.tau_time = header['TAU_TIME']

        self.antenna_set = header.get('ANTENNA', None)
        self.subbands = header.get('SUBBANDS', None)
        self.channels = header.get('CHANNELS', None)
        self.ncore = header.get('NCORE', None)
        self.nremote = header.get('NREMOTE', None)
        self.nintl = header.get('NINTL', None)
        self.position = header.get('POSITION', None)
        self.subbandwidth = header.get('SUBBANDW', None)
