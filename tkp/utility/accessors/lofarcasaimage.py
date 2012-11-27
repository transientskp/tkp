from pyrap.tables import table as pyrap_table
from tkp.utility.accessors.dataaccessor import DataAccessor
import tkp.utility.accessors
import logging
import warnings

logger = logging.getLogger(__name__)

subtable_names = [
    'LOFAR_FIELD',
    'LOFAR_ANTENNA',
    'LOFAR_HISTORY',
    'LOFAR_ORIGIN',
    'LOFAR_SOURCE',
    'LOFAR_QUALITY',
    'LOFAR_STATION',
    'LOFAR_POINTING',
    'LOFAR_OBSERVATION'
]

freq_units = {
    'Hz': 1,
    'kHz': 10**3,
    'MHz': 10**6,
    'GHz': 10**9,
}

class LofarCasaImage(DataAccessor):
    """
    Use pyrap to pull image data out of an Casa table.

    This accessor assumes the casatable contains the values described in the
    CASA Image description for LOFAR. 0.03.00
    """
    def __init__(self, filename, plane=0, beam=None):
        super(LofarCasaImage, self).__init__()  # Set defaults
        self.filename = filename
        self.table = pyrap_table(self.filename, ack=False)
        self.beam = beam
        self.subtables = {}
        self.plane = plane
        self.data = self.table[0]['map']

        self._subtableparse()
        self._coordparse()
        self._freqparse()
        self._beamsizeparse()

        # BUG3872 stuff below
        # freq
        self.frequency = self.table.getkeywords()['coords']['spectral2']['restfreq']

        # subband
        # see http://www.lofar.org/operations/doku.php?id=operator:background_to_observations&s[]=subband&s[]=width&s[]=clock&s[]=frequency
        clockcol = self.subtables['LOFAR_OBSERVATION'].col('CLOCK_FREQUENCY')
        clock = clockcol.getcol()[0]
        unit = clockcol.getkeyword('QuantumUnits')[0]
        trueclock = freq_units[unit] * clock
        self.subbandwidth = trueclock / 1024

        # integration time
        startcol = self.subtables['LOFAR_ORIGIN'].col('START')
        endcol = self.subtables['LOFAR_ORIGIN'].col('END')
        self.intgr_time = endcol[0] - startcol[0]

        # antenna configuration
        self.configuration = self.subtables['LOFAR_OBSERVATION'].getcol('ANTENNA_SET')[0]

        # number of subbands
        self.subbands = self.subtables['LOFAR_ORIGIN'].getcol('NUM_CHAN')[0]

        # number of channels
        self.channels = self.subtables['LOFAR_ORIGIN'].getcol('NCHAN_AVG')[0]

        # number of stations
        nvis_used = self.subtables['LOFAR_OBSERVATION'].getcol('NVIS_USED')
        station_ids = self.subtables['LOFAR_ANTENNA'].getcol('STATION_ID')
        names = self.subtables['LOFAR_ANTENNA'].getcol('NAME')


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
        self.beam = tkp.utility.accessors.beam2semibeam(bmaj, bmin, bpa, deltax, deltay)

    def _subtableparse(self):
        if not 'ATTRGROUPS' in self.table.getkeywords():
            msg = "LOFAR standard violation: ATTRGROUPS not defined in %s" % self.filename
            logger.warn(msg)
            warnings.warn(msg)
            return

        for subtable in subtable_names:
            subtable_location = self.table.getkeyword("ATTRGROUPS")[subtable]
            self.subtables[subtable] = pyrap_table(subtable_location)



