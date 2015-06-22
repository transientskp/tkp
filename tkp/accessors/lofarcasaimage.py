"""
This module implements the CASA LOFAR data container format, described in this
document:

http://www.lofar.org/operations/lib/exe/fetch.php?media=:public:documents:casa_image_for_lofar_0.03.00.pdf
"""
import logging
import warnings
import numpy
import datetime
from casacore.tables import table as casacore_table
from tkp.accessors.casaimage import CasaImage
from tkp.accessors.lofaraccessor import LofarAccessor
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

class LofarCasaImage(CasaImage, LofarAccessor):
    """
    Use casacore to pull image data out of an Casa table.

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

        self.subtables = self.open_subtables()
        self.taustart_ts = self.parse_taustartts()
        self.tau_time = self.parse_tautime()

        # Additional, LOFAR-specific metadata
        self.antenna_set = self.parse_antennaset()
        self.ncore, self.nremote, self.nintl =  self.parse_stations()
        self.subbandwidth = self.parse_subbandwidth()
        self.subbands = self.parse_subbands()


    def open_subtables(self):
        """open all subtables defined in the LOFAR format
        args:
            table: a casacore table handler to a LOFAR CASA table
        returns:
            a dict containing all LOFAR CASA subtables
        """
        subtables = {}
        for subtable in subtable_names:
            subtable_location = self.table.getkeyword("ATTRGROUPS")[subtable]
            subtables[subtable] = casacore_table(subtable_location, ack=False)
        return subtables


    def parse_taustartts(self):
        """ extract image start time from CASA table header
        """
        # Note that we sort the table in order of ascending start time then choose
        # the first value to ensure we get the earliest possible starting time.
        observation_table = self.subtables['LOFAR_OBSERVATION']
        julianstart = observation_table.query(
            sortlist="OBSERVATION_START", limit=1).getcell(
            "OBSERVATION_START", 0
        )
        unixstart = julian2unix(julianstart)
        taustart_ts = datetime.datetime.fromtimestamp(unixstart)
        return taustart_ts


    @staticmethod
    def non_overlapping_time(series):
        """
        Returns the sum of total ranges without overlap.

        series: a list of 2 item tuples representing ranges.
        """
        series.sort()
        overlap = total = 0
        for n, (start, end) in enumerate(series):
            total += end - start
            for (nextstart, nextend) in series[n+1:]:
                if nextstart >= end:
                    break
                overlapstart = max(nextstart, start)
                overlapend = min(nextend, end)
                overlap += overlapend - overlapstart
                start = overlapend
        return total - overlap


    def parse_tautime(self):
        """
        Returns the total on-sky time for this image.
        """
        origin_table = self.subtables['LOFAR_ORIGIN']
        startcol = origin_table.col('START')
        endcol = origin_table.col('END')
        series = [(int(start), int(end)) for start, end in zip(startcol, endcol)]
        tau_time = LofarCasaImage.non_overlapping_time(series)
        return tau_time



    def parse_antennaset(self):
        observation_table = self.subtables['LOFAR_OBSERVATION']
        antennasets = CasaImage.unique_column_values(observation_table, "ANTENNA_SET")
        if len(antennasets) == 1:
            return antennasets[0]
        else:
            raise Exception("Cannot handle multiple antenna sets in image")



    def parse_subbands(self):
        origin_table = self.subtables['LOFAR_ORIGIN']
        num_chans = CasaImage.unique_column_values(origin_table, "NUM_CHAN")
        if len(num_chans) == 1:
            return num_chans[0]
        else:
            raise Exception("Cannot handle varying numbers of channels in image")


    def parse_subbandwidth(self):
        # subband
        # see http://www.lofar.org/operations/doku.php?id=operator:background_to_observations&s[]=subband&s[]=width&s[]=clock&s[]=frequency
        freq_units = {
            'Hz': 1,
            'kHz': 10 ** 3,
            'MHz': 10 ** 6,
            'GHz': 10 ** 9,
        }
        observation_table = self.subtables['LOFAR_OBSERVATION']
        clockcol = observation_table.col('CLOCK_FREQUENCY')
        clock_values = CasaImage.unique_column_values(observation_table, "CLOCK_FREQUENCY")
        if len(clock_values) == 1:
            clock = clock_values[0]
            unit = clockcol.getkeyword('QuantumUnits')[0]
            trueclock = freq_units[unit] * clock
            subbandwidth = trueclock / 1024
            return subbandwidth
        else:
            raise Exception("Cannot handle varying clocks in image")



    def parse_stations(self):
        """Extract number of specific LOFAR stations used
        returns:
            (number of core stations, remote stations, international stations)
        """

        observation_table = self.subtables['LOFAR_OBSERVATION']
        antenna_table = self.subtables['LOFAR_ANTENNA']
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
