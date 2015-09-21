
import numpy
import pytz
import datetime
import dateutil.parser
import logging
import re

import astropy.io.fits as pyfits

from tkp.accessors.dataaccessor import DataAccessor
from tkp.utility.coordinates import WCS

logger = logging.getLogger(__name__)

class FitsImage(DataAccessor):
    """
    Use PyFITS to pull image data out of a FITS file.

    Provide standard attributes, as per :class:`DataAccessor`. In addition, we
    provide a ``telescope`` attribute if the FITS file has a ``TELESCOP``
    header.
    """
    def __init__(self, url, plane=None, beam=None, hdu_index=0):
        super(FitsImage, self).__init__()
        self.url = url
        self.header = self._get_header(hdu_index)
        self.wcs = self.parse_coordinates()
        self.data = self.read_data(hdu_index, plane)
        self.taustart_ts, self.tau_time = self.parse_times()
        self.freq_eff, self.freq_bw = self.parse_frequency()
        self.pixelsize = self.parse_pixelsize()
        if beam:
            (bmaj, bmin, bpa) = beam
        else:
            (bmaj, bmin, bpa) = self.parse_beam()
        self.beam = self.degrees2pixels(
                bmaj, bmin, bpa, self.pixelsize[0], self.pixelsize[1]
            )
        self.centre_ra, self.centre_decl = self.calculate_phase_centre()

        # Bonus attribute
        if 'TELESCOP' in self.header:
            self.telescope = self.header['TELESCOP']

    def _get_header(self, hdu_index):
        with pyfits.open(self.url) as hdulist:
            hdu = hdulist[hdu_index]
        return hdu.header.copy()



    def read_data(self, hdu_index, plane):
        """
        Read and store data from our FITS file.

        NOTE: PyFITS reads the data into an array indexed as [y][x]. We
        take the transpose to make this more intuitively reasonable and
        consistent with (eg) ds9 display of the FitsFile. Transpose back
        before viewing the array with RO.DS9, saving to a FITS file,
        etc.
        """
        with pyfits.open(self.url) as hdulist:
            hdu = hdulist[hdu_index]
            data = numpy.float64(hdu.data.squeeze())
        if plane is not None and len(data.shape) > 2:
            data = data[plane].squeeze()
        n_dim = len(data.shape)
        if n_dim != 2:
            logger.warn("Loaded datacube with %s dimensions, assuming Stokes I and taking plane 0" % n_dim)
            data = data[0, :, :]
        data = data.transpose()
        return data


    def parse_coordinates(self):
        """Returns a WCS object"""
        header = self.header
        wcs = WCS()
        try:
            wcs.crval = header['crval1'], header['crval2']
            wcs.crpix = header['crpix1'] - 1, header['crpix2'] - 1
            wcs.cdelt = header['cdelt1'], header['cdelt2']
        except KeyError:
            msg = "Coordinate system not specified in FITS"
            logger.error(msg)
            raise TypeError(msg)
        try:
            wcs.ctype = header['ctype1'], header['ctype2']
        except KeyError:
            wcs.ctype = 'unknown', 'unknown'
        try:
            wcs.crota = float(header['crota1']), float(header['crota2'])
        except KeyError:
            wcs.crota = 0., 0.
        try:
            wcs.cunit = header['cunit1'], header['cunit2']
        except KeyError:
            # The "Definition of the Flexible Image Transport System", version
            # 3.0, tells us that "units for celestial coordinate systems defined
            # in this Standard must be degrees", so we assume that if nothing else
            # is specifiedj
            msg = "WCS units unknown; using degrees"
            logger.warning(msg)
            wcs.cunit = 'deg', 'deg'
        return wcs


    def calculate_phase_centre(self):
        x, y = self.data.shape
        centre_ra, centre_decl = self.wcs.p2s((x / 2, y / 2))
        return centre_ra, centre_decl



    def parse_frequency(self):
        """
        Set some 'shortcut' variables for access to the frequency parameters
        in the FITS file header.

        @param hdulist: hdulist to parse
        @type hdulist: hdulist
        """
        freq_eff = None
        freq_bw = None
        try:
            header = self.header
            if header['TELESCOP'] == 'LOFAR':
                freq_eff = header['RESTFRQ']
                freq_bw = header['RESTBW']
            else:
                if header['ctype3'] in ('FREQ', 'VOPT'):
                    freq_eff = header['crval3']
                    freq_bw = header['cdelt3']
                elif header['ctype4'] in ('FREQ', 'VOPT'):
                    freq_eff = header['crval4']
                    freq_bw = header['cdelt4']
                else:
                    freq_eff = header['restfreq']
                    freq_bw = 0.0
        except KeyError:
            msg = "Frequency not specified in FITS"
            logger.error(msg)
            raise TypeError(msg)

        return freq_eff, freq_bw






    def parse_beam(self):
        """Read and return the beam properties bmaj, bmin and bpa values from
        the fits header.

        Returns:
          - Beam parameters, (semimajor, semiminor, position angle)
            in (pixels, pixels, radians)
        """
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

        bmaj, bmin, bpa = None, None, None
        header = self.header
        try:
            # MIRIAD FITS file
            bmaj = header['BMAJ']
            bmin = header['BMIN']
            bpa = header['BPA']
        except KeyError:

            def get_history(hdr):
                """
                Returns all history cards in FITS header hdr as a list of strings.
                """
                return hdr['HISTORY']

            for hist_entry in get_history(header):
                results = beam_regex.search(hist_entry)
                if results:
                    bmaj, bmin, bpa = [float(results.group(key)) for
                                       key in ('bmaj', 'bmin', 'bpa')]
                    break

        return bmaj, bmin, bpa



    def parse_times(self):
        """Returns:
          - taustart_ts: tz naive (implicit UTC) datetime at start of observation.
          - tau_time: Integration time, in seconds
        """
        # Attempt to do something sane with timestamps.
        try:
            start = self.parse_start_time()
        except KeyError:
            #If no start time specified, give up:
            logger.warn("Timestamp not specified in FITS file:"
                        " using 'now' with dummy (zero-valued) integration time.")
            return datetime.datetime.now(), 0.

        try:
            end = dateutil.parser.parse(self.header['end_utc'])
        except KeyError:
            msg = "End time not specified or unreadable"
            logger.warning(msg)
            end = start

        delta = end - start
        tau_time = delta.total_seconds()

        #For simplicity, the database requires naive datetimes (implicit UTC)
        #So we convert to UTC and then drop the timezone:
        try:
            timezone = pytz.timezone(self.header['timesys'])
            start_w_tz = start.replace(tzinfo=timezone)
            start_utc = pytz.utc.normalize(start_w_tz.astimezone(pytz.utc))
            return start_utc.replace(tzinfo=None), tau_time
        except (pytz.UnknownTimeZoneError, KeyError):
            logger.debug("Timezone not specified in FITS file: assuming UTC.")
            return start, tau_time


    def parse_start_time(self):
        """
        Returns:
          - start time of image as an instance of ``datetime.datetime``
        """
        header = self.header
        try:
            start = dateutil.parser.parse(header['date-obs'])
        except AttributeError:
            # Maybe it's a float, Westerbork-style?
            if isinstance(header['date-obs'], float):
                logger.warn("Non-standard date specified in FITS file!")
                frac, year = numpy.modf(header['date-obs'])
                start = datetime.datetime(int(year), 1, 1)
                delta = datetime.timedelta(365.242199 * frac)
                start += delta
            else:
                raise KeyError("Timestamp in fits file unreadable")
        return start


