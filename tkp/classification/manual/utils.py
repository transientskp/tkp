import datetime
import math


class Position(object):

    """Class that provides an astronomical Position

    All ra, dec & error values are in the same unit (presumed degrees,
    but radians would equally well work).

    Currently, the error on the ra and dec is taken to be the same for
    both directions.
    """

    def __init__(self, ra, dec, error=0):
        self.ra = ra
        self.dec = dec
        if isinstance(error, tuple):
            self.ra_err = error[0]
            self.dec_err = error[1]
        else:
            self.ra_err = self.dec_err = error

    def __str__(self):
        return "(%.3f, %.3f) +/- (%.4f, %.4f)" % (
            self.ra, self.dec, self.ra_err, self.dec_err)

    def __repr__(self):
        return "Position(ra=%.3f, dec=%.3f, error=(%.3f, %.3f)" % (
            self.ra, self.dec, self.ra_err, self.dec_err)

    def match(self, other, precision=0):
        """Matches this position object (self) with another (other) position

        Args:

            other (Position): position to match with

        Kwargs:

            precision (float): positional match accuracy in degrees

        Returns:
            (bool): whether the positions match within the precision
        
        The parameter precision is combined with the errors on both positions;
        it has the same unit as the error (and ra & dec).
        """

        dx = self.ra - other.ra
        dy = self.dec - other.dec
        delta = dx*dx + dy*dy
        error = (self.ra_err * self.ra_err + self.dec_err * self.dec_err +
                 other.ra_err * other.ra_err + other.dec_err * other.dec_err +
                 precision * precision)
        return (delta < error)


class SourceShape(object):
    """Currently empty. To be implemented"""
    pass


class DateTime(datetime.datetime):
    """Extends the datetime.datetime class with an accuracy

    The extra attribute error indicates the accuracy of the time stamp;
    it uses seconds as unit.
    """

    def __new__(cls, year, month=1, day=1, hour=0, minute=0, second=0,
                microsecond=0, error=0):
        return super(DateTime, cls).__new__(cls, year, month, day, hour,
                                            minute, second, microsecond)

    def __init__(self, year, month, day=1, hour=0, minute=0, second=0,
                 microsecond=0, error=0):
        super(DateTime, self).__init__()
        self.error = error
        self.datetime = datetime.datetime.combine(self.date(), self.time())
        
    def __reduce__(self):
        """Override this function to pickle correctly

        """
        # When pickling a datetime object and then subsequently
        # unpickling it, pickle uses an undocumented initializer, namely
        # a single string representing the current date & time (eg,
        # '\x07\xda\x02\x03\x04\x05\x06\x00\x00\x00'). This is the
        # string returned by __reduce__ (and __reduce_ex__) of the
        # datetime type.  We override __reduce__ to return an object
        # that can work with an extra argument when pickling.
        ret = (DateTime,
               (self.year, self.month, self.day, self.hour, self.minute,
               self.second, self.microsecond, self.error))
        return ret

    def __reduce_ex__(self, proto=0):
        """Override datetime's __reduce_ex__, but just use the
        __reduce__ implementation"""

        return self.__reduce__()

    def __str__(self):
        return "%s +/- %.1f" % (super(DateTime, self).__str__(), self.error)

    def __repr__(self):
        return ("DateTime(year=%d, month=%d, day=%d, hour=%d, minute=%d, "
                "second=%d, microsecond=%d, error=%.1f)" % (
            self.year, self.month, self.day, self.hour, self.minute,
            self.second, self.microsecond, self.error))

    def match(self, other, precision=0):
        """Matches this datetime object (self) with another (other) datetime

        :argument other: date-time to match with
        :type other: DateTime instance
        :keyword precision: match accuracy in seconds
        :type precision: float

        :returns: whether the dates match
        :rtype: bool
        
        The parameter precision is combined with the errors on both datetime;
        it has the same unit as the error (seconds).
        """

        delta = abs(self - other)
        delta = delta.seconds + delta.microseconds/1e6 + delta.days*86400
        error = math.sqrt(self.error * self.error + other.error * other.error +
                          precision * precision)
        return (delta < error)




# The following set of classes provide a rather difficult way out
# of the problem that, in Python 2, None < 0 evaluates to True
# (Python 3 raises a TypeError).
# 
# This problem becomes apparent in the classification part, when a
# branch tests for an attribute that is not defined: it may return
# True, while it should just ignore this test instead (since the
# information is not available).
#
# Using the classes below should raise a TypeError (like in Python 3)
# instead; the classifier should catch this TypeError and ignore the
# test.
#
# It is all rather kludgy; Better to move to Python 3 soon!

class Int(int):
    """Int that raises a typerror on comparison"""

    def __new__(cls, value):
        if isinstance(value, (int, basestring)):
            return int.__new__(cls, value)
        elif value is None:
            return int.__new__(cls, 0)
        else:
            raise TypeError("%s should be a int or None" % str(value))

    def __init__(self, value):
        self._None = value is None

    def __lt__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and int")
        else:
            return int.__lt__(self, other)

    def __gt__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and int")
        else:
            return int.__gt__(self, other)

    def __le__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and int")
        else:
            return int.__le__(self, other)

    def __ge__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and int")
        else:
            return int.__ge__(self, other)

    def __eq__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and int")
        else:
            return int.__eq__(self, other)

    def __ne__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and int")
        else:
            return int.__ne__(self, other)

    @property
    def isNone(self):
        return self._None
    

class Float(float):
    """Float that raises a typerror on comparison"""

    def __new__(cls, value):
        if isinstance(value, (float, int, long, basestring)):
            return float.__new__(cls, value)
        elif value is None:
            return float.__new__(cls, 0)
        else:
            raise TypeError("%s should be a float or None" % str(value))

    def __init__(self, value):
        self._None = value is None

    def __lt__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and float")
        else:
            return float.__lt__(self, other)

    def __gt__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and float")
        else:
            return float.__gt__(self, other)

    def __le__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and float")
        else:
            return float.__le__(self, other)

    def __ge__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and float")
        else:
            return float.__ge__(self, other)

    def __eq__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and float")
        else:
            return float.__eq__(self, other)

    def __ne__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and float")
        else:
            return float.__ne__(self, other)

    @property
    def isNone(self):
        return self._None
    

class String(str):
    """String that raises a typerror on comparison"""

    def __new__(cls, value):
        if isinstance(value, basestring):
            return str.__new__(cls, value)
        elif value is None:
            return str.__new__(cls, '')
        else:
            raise TypeError("%s should be a string or None" % str(value))

    def __init__(self, value):
        self._None = value is None

    def __lt__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and string")
        else:
            return str.__lt__(self, other)

    def __gt__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and string")
        else:
            return str.__gt__(self, other)

    def __le__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and string")
        else:
            return str.__le__(self, other)

    def __ge__(self, other):
        if self._None:
            raise TypeError("Cannot compare None and string")
        else:
            return str.__ge__(self, other)

    def __eq__(self, other):
        if self._None:
            if other is None:
                return True
            raise TypeError("Cannot compare None and string")
        else:
            return str.__eq__(self, other)

    def __ne__(self, other):
        if self._None:
            if other is None:
                return False
            raise TypeError("Cannot compare None and string")
        else:
            return str.__ne__(self, other)
    
    @property
    def isNone(self):
        return self._None
    
