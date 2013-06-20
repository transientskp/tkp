from tkp.utility.accessors import FitsImage

def parse_additional_lofar_metadata(header):
    """Parse missing stuff from headers that should be injected by trap-inject"""
    metadata = {
        'antenna_set': header['ANTENNA'],
        'channels': header['CHANNELS'],
        'ncore': header['NCORE'],
        'nintl': header['NINTL'],
        'nremote': header['NREMOTE'],
        'position': header['POSITION'],
        'subbands': header['SUBBANDS'],
        'subbandwidth': header['SUBBANDW'],
        }
    return metadata


class LofarFitsImage(FitsImage):
    def __init__(self, url, plane=False, beam=False, hdu=0):
        super(LofarFitsImage, self).__init__(url, plane, beam, hdu)
        self._override_tau_time()
        try:
            self.extra_metadata = parse_additional_lofar_metadata(self.header)
        except KeyError as e:
            raise IOError("Problem loading additional metadata from "
                          "LofarFitsImage at %s, error reads: %s" %
                          (self.url, e))

    def extract_metadata(self):
        """Add additional lofar metadata to returned dict."""
        md = super(LofarFitsImage, self).extract_metadata()
        md.update(self.extra_metadata)
        return md


    def _override_tau_time(self):
        """This may have been set already by _timeparse, but if defined here
         it is set by our inject script and should be used"""
        if 'TAU_TIME' in self.header:
            self.tau_time = self.header['TAU_TIME']

