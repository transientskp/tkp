import datetime
from tkp.utility.accessors import DataAccessor
import pyfits
import numpy
from tkp.utility.coordinates import WCS
import pytz
import dateutil.parser
import logging
import re

logger = logging.getLogger(__name__)

class FITSImage(DataAccessor):
    """
    Use PyFITS to pull image data out of a FITS file.

    Provide standard attributes, as per :class:`DataAccessor`. Also, if we're
    passed a request for an unknown attribute, we try to pull it out of the
    FITS header.
    If beam info is not present in the header, it HAS to be provided as a
    tuple: (bmaj, bmin, bpa).
    """
    def __init__(self, source, plane=False, beam=False, hdu=0):
        # NB: pyfits bogs down reading parameters from FITS files with very
        # long headers. This code should run in a fraction of a second on most
        # files, but can take several seconds given a huge header.
        super(FITSImage, self).__init__()  # Set defaults

        self.plane = plane

        # filename attribute is required by db_image_from_accessor(), below.
        if isinstance(source, basestring):
            self.filename = source
            hdulist = pyfits.open(source)
            hdu = hdulist[hdu]
        elif isinstance(source, pyfits.core.HDUList):
            self.filename = source.filename()
            hdu = source[hdu]
        elif isinstance(source, pyfits.PrimaryHDU) or isinstance(source, pyfits.ImageHDU):
            self.filename = source.fileinfo()['file'].name
            hdu = source

        self.header = hdu.header.copy()
        self._read_data(hdu)

        self._coordparse(hdu)
        try:
            self._freqparse(hdu)
        except KeyError:
            # Never mind frequency information then
            # But be aware when storing this in the database
            pass
        if not beam:
            self._beamsizeparse(hdu)
        else:
            super(FITSImage, self)._beamsizeparse(beam[0], beam[1], beam[2])

        # Attempt to do something sane with timestamps.
        timezone = pytz.utc
        try:
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
            try:
                timezone = pytz.timezone(hdu.header['timesys'])
            except (pytz.UnknownTimeZoneError, KeyError):
                logger.debug(
                    "Timezone not specified in FITS file: assuming UTC")
            timestamp = timestamp.replace(tzinfo=timezone)
            self.utc = pytz.utc.normalize(timestamp.astimezone(pytz.utc))
        except KeyError:
            logger.warn("Timestamp not specified in FITS file; using now")
            self.utc = datetime.datetime.now().replace(tzinfo=pytz.utc)
        self.obstime = self.utc
        try:
            endtime = dateutil.parser.parse(hdu.header['end_utc'])
            endtime = endtime.replace(tzinfo=timezone)
            self.utc_end = pytz.utc.normalize(endtime.astimezone(pytz.utc))
            delta = self.utc_end - self.utc
            # In Python 2.7, we can use delta.total_seconds instead
            self.inttime = (delta.days*86400 + delta.seconds +
                            delta.microseconds/1e6)
        except KeyError:
            logger.warn("End time not specified or unreadable")
            self.inttime = 0.

        if isinstance(source, basestring):
            # If we opened the FITS file ourselves, we'd better ensure it's
            # closed
            hdulist.close()

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
            self.wcs.cunits = header['cunit1'], header['cunit2']
        except KeyError:
            self.wcs.cunits = 'unknown', 'unknown'

        self.wcs.wcsset()
        self.pix_to_position = self.wcs.p2s

    def _freqparse(self, hdu):
        """
        Set some 'shortcut' variables for access to the frequency parameters
        in the FITS file header.

        @param hdulist: hdulist to parse
        @type hdulist: hdulist
        """
        try:
            if hdu.header['TELESCOP'] == 'LOFAR':
                self.freqeff = hdu.header['RESTFRQ']
                self.freqbw = 0.0 # TODO: We need this in the header as well...
            else:
                if hdu.header['ctype3'] in ('FREQ', 'VOPT'):
                    self.freqeff = hdu.header['crval3']
                    self.freqbw = hdu.header['cdelt3']
                elif hdu.header['ctype4'] in ('FREQ', 'VOPT'):
                    self.freqeff = hdu.header['crval4']
                    self.freqbw = hdu.header['cdelt4']
                else:
                    self.freqeff = hdu.header['restfreq']
                    self.freqbw = 0.0
        except KeyError:
            logger.warn("Frequency not specified in FITS")

    def get_header(self):
        # Preserved for API compatibility.
        return self.header

    def _read_data(self, hdu):
        """
        Read and store data from our FITS file.

        NOTE: PyFITS reads the data into an array indexed as [y][x]. We
        take the transpose to make this more intuitively reasonable and
        consistent with (eg) ds9 display of the FITSImage. Transpose back
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
            # AIPS FITS file; stored in the history section
            regex = re.compile(r'''
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
            for i, key in enumerate(header.ascardlist().keys()):
                if key == 'HISTORY':
                    results = regex.search(header[i])
                    if results:
                        bmaj, bmin, bpa = [float(results.group(key)) for
                                           key in ('bmaj', 'bmin', 'bpa')]
                        break
        if bmaj is None:
            # if not provided and not found we are lost and
            # have to bomb out.
            raise ValueError("""\
Basic processing is impossible without adequate information about the \
resolution element.""")
        super(FITSImage, self)._beamsizeparse(bmaj, bmin, bpa)

    def __getattr__(self, attrname):
        """
        Read FITS header for unknown attributes.

        If they're not found, throw an AttributeError.

        @type attrname: string
        """
        if attrname in self.header:
            return self.header[attrname]
        raise AttributeError(attrname)


class FitsFile(FITSImage):
    pass
