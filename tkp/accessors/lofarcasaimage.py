"""
This module implements the CASA LOFAR data container format, described in this
document:

http://www.lofar.org/operations/lib/exe/fetch.php?media=:public:documents:casa_image_for_lofar_0.03.00.pdf
"""
import logging
import warnings
import numpy
import datetime
from pyrap.tables import table as pyrap_table
from tkp.accessors.casaimage import CasaImage
from tkp.accessors.lofaraccessor import LofarAccessor
from tkp.accessors.lofaraccessor import LofarAccessorProperties

from tkp.utility.coordinates import julian2unix


logger = logging.getLogger(__name__)

subtable_names = (
    'LOFAR_FIELD',
    'LOFAR_ANTENNA',
    'LOFAR_HISTORY',
    'LOFAR_ORIGIN',
    'LOFAR_QUALITY',
    'LOFAR_STATION',
    'LOFAR_POINTING',
    'LOFAR_OBSERVATION'
)

class LofarCasaImage(CasaImage, LofarImage, LofarAccessorProperties):
    """
    Use pyrap to pull image data out of an Casa table.

    This accessor assumes the casatable contains the values described in the
    CASA Image description for LOFAR. 0.03.00.

    Args:
      - url: location of CASA table
      - plane: if datacube, what plane to use
      - beam: (optional) beam parameters in degrees, in the form
        (bmaj, bmin, bpa). Will attempt to read from header if
        not supplied.
    """
    def __init__(self, url, plane=0, beam=None):
        super(LofarCasaImage, self).__init__(url, plane, beam)

        subtables = open_subtables(self.table)
        self._taustart_ts = parse_taustartts(self.subtables)
        self._tau_time = parse_tautime(self.subtables)

        # Additional, LOFAR-specific metadata
        self._antenna_set = parse_antennaset(subtables),
        self._channels = parse_channels(subtables),
        self._ncore, self._nremote, self._nintl =  parse_stations(subtables)
        self._subbandwidth = parse_subbandwidth(subtables),
        self._subbands = parse_subbands(subtables)

        try:
            self.extra_metadata = parse_additional_lofar_metadata(subtables)
        except KeyError as e:
            raise IOError("Problem loading additional metadata from "
                          "LofarCasaImage at %s, error reads: %s" %
                          (self.url, e))


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


def parse_taustartts(subtables):
    """ extract observation time from CASA table header
    """
    observation_table = subtables['LOFAR_OBSERVATION']
    julianstart = observation_table.getcol('OBSERVATION_START')[0]
    unixstart = julian2unix(julianstart)
    taustart_ts = datetime.datetime.fromtimestamp(unixstart)
    return taustart_ts


def parse_tautime(subtables):
    origin_table = subtables['LOFAR_ORIGIN']
    startcol = origin_table.col('START')
    endcol = origin_table.col('END')
    tau_time = len(set.union(*[set(range(int(start), int(end)))
                               for start, end
                               in zip(startcol, endcol)]))
    return tau_time


def parse_antennaset(subtables):
    observation_table = subtables['LOFAR_OBSERVATION']
    return observation_table.getcol('ANTENNA_SET')[0]


def parse_subbands(subtables):
    origin_table = subtables['LOFAR_ORIGIN']
    return origin_table.getcol('NUM_CHAN')[0]


def parse_subbandwidth(subtables):
    # subband
    # see http://www.lofar.org/operations/doku.php?id=operator:background_to_observations&s[]=subband&s[]=width&s[]=clock&s[]=frequency
    freq_units = {
        'Hz': 1,
        'kHz': 10 ** 3,
        'MHz': 10 ** 6,
        'GHz': 10 ** 9,
    }
    observation_table = subtables['LOFAR_OBSERVATION']
    clockcol = observation_table.col('CLOCK_FREQUENCY')
    clock = clockcol.getcol()[0]
    unit = clockcol.getkeyword('QuantumUnits')[0]
    trueclock = freq_units[unit] * clock
    subbandwidth = trueclock / 1024
    return subbandwidth


def parse_channels(subtables):
    origin_table = subtables['LOFAR_ORIGIN']
    return origin_table.getcol('NCHAN_AVG')[0]


def parse_stations(subtables):
    """Extract number of specific LOFAR stations used
    returns:
        (number of core stations, remote stations, international stations)
    """
    observation_table = subtables['LOFAR_OBSERVATION']
    antenna_table = subtables['LOFAR_ANTENNA']
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
