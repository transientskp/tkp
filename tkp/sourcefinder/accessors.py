#
# LOFAR Transients Key Project
#
"""
Data accessors.

These can be used to populate ImageData objects based on some data source
(FITS file, array in memory... etc).
"""
# Python standard library
import datetime, logging
import dateutil.parser, pytz
# Other external libraries
import pyfits
import numpy

class DataAccessor(object):
    """
    Base class for accessors used with :class:`tkp_lib.image.ImageData`.

    Data accessors provide a uniform way for the ImageData class (ie, generic
    image representation) to access the various ways in which images may be
    stored (FITS files, arrays in memory, potentially HDF5, etc).
    """
    def _beamsizeparse(self, bmaj, bmin, bpa):
        """
        Needs beam parameters, no defaults.
        """

        self.semimaj = (bmaj / 2.) * (numpy.sqrt((numpy.sin(numpy.pi * bpa / 180.) ** 2) / (self.cdelt1 ** 2) \
                                          +(numpy.cos(numpy.pi * bpa / 180.) ** 2) / (self.cdelt2 ** 2)))
        self.semimin = (bmin / 2.) * (numpy.sqrt((numpy.cos(numpy.pi * bpa / 180.) ** 2) / (self.cdelt1 ** 2) \
                                          +(numpy.sin(numpy.pi * bpa / 180.) ** 2) / (self.cdelt2 ** 2)))
        self.theta = numpy.pi * bpa / 180


class DataArray(DataAccessor):
    """
    Potential source for :class:`tkp_lib.image.ImageData`, based on an
    in-memory array.
    """
    def __init__(self, data, centrera, centredec, centrerapix, centredecpix,
        raincr, decincr, ctype1, ctype2):
        self.data = data

        # And this, children, is why we should always call things by the same
        # names...
        self.centrera, self.centredec = centrera, centredec
        self.crval1, self.crval2 = centrera, centredec
        self.centrerapix, self.centredecpix = centrerapix, centredecpix
        self.crpix1, self.crpix2 = centrerapix, centredecpix
        self.raincr, self.decincr = raincr, decincr
        self.cdelt1, self.cdelt2 = raincr, decincr
        self.ctype1, self.ctype2 = ctype1, ctype2


class AIPSppImage(DataAccessor):
    """
    Use pyrap to pull image data out of an AIPS++ table.

    This assumes that all AIPS++ images are structured just like the example
    James Miller-Jones provided me with. This is probably not a good
    assumption...
    """
    def __init__(self, filename, plane=0,beam=False):
        self.filename = filename
        self.plane = plane
        self._coordparse()
        bmaj,bmin,bpa=beam
        self._beamsizeparse(bmaj, bmin, bpa)

    def _get_table(self):
        from pyrap.tables import table
        return table(self.filename, ack=False)

    def _coordparse(self):
        my_coordinates = self._get_table().getkeyword('coords')['direction0']
        self.crval1, self.crval2 = my_coordinates['crval']
        self.crpix1, self.crpix2 = my_coordinates['crpix']
        self.cdelt1, self.cdelt2 = my_coordinates['cdelt']
        if my_coordinates['projection'] == "SIN":
            if my_coordinates['axes'][0] == "Right Ascension":
                self.ctype1 = "RA---SIN"
            if my_coordinates['axes'][1] == "Declination":
                self.ctype2 = "DEC--SIN"

    @property
    def data(self):
        return self._get_table().getcellslice("map", 0,
            [0, self.plane,  0,  0],
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
    tuple: (bmaj,bmin,bpa).
    """
    def __init__(self, filename, plane=False,beam=False):
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
            bmaj,bmin,bpa=beam
            super(FitsFile, self)._beamsizeparse(bmaj, bmin, bpa)

        # Attempt to do something sane with timestamps.
        try:
            try:
                timestamp = dateutil.parser.parse(hdulist[0].header['date-obs'])
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
            except (pytz.UnknownTimeZoneError, KeyError), error:
                logging.debug("Timezone not specified in FITS file: assuming UTC")
                timezone = pytz.utc
            #print "timestamp:",timestamp
            timestamp = timestamp.replace(tzinfo=timezone)
            self.utc = pytz.utc.normalize(timestamp.astimezone(pytz.utc))
        except KeyError:
            logging.warn("Timestamp not specified in FITS file; using now")
            self.utc = datetime.datetime.now().replace(tzinfo=pytz.utc)
        self.obstime = self.utc

        self.plane = plane

        hdulist.close()

    def _coordparse(self, hdulist):
        """
        Set some 'shortcut' variables for access to the coordinate parameters
        in the FITS file header.

        @param hdulist: hdulist to parse
        @type hdulist: hdulist
        """
        # These are maintained for legacy reasons -- better to access by
        # header name through __getattr__?
        try:
            self.centrera = hdulist[0].header['crval1']
            self.centredec = hdulist[0].header['crval2']
            self.centrerapix = hdulist[0].header['crpix1']
            self.centredecpix = hdulist[0].header['crpix2']
            self.raincr = hdulist[0].header['cdelt1']
            self.decincr = hdulist[0].header['cdelt2']
        except KeyError, error:
            logging.warn("Coordinate system not specified in FITS")
            raise

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
        except KeyError, error:
            logging.warn("Frequency not specified in FITS")
            raise

    def __getstate__(self):
        return {"filename": self.filename, "plane": self.plane, "obstime": self.obstime}

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
            # This basically takes Stokes I if we have an image cube instead of an image.
            # self.data=self.data[0,:,:]
            # If you make some assumptions about the data format, that may
            # be true, but...
            raise IndexError("Data has wrong shape")
        data = data.transpose()
        return data

    def _beamsizeparse(self, hdulist):
        """
        Read and return the beam properties bmaj, bmin and bpa values from the fits header
        Only Miriad and AIPS cleaned images can be handled by this method.
        (As these values were previously hard-coded in settings.py,
        we now set them here when the header is read.)
        If no (key) values can be read we use the WENSS values.
        """

        hdulist = pyfits.open(self.filename)
        prthdr = hdulist[0].header

        xpix_deg = prthdr['CDELT1']
        ypix_deg = prthdr['CDELT2']

        try:
            # Here we check if the key params are in the header (Miriad)
            bmaj = prthdr['BMAJ']
            bmin = prthdr['BMIN']
            bpa = prthdr['BPA']
        except KeyError,error:
            # if not found we check whether they are in the HISTORY key (AIPS)
            found = False
            for i in range(len(prthdr.ascardlist().keys())):
                if (prthdr.ascardlist().keys()[i] == 'HISTORY'):
                    histline = prthdr[i]
                    if (histline.find('BMAJ') > -1):
                        found = True
                        idx_bmaj = histline.find('BMAJ')
                        idx_bmin = histline.find('BMIN')
                        idx_bpa = histline.find('BPA')
                        bmaj = float(histline[idx_bmaj+5:idx_bmin])
                        bmin = float(histline[idx_bmin+5:idx_bpa])
                        bpa = float(histline[idx_bpa+4:len(histline)])
            if found is False:
                # if not provided and not found we are lost and
                # have to bomb out.
                raise ValueError(
                    "Basic processing is impossible without "
                    "adequate information about the resolution element.")

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
            if hdr.has_key(attrname):
                return hdr[attrname]
        raise AttributeError(attrname)


    def fitsfile(self):
        return self.filename
