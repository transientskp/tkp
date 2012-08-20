
from tkp.utility.coordinates import WCS
from tkp.utility.accessors.dataaccessor import DataAccessor
import numpy
import re

class LofarImage(DataAccessor):
    def __init__(self, source, plane=False, beam=False):
        super(LofarImage, self).__init__()  # Set defaults

        self.plane = plane

        self._read_data(source)
        self._coordparse(source)

        if not beam:
            self._beamsizeparse(source)
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
                    logging.warn("Non-standard date specified in FITS file!")
                    frac, year = numpy.modf(hdu.header['date-obs'])
                    timestamp = datetime.datetime(int(year), 1, 1)
                    delta = datetime.timedelta(365.242199 * frac)
                    timestamp += delta
                else:
                    raise KeyError("Timestamp in fits file unreadable")
            try:
                timezone = pytz.timezone(hdu.header['timesys'])
            except (pytz.UnknownTimeZoneError, KeyError):
                logging.debug(
                    "Timezone not specified in FITS file: assuming UTC")
            timestamp = timestamp.replace(tzinfo=timezone)
            self.utc = pytz.utc.normalize(timestamp.astimezone(pytz.utc))
        except KeyError:
            logging.warn("Timestamp not specified in FITS file; using now")
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
            logging.warn("End time not specified or unreadable")
            self.inttime = 0.

        if isinstance(source, basestring):
            # If we opened the FITS file ourselves, we'd better ensure it's
            # closed
            hdulist.close()

    def _coordparse(self, source):
        """Set some 'shortcut' variables for access to the coordinate
        parameters in the FITS file header.
        """
        # These are maintained for legacy reasons -- better to access by
        # header name through __getattr__?
        self.wcs = WCS()
        try:
            self.wcs.crval = source["coordinfo"]["coords"]["direction0"].attrs["crval"]
            self.wcs.crpix = source["coordinfo"]["coords"]["direction0"].attrs["crpix"]
            self.wcs.cdelt = source["coordinfo"]["coords"]["direction0"].attrs["cdelt"]
        except KeyError:
            logging.warn("Coordinate system not specified in FITS")
            raise
        try:
            self.wcs.ctype = source['ctype1'], source['ctype2']
        except KeyError:
            self.wcs.ctype = 'unknown', 'unknown'
        try:
            self.wcs.crota = float(source['crota1']), float(source['crota2'])
        except KeyError:
            self.wcs.crota = 0., 0.
        try:
            self.wcs.cunits = source['cunit1'], source['cunit2']
        except KeyError:
            self.wcs.cunits = 'unknown', 'unknown'

        self.wcs.wcsset()
        self.pix_to_position = self.wcs.p2s


    def get_header(self):
        # Preserved for API compatibility.
        return self.header

    def _read_data(self, source):
        """
        Read and store data from our FITS file.
        """
        self.data = numpy.squeeze(source["map"])

        if len(self.data.shape) != 2:
            raise IndexError("Data has wrong shape")

        # TODO: do we need to transpose?
        #self.data = data.transpose()

        coordinfo = source["/coordinfo"]
        attrgroups = source["/ATTRGROUPS"]

        lofar_antenna = attrgroups["LOFAR_ANTENNA"]
        lofar_field = attrgroups['LOFAR_FIELD']
        lofar_history = attrgroups['LOFAR_HISTORY']
        lofar_observation = attrgroups['LOFAR_OBSERVATION']
        lofar_origin = attrgroups['LOFAR_ORIGIN']
        lofar_source = attrgroups['LOFAR_SOURCE']
        lofar_station = attrgroups['LOFAR_STATION']

        self.filename = source.attrs['FILENAME']
        filedate = source.attrs['FILEDATE']
        filetype = source.attrs['FILETYPE']
        self.telescope = source.attrs['TELESCOPE']
        observer = source.attrs['OBSERVER']
        project_id = source.attrs['PROJECT_ID']
        project_title = source.attrs['PROJECT_TITLE'],
        project_pi = source.attrs['PROJECT_PI']
        project_co_i = source.attrs['PROJECT_CO_I']
        project_contact = source.attrs['PROJECT_CONTACT']
        observation_id = source.attrs['OBSERVATION_ID']
        observation_start_mjd = source.attrs['OBSERVATION_START_MJD']
        observation_start_utc = source.attrs['OBSERVATION_START_UTC']
        observation_end_mjd = source.attrs['OBSERVATION_END_MJD']
        observation_end_utc = source.attrs['OBSERVATION_END_UTC']
        observation_nof_station = source.attrs['OBSERVATION_NOF_STATIONS']
        observation_stations_list = source.attrs['OBSERVATION_STATIONS_LIST']
        observation_frequency_max = source.attrs['OBSERVATION_FREQUENCY_MAX']
        observation_frequency_min = source.attrs['OBSERVATION_FREQUENCY_MIN']
        self.freqeff = source.attrs['OBSERVATION_FREQUENCY_CENTER']
        observation_frequency_unit = source.attrs['OBSERVATION_FREQUENCY_UNIT']
        observation_nof_bits_per_sample = source.attrs['OBSERVATION_NOF_BITS_PER_SAMPLE']
        clock_frequency = source.attrs['CLOCK_FREQUENCY']
        clock_frequency_unit = source.attrs['CLOCK_FREQUENCY_UNIT']
        antenna_set = source.attrs['ANTENNA_SET']
        filter_selection = source.attrs['FILTER_SELECTION']
        target = source.attrs['TARGET']
        system_version = source.attrs['SYSTEM_VERSION']
        pipeline_name = source.attrs['PIPELINE_NAME']
        pipeline_version = source.attrs['PIPELINE_VERSION']
        notes = source.attrs['NOTES']




    def _beamsizeparse(self, source):
        """Read and return the beam properties bmaj, bmin and bpa values from
        the fits header

        Only Miriad and AIPS cleaned images can be handled by this method.
        If no (key) values can be read we use the WENSS values.
        """

        bmaj, bmin, bpa = None, None, None
        try:
            # MIRIAD FITS file
            bmaj = source['BMAJ']
            bmin = source['BMIN']
            bpa = source['BPA']
        except KeyError:
            pass
        if bmaj is None:
            # if not provided and not found we are lost and
            # have to bomb out.
            raise ValueError("Basic processing is impossible without adequate information about the resolution element")
        super(FITSImage, self)._beamsizeparse(bmaj, bmin, bpa)

    def __getattr__(self, attrname):
        """
        Read FITS source for unknown attributes.

        If they're not found, throw an AttributeError.

        @type attrname: string
        """
        if attrname in self.source:
            return self.source[attrname]
        raise AttributeError(attrname)