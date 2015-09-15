import logging
from tkp.accessors import CasaImage

logger = logging.getLogger(__name__)


class AartfaacCasaImage(CasaImage):

    def __init__(self, url, plane=0, beam=None):
        super(AartfaacCasaImage, self).__init__(url, plane=0, beam=None)

        self.taustart_ts = self.parse_taustartts()
        self.telescope = self.table.getkeyword('coords')['telescope']

        # TODO: header does't contain integration time
        # aartfaac imaginig pipeline issue #25
        self.tau_time = 1

    def parse_frequency(self):
        """
        Extract frequency related information from headers

        (Overrides the implementation in CasaImage, which pulls the entries
        from the 'spectral2' sub-table.)

        """
        keywords = self.table.getkeywords()

        # due to some undocumented casacore feature, the 'spectral' keyword
        # changes from spectral1 to spectral2 when AARTFAAC imaging developers
        # changed some of the header information. For now we will try both
        # locations.
        if 'spectral1' in keywords['coords']:
            keyword = 'spectral1'

        if 'spectral2' in keywords['coords']:
            keyword = 'spectral2'

        freq_eff = keywords['coords'][keyword]['restfreq']
        freq_bw = keywords['coords'][keyword]['wcs']['cdelt']
        return freq_eff, freq_bw
