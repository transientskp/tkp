"""
Mock data objects for use in testing.
"""
from tkp.accessors.dataaccessor import DataAccessor
import numpy

class Mock(object):
    def __init__(self, returnvalue=None):
        self.callcount = 0
        self.callvalues = []
        self.returnvalue = returnvalue

    def __call__(self, *args, **kwargs):
        self.callcount += 1
        self.callvalues.append((args, kwargs))
        return self.returnvalue


class MockImage(DataAccessor):
    def __init__(self, keywords, wcs):
        """
        Quick and dirty mocking of a data accessor for use in tests.

        Args:
            kewords (dict): key-value metadata pairs. Should reflect the
                DataAccessor properties, but we don't enforce this.
            wcs (tkp.utility.coordinates.WCS): WCS for the image.
        """
        self.keywords = keywords
        self.wcs = wcs
        self.data = numpy.array([[[[0]]]])
        self.url = self.keywords["url"]
        self.pixelsize = self.parse_pixelsize()
        self.tau_time = self.keywords["tau_time"]
        self.taustart_ts = self.keywords["taustart_ts"]
        self.centre_ra = self.keywords["centre_ra"]
        self.centre_decl = self.keywords["centre_decl"]
        self.freq_eff = self.keywords["freq_eff"]
        self.freq_bw = self.keywords["freq_bw"]
        self.beam = self.keywords["beam"]
