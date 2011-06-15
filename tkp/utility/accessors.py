#
# LOFAR Transients Key Project
#

# NOTE: use of numpy.squeeze() appears a bad idea, in the case of
# (unlikely, but not impossible) [1, Y] or [X, 1] shaped images...

"""
Data accessors.

These can be used to populate ImageData objects based on some data source
(FITS file, array in memory... etc).
"""
import datetime
import re
import logging
import dateutil.parser
import pytz
from .coordinates import WCS
import pyfits
import numpy


class DataAccessor(object):
    """
    Base class for accessors used with :class:`tkp_lib.image.ImageData`.

    Data accessors provide a uniform way for the ImageData class (ie, generic
    image representation) to access the various ways in which images may be
    stored (FITS files, arrays in memory, potentially HDF5, etc).
    """

    def __init__(self, *args, **kwargs):
        self.beam = kwargs.pop('beam', (None, None, None))
        self.wcs = kwargs.pop('wcs', WCS())
        super(DataAccessor, self).__init__(*args, **kwargs)
        # Set defaults
        self.inttime = 0.  # seconds
        self.obstime = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.freqbw = 0.
        self.freqeff = 0.  # Hertz (? MHz?)

    def _beamsizeparse(self, bmaj, bmin, bpa):
        """Needs beam parameters, no defaults."""

        semimaj = (bmaj / 2.) * (numpy.sqrt(
            (numpy.sin(numpy.pi * bpa / 180.)**2) /
            (self.wcs.cdelt[0]**2) +
            (numpy.cos(numpy.pi * bpa / 180.)**2) /
            (self.wcs.cdelt[1]**2)))
        semimin = (bmin / 2.) * (numpy.sqrt(
            (numpy.cos(numpy.pi * bpa / 180.)**2) /
            (self.wcs.cdelt[0]**2) +
            (numpy.sin(numpy.pi * bpa / 180.)**2) /
            (self.wcs.cdelt[1]**2)))
        theta = numpy.pi * bpa / 180
        self.beam = (semimaj, semimin, theta)


class AIPSppImage(DataAccessor):
    """
    Use pyrap to pull image data out of an AIPS++ table.

    This assumes that all AIPS++ images are structured just like the example
    James Miller-Jones provided me with. This is probably not a good
    assumption...
    """
    def __init__(self, filename, plane=0, beam=None):
        super(AIPSppImage, self).__init__()
        self.filename = filename
        self.plane = plane
        self._coordparse()
        if beam:
            bmaj, bmin, bpa = beam
            self._beamsizeparse(bmaj, bmin, bpa)
        else:
            self.beam = None

    def _get_table(self):
        from pyrap.tables import table
        return table(self.filename, ack=False)

    def _coordparse(self):
        self.wcs = WCS()
        my_coordinates = self._get_table().getkeyword('coords')['direction0']
        self.wcs.crval = my_coordinates['crval']
        self.wcs.crpix = my_coordinates['crpix']
        self.wcs.cdelt = my_coordinates['cdelt']
        ctype = ['unknown', 'unknown']
        # What about other projections?!
        if my_coordinates['projection'] == "SIN":
            if my_coordinates['axes'][0] == "Right Ascension":
                ctype[0] = "RA---SIN"
            if my_coordinates['axes'][1] == "Declination":
                ctype[1] = "DEC--SIN"
        self.wcs.ctype = tuple(ctype)
        # Rotation, units? We better set a default
        self.wcs.crota = (0., 0.)
        self.wcs.cunits = ('unknown', 'unknown')
        # Update WCS
        self.wcs.wcsset()
        self.pix_to_position = self.wcs.p2s

    @property
    def data(self):
        return self._get_table().getcellslice("map", 0,
            [0, self.plane, 0, 0],
            [0, self.plane, -1, -1]
        ).squeeze()

    def __getstate__(self):
        return {"filename": self.filename, "plane": self.plane}

    def __setstate__(self, statedict):
        self.filename = statedict['filename']
        self.plane = statedict['plane']
        self._coordparse()


class FitsFile(DataAccessor):
    """
    Use PyFITS to pull image data out of a FITS file.

    Provide standard attributes, as per :class:`DataAccessor`. Also, if we're
    passed a request for an unknown attribute, we try to pull it out of the
    FITS header.
    If beam info is not present in the header, it HAS to be provided as a
    tuple: (bmaj, bmin, bpa).
    """
    def __init__(self, filename, plane=False, beam=False):
        # NB: pyfits bogs down reading parameters from FITS files with very
        # long headers. This code should run in a fraction of a second on most
        # files, but can take several seconds given a huge header.
        self.filename = filename
        hdulist = pyfits.open(self.filename)

        self._coordparse(hdulist)
        self._freqparse(hdulist)
        if not beam:
            self._beamsizeparse(hdulist)
        else:
            super(FitsFile, self)._beamsizeparse(beam[0], beam[1], beam[2])

        # Attempt to do something sane with timestamps.
        timezone = pytz.utc
        try:
            try:
                timestamp = dateutil.parser.parse(
                    hdulist[0].header['date-obs'])
            except AttributeError:
                # Maybe it's a float, Westerbork-style?
                if isinstance(hdulist[0].header['date-obs'], float):
                    logging.warn("Non-standard date specified in FITS file!")
                    frac, year = numpy.modf(hdulist[0].header['date-obs'])
                    timestamp = datetime.datetime(int(year), 1, 1)
                    delta = datetime.timedelta(365.242199 * frac)
                    timestamp += delta
                else:
                    raise KeyError("Timestamp in fits file unreadable")
            try:
                timezone = pytz.timezone(hdulist[0].header['timesys'])
            except (pytz.UnknownTimeZoneError, KeyError):
                logging.debug(
                    "Timezone not specified in FITS file: assuming UTC")
            timestamp = timestamp.replace(tzinfo=timezone)
            self.utc = pytz.utc.normalize(timestamp.astimezone(pytz.utc))
        except KeyError:
            logging.warn("Timestamp not specified in FITS file; using now")
            self.utc = datetime.datetime.now().replace(tzinfo=pytz.utc)
        try:
            endtime = dateutil.parser.parse(hdulist[0].header['end_utc'])
            endtime = endtime.replace(tzinfo=timezone)
            self.utc_end = pytz.utc.normalize(endtime.astimezone(pytz.utc))
            delta = self.utc_end - self.utc
            self.inttime = delta[0]*86400 + delta[1] + delta[2]/1e6
        except KeyError:
            logging.warn("End time not specified or unreadable")
            self.inttime = 0
        self.obstime = self.utc
        self.plane = plane
        hdulist.close()

    def _coordparse(self, hdulist):
        """Set some 'shortcut' variables for access to the coordinate
        parameters in the FITS file header.
        """
        # These are maintained for legacy reasons -- better to access by
        # header name through __getattr__?
        self.wcs = WCS()
        header = hdulist[0].header
        try:
            self.wcs.crval = header['crval1'], header['crval2']
            self.wcs.crpix = header['crpix1'], header['crpix2']
            self.wcs.cdelt = header['cdelt1'], header['cdelt2']
        except KeyError:
            logging.warn("Coordinate system not specified in FITS")
            raise
        try:
            self.wcs.ctype = header['ctype1'], header['ctype2']
        except KeyError:
            self.ws.ctype = 'unknown', 'unknown'
        try:
            self.wcs.crota = float(header['crota1']), float(header['crota2'])
        except KeyError:
            self.ws.crota = 0., 0.
        try:
            self.wcs.cunits = header['cunit1'], header['cunit2']
        except KeyError:
            self.wcs.cunits = 'unknown', 'unknown'

        self.wcs.wcsset()
        self.pix_to_position = self.wcs.p2s

    def _freqparse(self, hdulist):
        """
        Set some 'shortcut' variables for access to the frequency parameters
        in the FITS file header.

        @param hdulist: hdulist to parse
        @type hdulist: hdulist
        """
        # These are maintained for legacy reasons -- better to access by
        # header name through __getattr__?
        try:
            # Check for correct suffix, 3 was used as well
            #self.freqeff = hdulist[0].header['crval3']
            #self.freqbw = hdulist[0].header['cdelt3']
            self.freqeff = hdulist[0].header['crval4']
            self.freqbw = hdulist[0].header['cdelt4']
        except KeyError:
            logging.warn("Frequency not specified in FITS")
            raise

    def __getstate__(self):
        return {
            "filename": self.filename,
            "plane": self.plane,
            "obstime": self.obstime
            }

    def __setstate__(self, statedict):
        self.filename = statedict['filename']
        self.plane = statedict['plane']
        self.obstime = statedict['obstime']
        self.utc = self.obstime

        hdulist = pyfits.open(self.filename)
        self._coordparse(hdulist)
        self._beamsizeparse(hdulist)
        hdulist.close()

    def get_header(self):
        return pyfits.getheader(self.filename)

    @property
    def data(self):
        """
        Read and return data from our FITS file.

        NOTE: PyFITS reads the data into an array indexed as [y][x]. We
        take the transpose to make this more intuitively reasonable and
        consistent with (eg) ds9 display of the FitsFile. Transpose back
        before viewing the array with RO.DS9, saving to a FITS file,
        etc.
        """
        # pyfits returns data in arrays of numpy.float32; boost.python
        # chokes on them.
        data = numpy.float64(pyfits.getdata(self.filename).squeeze())
        if not isinstance(self.plane, bool):
            data = data[self.plane].squeeze()
        if len(data.shape) != 2:
            # This basically takes Stokes I if we have an image cube instead
            # of an image.
            # self.data=self.data[0,:,:]
            # If you make some assumptions about the data format, that may
            # be true, but...
            raise IndexError("Data has wrong shape")
        data = data.transpose()
        return data

    def _beamsizeparse(self, hdulist):
        """Read and return the beam properties bmaj, bmin and bpa values from
        the fits header

        Only Miriad and AIPS cleaned images can be handled by this method.
        If no (key) values can be read we use the WENSS values.
        """

        hdulist = pyfits.open(self.filename)
        header = hdulist[0].header
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
        hdulist.close()
        super(FitsFile, self)._beamsizeparse(bmaj, bmin, bpa)

    def __getattr__(self, attrname):
        """
        Read FITS header for unknown attributes.

        If they're not found, throw an AttributeError.

        @type attrname: string
        """
        if hasattr(self, "filename"):
            hdr = pyfits.open(self.filename)[0].header
            if attrname in hdr:
                return hdr[attrname]
        raise AttributeError(attrname)

    def fitsfile(self):
        return self.filename


def dbimage_from_accessor(dataset, image):
    """Create an entry in the database images table from an image 'accessor'

    Args:

        - dataset (dataset.DataSet): DataSet for the image. Also
          provides the database connection.

        - image (DataAccessor): FITS/AIPS/HDF5 image available through
          an accessor

    Returns:

        (dataset.Image): a dataset.Image instance.
    """
    from ..database.dataset import Image
    
    data = {'tau_time': image.inttime,
            'freq_eff': image.freqeff,
            'freq_bw': image.freqbw,
            'taustart_ts': image.obstime.strftime("%Y-%m-%d-%H:%M:%S.%3f"),
            'url': image.filename,
            }
    image = Image(dataset, data=data)
    return image


def sourcefinder_image_from_accessor(image):
    """Create a source finder ImageData object from an image 'accessor'

    Args:

        - image (DataAccessor): FITS/AIPS/HDF5 image available through
          an accessor.

    Returns:

        (sourcefinder.ImageData): a source finder image.
    """

    from ..sourcefinder.image import ImageData
    
    image = ImageData(image.data, image.beam, image.wcs)
    return image
