"""
This module implements the CASA kat7 data container format.
"""
import logging
from tkp.accessors.dataaccessor import BasicAccessorProperties
from tkp.accessors.casaimage import CasaImage
from tkp.utility.coordinates import mjd2datetime

logger = logging.getLogger(__name__)


class Kat7CasaImage(CasaImage, BasicAccessorProperties):
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

        self._taustart_ts = parse_taustartts(self.table)
        self._tau_time = parse_tautime(self.table)


def parse_taustartts(table):
    """ extract observation time from CASA table header
    """
    obsdate = table.getkeyword('coords')['obsdate']['m0']['value']
    return mjd2datetime(obsdate)


def parse_tautime(table):
    # TODO: this information is not yet included in the kat-7 casa headers
    return 1
