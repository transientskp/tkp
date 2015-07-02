"""
This module implements the CASA kat7 data container format.
"""
import logging
from tkp.accessors.casaimage import CasaImage


logger = logging.getLogger(__name__)

class AmiCasaImage(CasaImage):
    """
    Use casacore to pull image data out of a CASA table as produced by AMI-LA.

    Note that AMI-LA does not currently include image duration in its headers,
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
        super(AmiCasaImage, self).__init__(url, plane, beam)
        self.taustart_ts = self.parse_taustartts()
        self.tau_time = 1  # Placeholder value until properly implemented
