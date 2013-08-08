import abc

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
        """

    @abc.abstractproperty
    def subbands(self):
        """
        Number of subbands.
        """
