from .utils import Position, DateTime


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
                 position=None, timezero=None, shape=None, spectralindex=None):
        self.srcid = int(srcid)
        self.duration = duration
        self.variability = variability
        self.database = database
        self.shape = shape
        self.position = position
        self.timezero = timezero
        self.spectralindex = spectralindex

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
        if self.duration is not None:
            arglist.append("duration=%.1f" % self.duration)
        if self.variability is not None:
            arglist.append("variability=%.2f" % self.variability)
        if self.database is not None:
            arglist.append("database=%s" % self.database)
        if self.position is not None:
            arglist.append("position=%s" % repr(self.position))
        if self.timezero is not None:
            arglist.append("timezero=%s" % repr(self.timezero))
        if self.shape is not None:
            arglist.append("shape=%s" % self.shape)
        if self.spectralindex is not None:
            arglist.append("spectral index=%.1f" % self.spectralindex)
        return "%s(%s)" % (self.__class__.__name__, ", ".join(arglist),)

    def read(self, db_cursor=None):
        """Set up the transient by reading from the database"""

        if not db_cursor:
            return
