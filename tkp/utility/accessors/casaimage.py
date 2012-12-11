from pyrap.tables import table as pyrap_table
from tkp.utility.accessors.beam import degrees2pixels
from tkp.utility.accessors.dataaccessor import DataAccessor
import logging

logger = logging.getLogger(__name__)

class CasaImage(DataAccessor):
    """
    Use pyrap to pull image data out of an Casa table.

    """
    def __init__(self, filename, plane=0, beam=None):
        super(CasaImage, self).__init__()  # Set defaults
        self.filename = filename
        #pyrap can't handle unicode
        self.table = pyrap_table(self.filename.encode(), ack=False)
        self.beam = beam
        self.subtables = {}
        self.plane = plane
        self.data = self.table[0]['map']

        self._coordparse()
        self._freqparse()
        self._beamsizeparse()


    def _coordparse(self):
        my_coordinates = self.table.getkeyword('coords')['direction0']
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

    def _freqparse(self):
        # This is what one gets from the C-imager
        try:
            spectral_info = self.table.getkeyword('coords')['spectral2']
            self.freqeff = spectral_info['wcs']['crval']
            self.freqbw = spectral_info['wcs']['cdelt']
        except KeyError:
            pass

    def _beamsizeparse(self):
        if self.beam:
            bmaj, bmin, bpa = self.beam
        else:
            restoringbeam = self.table.getkeyword('imageinfo')['restoringbeam']
            bmaj = restoringbeam['major']['value']
            bmin = restoringbeam['minor']['value']
            bpa = restoringbeam['positionangle']['value']

        deltax = self.wcs.cdelt[0]
        deltay = self.wcs.cdelt[1]
        self.beam = degrees2pixels(bmaj, bmin, bpa, deltax, deltay)

