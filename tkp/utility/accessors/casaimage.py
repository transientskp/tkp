import logging
import warnings
from pyrap.tables import table as pyrap_table
from math import degrees
from tkp.utility.accessors.dataaccessor import DataAccessor
from tkp.utility.coordinates import WCS
from tkp.utility.accessors.beam import degrees2pixels
from tkp.utility.accessors.common import parse_pixelsize

logger = logging.getLogger(__name__)

class CasaImage(DataAccessor):
    def __init__(self, url, plane=0, beam=None):
        super(CasaImage, self).__init__()  # Set defaults
        self.url = url

        self.table = pyrap_table(self.url.encode(), ack=False)
        self.telescope = self.table.getkeyword('coords')['telescope']
        self.data = parse_data(self.table, plane)
        self.wcs = parse_coordinates(self.table)
        self.pixelsize = parse_pixelsize(self.wcs)
        self.centre_ra, self.centre_decl = parse_phase_centre(self.table)
        self.freq_eff, self.freq_bw = parse_frequency(self.table)

        if beam:
            (bmaj, bmin, bpa) = beam
            self.beam = degrees2pixels(bmaj, bmin, bpa,
                                       self.pixelsize[0], self.pixelsize[1])
        else:
            self.beam = parse_beam(self.table, self.pixelsize)

#------------------------------------------------------------------------------
# The following functions are all fairly class-specific in practice, 
# but can be defined simply, without state, so we might as well:
# It's slightly easier to test this way, we might end up re-using them,
# and it makes explicit that they are not overridden by some child class.
# It's also, arguably, easier to follow.
#------------------------------------------------------------------------------  
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
