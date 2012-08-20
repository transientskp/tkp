
from tkp.utility.coordinates import WCS
from tkp.utility.accessors.dataaccessor import DataAccessor

class CASAImage(DataAccessor):
    """
    Use pyrap to pull image data out of an AIPS++ table.

    This assumes that all AIPS++ images are structured just like the example
    James Miller-Jones provided me with. This is probably not a good
    assumption...
    """
    def __init__(self, filename, plane=0, beam=None):
        super(CASAImage, self).__init__()  # Set defaults
        self.filename = filename
        self.plane = plane
        self._coordparse()
        self._freqparse()
        if beam:
            bmaj, bmin, bpa = beam
            super(CASAImage, self)._beamsizeparse(bmaj, bmin, bpa)
        else:
            self._beamsizeparse()

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

    def _freqparse(self):
        # This is what one gets from the C-imager
        try:
            spectral_info = self._get_table().getkeyword('coords')['spectral2']
            self.freqeff = spectral_info['wcs']['crval']
            self.freqbw = spectral_info['wcs']['cdelt']
        except KeyError:
            pass

    def _beamsizeparse(self):
        try:
            beam_info = self._get_table().getkeyword(
                'imageinfo')['restoringbeam']
            bmaj = beam_info['major']['value']
            bmin = beam_info['minor']['value']
            bpa = beam_info['positionangle']['value']
            super(CASAImage, self)._beamsizeparse(bmaj, bmin, bpa)
        except KeyError:
            raise ValueError("beam size information not available")

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


class AIPSppImage(CASAImage):
    pass