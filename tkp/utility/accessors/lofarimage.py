
from tkp.utility.accessors.dataaccessor import DataAccessor

class LofarImage(DataAccessor):
    def __init__(self, source, plane=False, beam=False, hdu=0):
        super(LofarImage, self).__init__()  # Set defaults

        #self.header = hdu.header.copy()
        self._read_data(source)

    def _read_data(self, hdu):
        """
        Read and store data from our FITS file.

        NOTE: PyFITS reads the data into an array indexed as [y][x]. We
        take the transpose to make this more intuitively reasonable and
        consistent with (eg) ds9 display of the FITSImage. Transpose back
        before viewing the array with RO.DS9, saving to a FITS file,
        etc.
        """
        pass
#        data = numpy.float64(hdu.data.squeeze())
#        if not isinstance(self.plane, bool) and len(data.shape) > 2:
#            data = data[self.plane].squeeze()
#        if len(data.shape) != 2:
#            # This basically takes Stokes I if we have an image cube instead
#            # of an image.
#            # self.data=self.data[0,:,:]
#            # If you make some assumptions about the data format, that may
#            # be true, but...
#            raise IndexError("Data has wrong shape")
#        self.data = data.transpose()