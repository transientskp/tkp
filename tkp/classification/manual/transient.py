"""

A Transient object class, that stores a variety of information related to any type of transient

.. module::
   :synposis: A Transient object class
   
.. moduleauthor: Evert Rol, Transient Key Project <software@transientskp.org>

"""


from .utils import Position
from .utils import DateTime



class Undefined(object):
    """This is a small helper class to use for undefined values.

    Python's None evalutes to True or False in comparisons with actual
    values, instead of raising a TypeError. This prevents it from
    being used in the classification.py user interface, because that
    would horribly complicate the tests. Instead, if a value is simply
    unavailable, it will be assigned an Undefined() instance, and thus
    raise a TypeError.

    Note that this problem is particular to Python 2; Python 3 does
    the proper thing:
    http://docs.python.org/release/3.0.1/whatsnew/3.0.html#ordering-comparisons

    """
    
    # Note: special methods are bypassed by the Python interprester,
    # so there can't be a catch-all way of using eg __getattribute__
    # (http://docs.python.org/reference/datamodel.html#\
    # special-method-lookup-for-old-style-classes) We'll have to
    # define all those we want to catch
    
    def __lt__(self, other):
        raise TypeError("Cannot compare an undefined value")
    
    def __gt__(self, other):
        raise TypeError("Cannot compare an undefined value")
    
    def __le__(self, other):
        raise TypeError("Cannot compare an undefined value")
    
    def __ge__(self, other):
        raise TypeError("Cannot compare an undefined value")
    
    def __eq__(self, other):
        raise TypeError("Cannot compare an undefined value")
    
    def __ne__(self, other):
        raise TypeError("Cannot compare an undefined value")
    
    def __contains__(self, other):
        raise TypeError("Cannot compare an undefined value")


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
        self.duration = Undefined() if duration is None else duration
        self.variability = Undefined() if variability is None else variability
        self.database = database if database else []
        self.shape = Undefined() if shape is None else shape
        self.position = Undefined() if position is None else position
        self.timezero = Undefined() if timezero is None else timezero
        self.spectralindex = Undefined() if spectralindex is None else spectralindex
        self.features = {} if features is None else features

    def __str__(self):
        if hasattr(self, 'duration'):
            if hasattr(self, 'variability'):
                return "transient with duration %-6g and variability %-6g" % (
                    self.duration, self.variability)
            else:
                return "transient with duration %-6g" % (self.duration)
        elif hasattr(self, 'variability'):
            return "transient with variability %-6g" % (self.variability)
        else:
            return "transient source"

    def __repr__(self):
        arglist = ["srcid=%d" % self.srcid]
        if not isinstance(self.duration, Undefined):
            arglist.append("duration=%.1f" % self.duration)
        if not isinstance(self.variability, Undefined):
            arglist.append("variability=%.2f" % self.variability)
        if len(self.database):
            arglist.append("database=%s" % self.database)
        if not isinstance(self.position, Undefined):
            arglist.append("position=%s" % repr(self.position))
        if not isinstance(self.timezero, Undefined):
            arglist.append("timezero=%s" % repr(self.timezero))
        if not isinstance(self.shape, Undefined):
            arglist.append("shape=%s" % self.shape)
        if not isinstance(self.spectralindex, Undefined):
            arglist.append("spectralindex=%.1f" % self.spectralindex)
        if self.features != {}:
            arg.list.append("features=%s" % str(self.features))
        return "%s(%s)" % (self.__class__.__name__, ", ".join(arglist),)
