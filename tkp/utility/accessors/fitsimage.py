
import numpy
import pytz
import datetime
import dateutil.parser
import logging
import warnings
import re

import pyfits

from tkp.utility.accessors.beam import degrees2pixels
from tkp.utility.accessors.common import parse_pixelsize
from tkp.utility.accessors.dataaccessor import DataAccessor
from tkp.utility.coordinates import WCS


logger = logging.getLogger(__name__)

class FitsImage(DataAccessor):
    """
    Use PyFITS to pull image data out of a FITS file.

    Provide standard attributes, as per :class:`DataAccessor`. Also, if we're
    passed a request for an unknown attribute, we try to pull it out of the
    FITS header.
    If beam info is not present in the header, it HAS to be provided as a
    tuple: (bmaj, bmin, bpa) in degrees.
    """
    def __init__(self, url, plane=None, beam=None, hdu=0):
        """
        Args:
          - url: location of FITS file
          - beam: (optional) beam parameters in degrees, in the form 
            (bmaj, bmin, bpa). Will attempt to read from header if
            not supplied.
        """
        # NB: pyfits bogs down reading parameters from FITS files with very
        # long headers. This code should run in a fraction of a second on most
        # files, but can take several seconds given a huge header.
        super(FitsImage, self).__init__()  # Set defaults
        self.url = url
        self.beam = beam

        hdulist = pyfits.open(url)
        hdu = hdulist[hdu]
        self.header = hdu.header.copy()
        self.telescope = self.header['TELESCOP']
        self.data = read_data(hdu, plane)
        hdulist.close()

        self.wcs = parse_coordinates(self.header)
        self.pixelsize = parse_pixelsize(self.wcs)
        self.centre_ra, self.centre_decl = calculate_phase_centre(self.data.shape,
                                                                  self.wcs)
        self.freq_eff, self.freq_bw = parse_frequency(self.header)

        if beam:
            (bmaj, bmin, bpa) = beam
            self.beam = degrees2pixels(bmaj, bmin, bpa,
                                       self.pixelsize[0], self.pixelsize[1])
        else:
            self.beam = parse_beam(self.header, self.pixelsize)

        self.taustart_ts, self.tau_time = parse_times(self.header)


#------------------------------------------------------------------------------
# The following functions are all fairly class-specific in practice, 
# but can be defined simply, without state, so we might as well:
# It's slightly easier to test this way, we might end up re-using them,
# and it makes explicit that they are not overridden by some child class.
# It's also, arguably, easier to follow.
#------------------------------------------------------------------------------

def read_data(hdu, plane):
    """
    Read and store data from our FITS file.

    NOTE: PyFITS reads the data into an array indexed as [y][x]. We
    take the transpose to make this more intuitively reasonable and
    consistent with (eg) ds9 display of the FitsFile. Transpose back
    before viewing the array with RO.DS9, saving to a FITS file,
    etc.
    """
    data = numpy.float64(hdu.data.squeeze())
    if plane is not None and len(data.shape) > 2:
        data = data[plane].squeeze()
    n_dim = len(data.shape)
    if n_dim != 2:
        logger.warn("Loaded datacube with %s dimensions, assuming Stokes I and taking plane 0" % n_dim)
        data = data[0, :, :]
    data = data.transpose()
    return data

def parse_coordinates(header):
    """Returns a WCS object"""
    wcs = WCS()
    try:
        wcs.crval = header['crval1'], header['crval2']
        wcs.crpix = header['crpix1'], header['crpix2']
        wcs.cdelt = header['cdelt1'], header['cdelt2']
    except KeyError:
        logger.warn("Coordinate system not specified in FITS")
        raise
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
        # Blank values default to degrees.
        logger.warning("WCS units unknown; using defaults")
        wcs.cunit = '', ''

    wcs.wcsset()
    return wcs


def calculate_phase_centre(data_shape, wcs):
        x, y = data_shape
        centre_ra, centre_decl = wcs.p2s((x / 2, y / 2))
        return centre_ra, centre_decl


def parse_frequency(header):
        """
        Set some 'shortcut' variables for access to the frequency parameters
        in the FITS file header.

        @param hdulist: hdulist to parse
        @type hdulist: hdulist
        """
        freq_eff = None
        freq_bw = None
        try:
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
            logger.warn("Frequency not specified in FITS")
        return freq_eff, freq_bw

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

def parse_beam(header, pixelsize):
    """Read and return the beam properties bmaj, bmin and bpa values from
    the fits header.
    
    Returns: 
      - Beam parameters, (semimajor, semiminor, parallactic angle) 
        in (pixels,pixels, radians)  
    """
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

    beam = degrees2pixels(bmaj, bmin, bpa, pixelsize[0], pixelsize[1])
    return beam

def parse_times(header):
    """Returns: 
      - taustart_ts: tz naive (implicit UTC) datetime at start of observation.
      - tau_time: Integration time, in seconds
    """
    # Attempt to do something sane with timestamps.
    try:
        start = parse_start_time(header)
    except KeyError:
        #If no start time specified, give up:
        logger.warn("Timestamp not specified in FITS file;"
                    " using 'now' with dummy (zero-valued) integration time.")
        return datetime.datetime.now(), 0.

    try:
        end = dateutil.parser.parse(header['end_utc'])
    except KeyError:
        logger.warn("End time not specified or unreadable,"
                    "using dummy (zero-valued) integration time")
        end = start

    delta = end - start
    # In Python 2.7, we can use delta.total_seconds instead
    tau_time = (delta.days * 86400 + delta.seconds +
                    delta.microseconds / 1e6)

    #For simplicity, the database requires naive datetimes (implicit UTC)
    #So we convert to UTC and then drop the timezone:
    try:
        timezone = pytz.timezone(header['timesys'])
        start_w_tz = start.replace(tzinfo=timezone)
        start_utc = pytz.utc.normalize(start_w_tz.astimezone(pytz.utc))
        return start_utc.replace(tzinfo=None), tau_time
    except (pytz.UnknownTimeZoneError, KeyError):
        logger.debug("Timezone not specified in FITS file: assuming UTC.")
        return start, tau_time


def parse_start_time(header):
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


