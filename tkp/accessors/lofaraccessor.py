from tkp.accessors.dataaccessor import RequiredAttributesMetaclass
from future.utils import with_metaclass


class LofarAccessor(with_metaclass(RequiredAttributesMetaclass, object)):
    """
    Additional metadata required for processing LOFAR images through QC
    checks.

    Attributes:
        antenna_set (string): Antenna set in use during observation.
            String; 'LBA_INNER', 'LBA_OUTER', 'LBA_SPARSE', 'LBA' or 'HBA'
        ncore(int): Number of core stations in use during observation.
        nremote(int): Number of remote stations in use during observation.
        nintl(int): Number of international stations in use during observation.
        subbandwidth(float): Width of a subband in Hz.
        subbands(int): Number of subbands.
    """
    _required_attributes = [
        'antenna_set',
        'ncore',
        'nremote',
        'nintl',
        'subbandwidth',
        'subbands',
    ]
