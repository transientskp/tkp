import logging
import warnings
from pyrap.tables import table as pyrap_table
from math import degrees
from tkp.accessors.dataaccessor import DataAccessor
from tkp.utility.coordinates import WCS
from tkp.accessors.common import parse_pixelsize, degrees2pixels

logger = logging.getLogger(__name__)

class CasaImage(DataAccessor):
    # NB CasaImage does not provide tau_time or taustart_ts, so cannot be
    # instantiated.
    def __init__(self, url, plane=0, beam=None):
        super(CasaImage, self).__init__()
        self._url = url
        table = pyrap_table(self.url.encode(), ack=False)
        self._data = parse_data(table, plane)
        self._wcs = parse_coordinates(table)
        self._centre_ra, self._centre_decl = parse_phase_centre(table)
        self._freq_eff, self._freq_bw = parse_frequency(table)

        if beam:
            (bmaj, bmin, bpa) = beam
            self._beam = degrees2pixels(
                bmaj, bmin, bpa, self.pixelsize[0], self.pixelsize[1]
            )
        else:
            self._beam = parse_beam(table, self.pixelsize)

    @property
    def wcs(self):
        return self._wcs

    @property
    def data(self):
        return self._data

    @property
    def url(self):
        return self._url

    @property
    def pixelsize(self):
        return parse_pixelsize(self.wcs)

    @property
    def centre_ra(self):
        return self._centre_ra

    @property
    def centre_decl(self):
        return self._centre_decl

    @property
    def freq_eff(self):
        return self._freq_eff

    @property
    def freq_bw(self):
        return self._freq_bw

    @property
    def beam(self):
        return self._beam


def parse_data(table, plane=0):
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

def parse_coordinates(table):
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
    # Update WCS
    wcs.wcsset()
    return wcs

def parse_frequency(table):
    """extract frequency related information from headers"""
    freq_eff = table.getkeywords()['coords']['spectral2']['restfreq']
    freq_bw = table.getkeywords()['coords']['spectral2']['wcs']['cdelt']
    return freq_eff, freq_bw


def parse_beam(table, pixelsize):
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
    beam_pixels = degrees2pixels(bmaj, bmin, bpa, pixelsize[0], pixelsize[1])
    return beam_pixels

def parse_phase_centre(table):
    # The units for the pointing centre are not given in either the image cube
    # itself or in the ICD. Assume radians.
    # Note that we'll return the RA modulo 360 so it's always 0 <= RA < 360
    centre_ra, centre_decl = table.getkeyword('coords')['pointingcenter']['value']
    return degrees(centre_ra) % 360, degrees(centre_decl)
