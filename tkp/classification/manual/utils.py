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
        self.error = error
        
    def __str__(self):
        return "(%.3f, %.3f)" % (self.ra, self.dec)

    def __repr__(self):
        return "Position(ra=%.3f, dec=%.3f, error=%.3f)" % (
            self.ra, self.dec, self.error)
    
    def match(self, other, precision=0):
        """Matches this position object (self) with another (other) position

        The parameter precision is combined with the errors on both positions;
        it has the same unit as the error (and ra & dec).

        """
        
        dx = self.ra - other.ra 
        dy = self.dec - other.dec
        delta = math.sqrt(dx*dx + dy*dy)
        error = math.sqrt(self.error * self.error +
                          other.error * other.error + precision * precision)
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

    def __reduce__(self):
        """Override this function to pickle correctly

        When pickling a datetime object and then subsequently
        unpickling it, pickle uses an undocumented initializer, namely
        a single string representing the current date & time (eg,
        '\x07\xda\x02\x03\x04\x05\x06\x00\x00\x00'). This is the
        string returned by __reduce__ (and __reduce_ex__) of the
        datetime type.  We override __reduce__ to return an object
        that can work with an extra argument when pickling.
        
        """
        
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

        The parameter precision is combined with the errors on both datetime;
        it has the same unit as the error (seconds).

        """
                
        delta = abs(self - other)
        delta = delta.seconds + delta.microseconds/1e6 + delta.days*86400
        error = math.sqrt(self.error * self.error + other.error * other.error +
                          precision * precision)
        return (delta < error)
