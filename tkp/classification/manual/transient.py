"""

A Transient object class, that stores a variety of information related to any type of transient

.. module::
   :synposis: A Transient object class
   
.. moduleauthor: Evert Rol, Transient Key Project <software@transientskp.org>

"""


from .utils import Position
from .utils import DateTime
from .utils import Int
from .utils import Float
from .utils import String


        
class Transient(object):

    """The Transient class defines a transient object

    Characteristics (attributes) of transient objects are, for example:

    - duration

    - variability: measure for variability

    - database: database name that it matches

    - shape: point, extended, gaussian

    - position: Position object

    - timezero: DateTime object, that indicates the start time of the transient

    Not all attributes need to be available; unavailable attributes
    will be simply ignored. The classification schema decides how to handle
    these cases.
    """

    def __init__(self, srcid=0, duration=None, variability=None, database=None,
                 position=None, timezero=None, shape=None, spectralindex=None,
                 features=None):
        """

        Kwargs:

            srcid (int): database source ID, where known

            duration (float): total duration of the transient

            variability (float): measure of the variability

            database (list of strings): list of database names with
                which the source can be associated

            position (Position): transient position

            timezero (DateTime): start time and date of the transient

            shape (string): transient shape ('point', 'gaussian',
                'extended')

            spectralindex (float): spectral index of the source

            features (dict): dictionary of extracted features. Used in
                automated classification.

        """
        self.srcid = int(srcid)
        self.duration = Float(duration)
        self.variability = Float(variability)
        self.database = database if database else []
        self.shape = String(shape)
        self.position = position
        self.timezero = timezero
        self.spectralindex = Float(spectralindex)
        if features is None:
            features = {}

    def __str__(self):
        if self.duration is not None:
            if self.variability is not None:
                return "transient with duration %-6g and variability %-6g" % (
                    self.duration, self.variability)
            else:
                return "transient with duration %-6g" % (self.duration)
        elif self.variability is not None:
            return "transient with variability %-6g" % (self.variability)
        else:
            return "transient source"

    def __repr__(self):
        arglist = ["srcid=%d" % self.srcid]
        if not self.duration.isNone:
            arglist.append("duration=%.1f" % self.duration)
        if not self.variability.isNone:
            arglist.append("variability=%.2f" % self.variability)
        if len(self.database):
            arglist.append("database=%s" % self.database)
        if self.position is not None:
            arglist.append("position=%s" % repr(self.position))
        if self.timezero is not None:
            arglist.append("timezero=%s" % repr(self.timezero))
        if not self.shape.isNone:
            arglist.append("shape=%s" % self.shape)
        if not self.spectralindex.isNone:
            arglist.append("spectralindex=%.1f" % self.spectralindex)
        return "%s(%s)" % (self.__class__.__name__, ", ".join(arglist),)
