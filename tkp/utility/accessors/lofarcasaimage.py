"""
This module implements the CASA LOFAR data container format, described in this
document:

http://www.lofar.org/operations/lib/exe/fetch.php?media=:public:documents:casa_image_for_lofar_0.03.00.pdf
"""
import logging
import warnings
import datetime
import numpy
from math import degrees

from pyrap.tables import table as pyrap_table

from tkp.utility.accessors.beam import degrees2pixels
from tkp.utility.accessors.dataaccessor import DataAccessor, parse_pixel_scale
from tkp.utility.coordinates import julian2unix


logger = logging.getLogger(__name__)

subtable_names = [
    'LOFAR_FIELD',
    'LOFAR_ANTENNA',
    'LOFAR_HISTORY',
    'LOFAR_ORIGIN',
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


def open_subtables(table):
    """open all subtables defined in the LOFAR format
    args:
        table: a pyrap table handler to a LOFAR CASA table
    returns:
        a dict containing all LOFAR CASA subtables
    """
    subtables = {}
    for subtable in subtable_names:
        subtable_location = table.getkeyword("ATTRGROUPS")[subtable]
        subtables[subtable] = pyrap_table(subtable_location, ack=False)
    return subtables


def parse_coordinates(table, wcs):
    """extract coordination properties from headers
    TODO: it would be better if this returns a new WCS object and not to modify
          the wcs argument
    """
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


def parse_frequency(table, observation_table):
    """extract frequency related information from headers"""
    freq_eff = table.getkeywords()['coords']['spectral2']['restfreq']
    freq_bw = table.getkeywords()['coords']['spectral2']['wcs']['cdelt']
    # subband
    # see http://www.lofar.org/operations/doku.php?id=operator:background_to_observations&s[]=subband&s[]=width&s[]=clock&s[]=frequency
    clockcol = observation_table.col('CLOCK_FREQUENCY')
    clock = clockcol.getcol()[0]
    unit = clockcol.getkeyword('QuantumUnits')[0]
    trueclock = freq_units[unit] * clock
    subbandwidth = trueclock / 1024
    return (freq_eff, freq_bw, subbandwidth)


def parse_data(table, plane=0):
    """extract and massage data from CASA table"""
    data = table[0]['map'].squeeze()
    planes = len(data.shape)
    if planes != 2:
        msg = "received datacube with %s planes, assuming Stokes I and taking plane 0" % planes
        logger.warn(msg)
        warnings.warn(msg)
        data = data[plane,:,:]
    data = data.transpose()
    return data


def parse_beam(table, wcs):
    """
    Return 2 tuples:
    - the beam parameters in degrees (major/minor/pa)
    - pixel size in degrees per pixel (xscale, yscale)
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

    if wcs.cunit[0] == "deg":
        deltax = wcs.cdelt[0]
    elif wcs.cunit[0] == "rad":
        deltax = degrees(wcs.cdelt[0])

    if wcs.cunit[1] == "deg":
        deltay = wcs.cdelt[1]
    elif wcs.cunit[1] == "rad":
        deltay = degrees(wcs.cdelt[1])

    beam_pixels = degrees2pixels(bmaj, bmin, bpa, deltax, deltay)
    return beam_pixels, (deltax, deltay)


def parse_tautime(origin_table):
    startcol = origin_table.col('START')
    endcol = origin_table.col('END')
    tau_time = endcol[0] - startcol[0]
    return tau_time


def parse_antennaset(observation_table):
    return observation_table.getcol('ANTENNA_SET')[0]


def parse_subbands(origin_table):
   return origin_table.getcol('NUM_CHAN')[0]


def parse_channels(origin_table):
    return origin_table.getcol('NCHAN_AVG')[0]


def parse_stations(observation_table, antenna_table):
    """Extract number of specific LOFAR stations used
    returns:
        (number of core stations, remote stations, international stations)
    """
    nvis_used = observation_table.getcol('NVIS_USED')
    names = numpy.array(antenna_table.getcol('NAME'))
    mask = numpy.sum(nvis_used, axis=2) > 0
    used = names[mask[0]]
    ncore = nremote = nintl = 0
    for station in used:
        if station.startswith('CS'):
            ncore += 1
        elif station.startswith('RS'):
            nremote += 1
        else:
            nintl += 1
    return ncore, nremote, nintl


def parse_phasecentre(table):
    # The units for the pointing centre are not given in either the image cube
    # itself or in the ICD. Assume radians.
    # Note that we'll return the RA modulo 360 so it's always 0 <= RA < 360
    phasecentre = table.getkeyword('coords')['pointingcenter']['value']
    centre_ra, centre_decl = phasecentre
    return degrees(centre_ra) % 360, degrees(centre_decl)


def parse_taustartts(observation_table):
    """ extract observation time from CASA table header
    """
    julianstart = observation_table.getcol('OBSERVATION_START')[0]
    unixstart = julian2unix(julianstart)
    taustart_ts = datetime.datetime.fromtimestamp(unixstart)
    return taustart_ts


def parse_position(antenna_table):
    """extract the position in ITRF (ie, Earth-centred Cartesian) coordinates.
    """
    position = antenna_table.getcol('POSITION')[0]
    return position


class LofarCasaImage(DataAccessor):
    """
    Use pyrap to pull image data out of an Casa table.

    This accessor assumes the casatable contains the values described in the
    CASA Image description for LOFAR. 0.03.00.

    args:
        url: location of CASA table
        plane: if datacube, what plane to use
        beam: beam parameters in pixels, in the form (bmaj, bmin, bpa)
    """
    def __init__(self, url, plane=0, beam=None):
        super(LofarCasaImage, self).__init__()  # Set defaults
        self.url = url
        self.table = pyrap_table(self.url.encode(), ack=False)
        self.data = parse_data(self.table, plane)

        self.beam = beam
        self.subtables = open_subtables(self.table)
        parse_coordinates(self.table, self.wcs)
        self.freq_eff, self.freq_bw, self.subbandwidth = parse_frequency(self.table,
                                        self.subtables['LOFAR_OBSERVATION'])
        self.pixel_scale = parse_pixel_scale(self.wcs)
        if not self.beam:
            self.beam, self.pixelsize = parse_beam(self.table, self.wcs)
        self.tau_time = parse_tautime(self.subtables['LOFAR_ORIGIN'])
        self.antenna_set = parse_antennaset(self.subtables['LOFAR_OBSERVATION'])
        self.subbands = parse_subbands(self.subtables['LOFAR_ORIGIN'])
        self.channels = parse_channels(self.subtables['LOFAR_ORIGIN'])
        self.ncore, self.nremote, self.nintl = parse_stations(self.subtables['LOFAR_OBSERVATION'],
                                            self.subtables['LOFAR_ANTENNA'])
        self.taustart_ts = parse_taustartts(self.subtables['LOFAR_OBSERVATION'])
        self.centre_ra, self.centre_decl = parse_phasecentre(self.table)
        self.position = parse_position(self.subtables['LOFAR_ANTENNA'])

        # check if everything is okay!
        self.ready()
