import logging
from tkp.accessors import CasaImage
from casacore.tables import table as casacore_table

logger = logging.getLogger(__name__)


class AartfaacCasaImage(CasaImage):

    def __init__(self, url, plane=0, beam=None):
        super(AartfaacCasaImage, self).__init__(url, plane=0, beam=None)
        table = casacore_table(self.url.encode(), ack=False)
        self.taustart_ts = self.parse_taustartts(table)
        self.telescope = table.getkeyword('coords')['telescope']

        # TODO: header does't contain integration time
        # aartfaac imaginig pipeline issue #25
        self.tau_time = 1

    def parse_frequency(self, table):
        """
        Extract frequency related information from headers

        (Overrides the implementation in CasaImage, which pulls the entries
        from the 'spectral2' sub-table.)

        """
        keywords = table.getkeywords()

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
