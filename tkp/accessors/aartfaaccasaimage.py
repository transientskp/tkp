import logging
from tkp.accessors import CasaImage
from tkp.utility.coordinates import mjd2datetime

logger = logging.getLogger(__name__)


class AartfaacCasaImage(CasaImage):
    taustart_ts = None
    url = None
    tau_time = None
    telescope = None

    def __init__(self, url, plane=0, beam=None):
        super(AartfaacCasaImage, self).__init__(url, plane=0, beam=None)
        self.parse_taustartts()
        self.parse_tau_time()

        self.parse_telescope()

    def parse_frequency(self):
        """extract frequency related information from headers"""
        keywords = self.table.getkeywords()
        self.freq_eff = keywords['coords']['spectral1']['restfreq']
        self.freq_bw = keywords['coords']['spectral1']['wcs']['cdelt']

    def parse_taustartts(self):
        obsdate = self.table.getkeyword('coords')['obsdate']['m0']['value']
        self.taustart_ts = mjd2datetime(obsdate)

    def parse_tau_time(self):
        # TODO: AARTFAAC header doesn't contain this (yet)
        self.tau_time = 1

    def parse_telescope(self):
        self.telescope = self.table.getkeyword('coords')['telescope']