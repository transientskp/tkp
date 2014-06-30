"""
Mock data objects for use in testing.
"""
from tkp.accessors.dataaccessor import DataAccessor
from tkp.accessors.common import parse_pixelsize, degrees2pixels


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
    """
    Quick and dirty mocking of a data accessor for use in tests.
    """
    def __init__(self, keywords, wcs):
        """
        Args:
            kewords (dict): key-value metadata pairs. Should reflect the
                DataAccessor properties, but we don't enforce this.
            wcs (tkp.utility.coordinates.WCS): WCS for the image.
        """
        self.keywords = keywords
        self._wcs = wcs

    @property
    def wcs(self):
        return self._wcs

    @property
    def data(self):
        return numpy.array([[[[0]]]])

    @property
    def url(self):
        return self.keywords["url"]

    @property
    def pixelsize(self):
        return parse_pixelsize(self.wcs)

    @property
    def tau_time(self):
        return self.keywords["tau_time"]

    @property
    def taustart_ts(self):
        return self.keywords["taustart_ts"]

    def get_centre_ra(self):
        return self.keywords["centre_ra"]
    def set_centre_ra(self, x):
        self.keywords["centre_ra"] = x
    centre_ra = property(get_centre_ra, set_centre_ra)

    def get_centre_decl(self):
        return self.keywords["centre_decl"]
    def set_centre_decl(self, x):
        self.keywords["centre_decl"] = x
    centre_decl = property(get_centre_decl, set_centre_decl)

    @property
    def freq_eff(self):
        return self.keywords["freq_eff"]

    @property
    def freq_bw(self):
        return self.keywords["freq_bw"]

    @property
    def beam(self):
        return self.keywords["beam"]
