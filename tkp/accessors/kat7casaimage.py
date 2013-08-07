"""
This module implements the CASA kat7 data container format.
"""
import logging
from pyrap.tables import table as pyrap_table
from tkp.accessors.casaimage import CasaImage
from tkp.utility.coordinates import mjd2datetime

logger = logging.getLogger(__name__)

class Kat7CasaImage(CasaImage):
    """
    Use pyrap to pull image data out of a CASA table as produced by KAT-7.

    Note that KAT-7 does not currently include image duration in its headers,
    so we use a placeholder value of 1.

    Note also that the start time is taken from the CASA coords record, and
    may not be valid if the image is composed of multiple observations.

    Args:
      - url: location of CASA table
      - plane: if datacube, what plane to use
      - beam: (optional) beam parameters in degrees, in the form
        (bmaj, bmin, bpa). Will attempt to read from header if
        not supplied.
    """
    def __init__(self, url, plane=0, beam=None):
        super(Kat7CasaImage, self).__init__(url, plane, beam)

        table = pyrap_table(self.url.encode(), ack=False)
        self._taustart_ts = parse_taustartts(table)

    @property
    def tau_time(self):
        # Placeholder value
        return 1

    @property
    def taustart_ts(self):
        return self._taustart_ts


def parse_taustartts(table):
    """ extract observation time from CASA table header
    """
    obsdate = table.getkeyword('coords')['obsdate']['m0']['value']
    return mjd2datetime(obsdate)
