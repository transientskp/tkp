import numpy
import logging
from tkp.accessors.fitsimage import FitsImage

logger = logging.getLogger(__name__)


class FitsImageBlob(FitsImage):
    """
    A Fits image Blob. Same as ``tkp.accessors.fitsimage.FitsImage`` but
    constructed from an in memory fits file, not a fits file on disk.
    """
    def __init__(self, hdulist, plane=None, beam=None, hdu_index=0):
        # set the URL in case we need it during header parsing for error loggign
        self.url = "AARTFAAC streaming image"
        super(FitsImage, self).__init__()

        self.header = self._get_header(hdulist, hdu_index)
        self.wcs = self.parse_coordinates()
        self.data = self.read_data(hdulist, hdu_index, plane)
        self.taustart_ts, self.tau_time = self.parse_times()
        self.freq_eff, self.freq_bw = self.parse_frequency()
        self.pixelsize = self.parse_pixelsize()

        elements = "memory://AARTFAAC", self.taustart_ts, self.tau_time,\
                   self.freq_eff, self.freq_bw
        self.url = "_".join([str(x) for x in elements])

        if beam:
            (bmaj, bmin, bpa) = beam
        else:
            (bmaj, bmin, bpa) = self.parse_beam()
        self.beam = self.degrees2pixels(
                bmaj, bmin, bpa, self.pixelsize[0], self.pixelsize[1]
            )
        self.centre_ra, self.centre_decl = self.calculate_phase_centre()

        # Bonus attribute
        if 'TELESCOP' in self.header:
            self.telescope = self.header['TELESCOP']

    def _get_header(self, hdulist, hdu_index):
        return hdulist[hdu_index].header

    def read_data(self, hdulist, hdu_index, plane):
        hdu = hdulist[hdu_index]
        data = numpy.float64(hdu.data.squeeze())
        if plane is not None and len(data.shape) > 2:
            data = data[plane].squeeze()
        n_dim = len(data.shape)
        if n_dim != 2:
            logger.warn(
                "Loaded datacube with %s dimensions, assuming Stokes I and taking plane 0" % n_dim)
            data = data[0, :, :]
        data = data.transpose()
        return data