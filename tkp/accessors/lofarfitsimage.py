from tkp.accessors import FitsImage
from tkp.accessors.lofaraccessor import LofarAccessor
from tkp.accessors.lofaraccessor import LofarAccessorProperties


class LofarFitsImage(FitsImage, LofarDataAccessor, LofarAccessorProperties):
    def __init__(self, url, plane=False, beam=False, hdu=0):
        super(LofarFitsImage, self).__init__(url, plane, beam, hdu)
        self._override_tau_time()
        self._antenna_set = header['ANTENNA']
        self._channels = header['CHANNELS']
        self._ncore = header['NCORE']
        self._nintl = header['NINTL']
        self._nremote = header['NREMOTE']
        self._subbands = header['SUBBANDS']
        self._subbandwidth = header['SUBBANDW']

    def _override_tau_time(self):
        """This may have been set already by _timeparse, but if defined here
         it is set by our inject script and should be used"""
        if 'TAU_TIME' in self.header:
            self._tau_time = self.header['TAU_TIME']

