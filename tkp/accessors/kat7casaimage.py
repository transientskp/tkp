"""
This module implements the CASA kat7 data container format.
"""
import logging
import warnings
import numpy
import datetime
from pyrap.tables import table as pyrap_table
from tkp.accessors.dataaccessor import DataAccessor
from tkp.accessors.casaimage import CasaImage
from tkp.utility.coordinates import julian2unix

logger = logging.getLogger(__name__)


class Kat7CasaImage(CasaImage):
    """
    Use pyrap to pull image data out of an Casa table.


    Args:
      - url: location of CASA table
      - plane: if datacube, what plane to use
      - beam: (optional) beam parameters in degrees, in the form 
        (bmaj, bmin, bpa). Will attempt to read from header if
        not supplied.
    """
    def __init__(self, url, plane=0, beam=None):
        super(Kat7CasaImage, self).__init__(url, plane, beam)

        self.taustart_ts = parse_taustartts(self.table)
        self.tau_time = parse_tautime(self.table)


def parse_taustartts(table):
    """ extract observation time from CASA table header
    """
    julianstart = table.getkeyword('coords')['obsdate']['m0']['value']
    unixstart = julian2unix(julianstart)
    taustart_ts = datetime.datetime.fromtimestamp(unixstart)
    return taustart_ts


def parse_tautime(table):
    # TODO: this information is not yet included in the kat-7 casa headers
    return 1
