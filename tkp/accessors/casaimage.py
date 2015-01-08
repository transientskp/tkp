import logging
import warnings
from pyrap.tables import table as pyrap_table
from math import degrees
from tkp.accessors.dataaccessor import DataAccessor
from tkp.utility.coordinates import WCS
from tkp.accessors.common import parse_pixelsize, degrees2pixels

logger = logging.getLogger(__name__)


class CasaImage(DataAccessor):
    """
    Generic CASA table parser.

    CasaImage does not provide the required tau_time or taustart_ts, so you
    can't use this accessor directly with TRAP.
    """
    data = None
    wcs = None
    freq_eff = None
    freq_bw = None
    beam = None
    centre_ra = None
    centre_decl = None

    def __init__(self, url, plane=0, beam=None):
        super(CasaImage, self).__init__()
        self.url = url
        self.table = pyrap_table(self.url.encode(), ack=False)
        self.parse_data(plane)
        self.parse_coordinates()
        self.parse_phase_centre()
        self.parse_frequency()
        self.parse_beam(beam)

    @property
    def pixelsize(self):
        return parse_pixelsize(self.wcs)

    def parse_data(self, plane=0):
        """extract and massage data from CASA table"""
        data = self.table[0]['map'].squeeze()
        planes = len(data.shape)
        if planes != 2:
            msg = "received datacube with %s planes, assuming Stokes I and " \
                  "taking plane 0" % planes
            logger.warn(msg)
            warnings.warn(msg)
            data = data[plane, :, :]
        self.data = data.transpose()

    def parse_coordinates(self):
        """Returns a WCS object"""
        wcs = WCS()
        my_coordinates = self.table.getkeyword('coords')['direction0']
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
        wcs.cunit = self.table.getkeyword('coords')['direction0']['units']
        self.wcs = wcs

    def parse_frequency(self):
        """extract frequency related information from headers"""
        keywords = self.table.getkeywords()
        self.freq_eff = keywords['coords']['spectral2']['restfreq']
        self.freq_bw = keywords['coords']['spectral2']['wcs']['cdelt']

    def parse_beam(self, beam):
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

        if beam:
            (bmaj, bmin, bpa) = beam
            self.beam = degrees2pixels(bmaj, bmin, bpa, self.pixelsize[0],
                                       self.pixelsize[1])
        else:
            restoringbeam = self.table.getkeyword('imageinfo')['restoringbeam']
            bmaj = ensure_degrees(restoringbeam['major'])
            bmin = ensure_degrees(restoringbeam['minor'])
            bpa = ensure_degrees(restoringbeam['positionangle'])
            self.beam = degrees2pixels(bmaj, bmin, bpa, self.pixelsize[0],
                                       self.pixelsize[1])

    def parse_phase_centre(self):
        """
        The units for the pointing centre are not given in either the image cube
        itself or in the ICD. Assume radians.
        Note that we'll return the RA modulo 360 so it's always 0 <= RA < 360
        """
        pos = self.table.getkeyword('coords')['pointingcenter']['value']
        centre_ra, centre_decl = pos
        self.centre_ra = degrees(centre_ra) % 360
        self.centre_decl = degrees(centre_decl)
