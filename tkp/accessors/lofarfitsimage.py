from tkp.accessors import FitsImage
from tkp.accessors.lofaraccessor import LofarAccessor
from tkp.accessors.lofaraccessor import LofarAccessorProperties


class LofarFitsImage(LofarAccessorProperties, FitsImage, LofarAccessor):
    def __init__(self, url, plane=False, beam=False, hdu=0):
        super(LofarFitsImage, self).__init__(url, plane, beam, hdu)
        header = self._get_header(hdu)
        self._antenna_set = header['ANTENNA']
        self._channels = header['CHANNELS']
        self._ncore = header['NCORE']
        self._nintl = header['NINTL']
        self._nremote = header['NREMOTE']
        self._subbands = header['SUBBANDS']
        self._subbandwidth = header['SUBBANDW']
        if 'TAU_TIME' in header:
            # This may have been set already by _timeparse, but if defined
            # here it is set by our inject script and should be used
            self._tau_time = header['TAU_TIME']
