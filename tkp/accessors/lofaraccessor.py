import abc
from tkp.accessors.dataaccessor import BasicAccessorProperties

class LofarAccessor(object):
    __metaclass__ = abc.ABCMeta
    """
    Additional metadata required for processing LOFAR images through QC
    checks.
    """
    @abc.abstractproperty
    def antenna_set(self):
        """
        Antenna set in use during observation. String; 'LBA_INNER', 'LBA_OUTER',
        'LBA_SPARSE', 'LBA' or 'HBA'
        """

    @abc.abstractproperty
    def channels(self):
        """
        Number of channels per subband in the first MS in the LOFAR_ORIGIN
        table.
        TODO: Check.
        """

    @abc.abstractproperty
    def ncore(self):
        """
        Number of core stations in use during observation. Integer.
        """

    @abc.abstractproperty
    def nremote(self):
        """
        Number of remote stations in use during observation. Integer.
        """

    @abc.abstractproperty
    def nintl(self):
        """
        Number of international stations in use during observation. Integer.
        """

    @abc.abstractproperty
    def subbandwidth(self):
        """
        Width of a subband in Hz.
        TODO: Check.
        """

    @abc.abstractproperty
    def subbands(self):
        """
        Number of subbands in the first MS in the LOFAR_ORIRIN table.
        TODO: Check.
        """

class LofarAccessorProperties(BasicAccessorProperties):
    #
    # Required attributes for images expected to undergo LOFAR QC.
    #
    @property
    def antenna_set(self):
        return self._antenna_set

    @property
    def channels(self):
        return self._channels

    @property
    def ncore(self):
        return self._ncore

    @property
    def nremote(self):
        return self._nremote

    @proeprty
    def nintl(self):
        return self._nintl

    @property
    def subbandwidth(self):
        return self._subbandwidth

    @property
    def subbands(self):
        return self._subbands
