from tkp.accessors import FitsImage
from tkp.accessors.lofaraccessor import LofarAccessor


class LofarFitsImage(FitsImage, LofarAccessor):
    def __init__(self, url, plane=False, beam=False, hdu=0):
        super(LofarFitsImage, self).__init__(url, plane, beam, hdu)
        header = self._get_header(hdu)
        self.antenna_set = header['ANTENNA']
        self.ncore = header['NCORE']
        self.nintl = header['NINTL']
        self.nremote = header['NREMOTE']
        self.subbands = header['SUBBANDS']
        self.subbandwidth = header['SUBBANDW']
        if 'TAU_TIME' in header:
            # This may have been set already by _timeparse, but if defined
            # here it is set by our inject script and should be used
            self.tau_time = header['TAU_TIME']

