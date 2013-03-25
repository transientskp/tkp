import logging

from tkp.utility.accessors.dataaccessor import DataAccessor


logger = logging.getLogger(__name__)

class CasaImage(DataAccessor):
    def __init__(self, filename, plane=0, beam=None):
        raise NotImplementedError("Non-LOFAR CASA images not supported")
