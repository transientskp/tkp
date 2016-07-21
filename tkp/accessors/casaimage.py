import logging
import warnings
from casacore.tables import table as casacore_table
from math import degrees
from tkp.accessors.dataaccessor import DataAccessor
from tkp.utility.coordinates import WCS
from tkp.utility.coordinates import mjd2datetime

logger = logging.getLogger(__name__)


class CasaImage(DataAccessor):
    """
    Provides common functionality for pulling data from the CASA image format

    (Technically known as the 'MeasurementSet' format.)

    NB CasaImage does not provide tau_time or taustart_ts, as there was
    no clear standard for these metadata, so cannot be
    instantiated directly - subclass it and extract these attributes
    as appropriate to a given telescope.
    """
    def __init__(self, url, plane=0, beam=None):
        super(CasaImage, self).__init__()
        self.url = url

        # we don't want the table as a property since it makes the accessor
        # not serializable
        table = casacore_table(self.url.encode(), ack=False)
        self.data = self.parse_data(table, plane)
        self.wcs = self.parse_coordinates(table)
        self.centre_ra, self.centre_decl = self.parse_phase_centre(table)
        self.freq_eff, self.freq_bw = self.parse_frequency(table)
        self.pixelsize = self.parse_pixelsize()

        if beam:
            (bmaj, bmin, bpa) = beam
        else:
            bmaj, bmin, bpa = self.parse_beam(table)
        self.beam = self.degrees2pixels(
            bmaj, bmin, bpa, self.pixelsize[0], self.pixelsize[1])

    def parse_data(self, table, plane=0):
        """extract and massage data from CASA table"""
        data = table[0]['map'].squeeze()
        planes = len(data.shape)
        if planes != 2:
            msg = "received datacube with %s planes, assuming Stokes I and taking plane 0" % planes
            logger.warn(msg)
            warnings.warn(msg)
            data = data[plane, :, :]
        data = data.transpose()
        return data

    def parse_coordinates(self, table):
        """Returns a WCS object"""
        wcs = WCS()
        my_coordinates = table.getkeyword('coords')['direction0']
        wcs.crval = my_coordinates['crval']
        wcs.crpix = my_coordinates['crpix']
        wcs.cdelt = my_coordinates['cdelt']
        ctype = ['unknown', 'unknown']
        # What about other projections?!
        if my_coordinates['projection'] == "SIN":
            if my_coordinates['axes'][0] == "Right Ascension":
                ctype[0] = "RA---SIN"
            if my_coordinates['axes'][1] == "Declination":
                ctype[1] = "DEC--SIN"
        wcs.ctype = tuple(ctype)
        # Rotation, units? We better set a default
        wcs.crota = (0., 0.)
        wcs.cunit = table.getkeyword('coords')['direction0']['units']
        return wcs

    def parse_frequency(self, table):
        """extract frequency related information from headers"""
        freq_eff = table.getkeywords()['coords']['spectral2']['restfreq']
        freq_bw = table.getkeywords()['coords']['spectral2']['wcs']['cdelt']
        return freq_eff, freq_bw

    def parse_beam(self, table):
        """
        Returns:
          - Beam parameters, (semimajor, semiminor, parallactic angle) in
            (pixels,pixels, radians).
        """
        def ensure_degrees(quantity):
            if quantity['unit'] == 'deg':
                return quantity['value']
            elif quantity['unit'] == 'arcsec':
                return quantity['value'] / 3600
            elif quantity['unit'] == 'rad':
                return degrees(quantity['value'])
            else:
                raise Exception("Beam units (%s) unknown" % quantity['unit'])

        restoringbeam = table.getkeyword('imageinfo')['restoringbeam']
        bmaj = ensure_degrees(restoringbeam['major'])
        bmin = ensure_degrees(restoringbeam['minor'])
        bpa = ensure_degrees(restoringbeam['positionangle'])
        return bmaj, bmin, bpa

    def parse_phase_centre(self, table):
        # The units for the pointing centre are not given in either the image
        # cubeitself or in the ICD. Assume radians.
        # Note that we'll return the RA modulo 360 so it's always 0 <= RA < 360
        centre_ra, centre_decl = table.getkeyword('coords')['pointingcenter']['value']
        return degrees(centre_ra) % 360, degrees(centre_decl)

    def parse_taustartts(self, table):
        """
        Extract integration start-time from CASA table header.

        This applies to some CASA images (typically those created from uvFITS
        files) but not all, and so should be called for each sub-class.

        Arguments:
            table: MAIN table of CASA image.

        Returns:
            Time of image start as a instance of ``datetime.datetime``
        """
        obsdate = table.getkeyword('coords')['obsdate']['m0']['value']
        return mjd2datetime(obsdate)


    @staticmethod
    def unique_column_values(table, column_name):
        """
        Find all the unique values in a particular column of a CASA table.

        Arguments:
          - table:       ``casacore.tables.table``
          - column_name: ``str``

        Returns:
          - ``numpy.ndarray`` containing unique values in column.
        """
        return table.query(
            columns=column_name, sortlist="unique %s" % (column_name)
        ).getcol(column_name)
