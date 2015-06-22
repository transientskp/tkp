#
# LOFAR Transients Key Project
"""
General purpose astronomical coordinate handling routines.
"""

import sys
import math
import pywcs
import logging
import datetime
import pytz

from casacore.measures import measures
from casacore.quanta import quantity

logger = logging.getLogger(__name__)

# Note that we take a +ve longitude as WEST.
CORE_LAT = 52.9088
CORE_LON = -6.8689

# ITRF position of CS002
# Should be a good approximation for anything refering to the LOFAR core.
ITRF_X = 3826577.066110000
ITRF_Y = 461022.947639000
ITRF_Z = 5064892.786

# Useful constants
SECONDS_IN_HOUR = 60**2
SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR

def julian_date(time=None, modified=False):
    """
    Calculate the Julian date at a given timestamp.



    Args:
        time (datetime.datetime): Timestamp to calculate JD for.
        modified (bool): If True, return the Modified Julian Date:
            the number of days (including fractions) which have elapsed between
            the start of 17 November 1858 AD and the specified time.
    Returns:
        float: Julian date value.
    """
    if not time:
        time = datetime.datetime.now(pytz.utc)
    mjdstart = datetime.datetime(1858, 11, 17, tzinfo=pytz.utc)
    mjd = time - mjdstart
    mjd_daynumber = (mjd.days + mjd.seconds / (24. * 60**2) +
                     mjd.microseconds / (24. * 60**2 * 1000**2))
    if modified:
        return mjd_daynumber
    return 2400000.5 + mjd_daynumber


def mjd2datetime(mjd):
    """
    Convert a Modified Julian Date to datetime via 'unix time' representation.

    NB 'unix time' is defined by the casacore/casacore package.
    """
    q = quantity("%sd" % mjd)
    return datetime.datetime.fromtimestamp(q.to_unix_time())


def mjd2lst(mjd, position=None):
    """
    Converts a Modified Julian Date into Local Apparent Sidereal Time in
    seconds at a given position. If position is None, we default to the
    reference position of CS002.

    mjd -- Modified Julian Date (float, in days)
    position -- Position (casacore measure)
    """
    dm = measures()
    position = position or dm.position(
        "ITRF", "%fm" % ITRF_X, "%fm" % ITRF_Y, "%fm" % ITRF_Z
    )
    dm.do_frame(position)
    last = dm.measure(dm.epoch("UTC", "%fd" % mjd), "LAST")
    fractional_day = last['m0']['value'] % 1
    return fractional_day * 24 * SECONDS_IN_HOUR


def mjds2lst(mjds, position=None):
    """
    As mjd2lst(), but takes an argument in seconds rather than days.

    Args:
        mjds (float):Modified Julian Date (in seconds)
        position (casacore measure): Position for LST calcs
    """
    return mjd2lst(mjds/SECONDS_IN_DAY, position)


def jd2lst(jd, position=None):
    """
    Converts a Julian Date into Local Apparent Sidereal Time in seconds at a
    given position. If position is None, we default to the reference position
    of CS002.

    Args:
        jd (float): Julian Date
        position (casacore measure): Position for LST calcs.
    """
    return mjd2lst(jd - 2400000.5, position)



# NB: datetime is not sensitive to leap seconds.
# However, leap seconds were first introduced in 1972.
# So there are no leap seconds between the start of the
# Modified Julian epoch and the start of the Unix epoch,
# so this calculation is safe.
#julian_epoch = datetime.datetime(1858, 11, 17)
#unix_epoch = datetime.datetime(1970, 1, 1, 0, 0)
#delta = unix_epoch - julian_epoch
#deltaseconds = delta.total_seconds()
#unix_epoch = 3506716800

# The above is equivalent to this:
unix_epoch = quantity("1970-01-01T00:00:00").get_value('s')

def julian2unix(timestamp):
    """
    Convert a modifed julian timestamp (number of seconds since 17 November
    1858) to Unix timestamp (number of seconds since 1 January 1970).

    Args:
        timestamp (numbers.Number): Number of seconds since the Unix epoch.

    Returns:
        numbers.Number: Number of seconds since the modified Julian epoch.
    """
    return timestamp - unix_epoch


def unix2julian(timestamp):
    """
    Convert a Unix timestamp (number of seconds since 1 January 1970) to a
    modified Julian timestamp (number of seconds since 17 November 1858).

    Args:
        timestamp (numbers.Number): Number of seconds since the modified
            Julian epoch.

    Returns:
        numbers.Number: Number of seconds since the Unix epoch.
    """
    return timestamp + unix_epoch


def sec2deg(seconds):
    """Seconds of time to degrees of arc"""
    return 15.0 * seconds / 3600.0


def sec2days(seconds):
    """Seconds to number of days"""
    return seconds / (24.0 * 3600)


def sec2hms(seconds):
    """Seconds to hours, minutes, seconds"""
    hours, seconds = divmod(seconds, 60**2)
    minutes, seconds = divmod(seconds, 60)
    return (int(hours), int(minutes), seconds)


def altaz(mjds, ra, dec, lat=CORE_LAT):
    """Calculates the azimuth and elevation of source from time and position
    on sky.  Takes MJD in seconds and ra, dec in degrees.  Returns (alt, az) in
    degrees."""

    # compute hour angle in degrees
    ha = mjds2lst(mjds) - ra
    if (ha < 0):
        ha = ha + 360

    # convert degrees to radians
    ha, dec, lat = [math.radians(value) for value in (ha, dec, lat)]

    # compute altitude in radians
    sin_alt = (math.sin(dec) * math.sin(lat) +
               math.cos(dec) * math.cos(lat) * math.cos(ha))
    alt = math.asin(sin_alt)

    # compute azimuth in radians
    # divide by zero error at poles or if alt = 90 deg
    cos_az = ((math.sin(dec) - math.sin(alt) * math.sin(lat)) /
              (math.cos(alt) * math.cos(lat)))
    az = math.acos(cos_az)
    # convert radians to degrees
    hrz_altitude, hrz_azimuth = [math.degrees(value) for value in (alt, az)]
    # choose hemisphere
    if (math.sin(ha) > 0):
        hrz_azimuth = 360 - hrz_azimuth

    return hrz_altitude, hrz_azimuth


def ratohms(radegs):
    """Convert RA in decimal degrees format to hours, minutes,
    seconds format.

    Keyword arguments:
    radegs -- RA in degrees format

    Return value:
    ra -- tuple of 3 values, [hours,minutes,seconds]

    """

    radegs %= 360
    raseconds = radegs * 3600 / 15.0
    return sec2hms(raseconds)


def dectodms(decdegs):
    """Convert Declination in decimal degrees format to hours, minutes,
    seconds format.

    Keyword arguments:
    decdegs -- Dec. in degrees format

    Return value:
    dec -- list of 3 values, [degrees,minutes,seconds]

    """

    sign = -1 if decdegs < 0 else 1
    decdegs = abs(decdegs)
    if decdegs > 90:
        raise ValueError("coordinate out of range")
    decd = int(decdegs)
    decm = int((decdegs - decd) * 60)
    decs = (((decdegs - decd) * 60) - decm) * 60
    # Necessary because of potential roundoff errors
    if decs - 60 > -1e-7:
        decm += 1
        decs = 0
        if decm == 60:
            decd += 1
            decm = 0
            if decd > 90:
                raise ValueError("coordinate out of range")

    if sign == -1:
        if decd == 0:
            if decm == 0:
                decs = -decs
            else:
                decm = -decm
        else:
            decd = -decd
    return (decd, decm, decs)


def propagate_sign(val1, val2, val3):
    """
    casacore (reasonably enough) demands that a minus sign (if required)
    comes at the start of the quantity. Thus "-0D30M" rather than "0D-30M".
    Python regards "-0" as equal to "0"; we need to split off a separate sign
    field.

    If more than one of our inputs is negative, it's not clear what the user
    meant: we raise.

    Args:
        val1(float): (,val2,val3) input values (hour/min/sec or deg/min/sec)

    Returns:
        tuple: "+" or "-" string denoting sign,
            val1, val2, val3 (numeric) denoting absolute values of inputs.
    """
    signs = [x<0 for x in (val1, val2, val3)]
    if signs.count(True) == 0:
        sign = "+"
    elif signs.count(True) == 1:
        sign, val1, val2, val3 = "-", abs(val1), abs(val2), abs(val3)
    else:
        raise ValueError("Too many negative coordinates")
    return sign, val1, val2, val3

def hmstora(rah, ram, ras):
    """Convert RA in hours, minutes, seconds format to decimal
    degrees format.

    Keyword arguments:
    rah,ram,ras -- RA values (h,m,s)

    Return value:
    radegs -- RA in decimal degrees

    """
    sign, rah, ram, ras = propagate_sign(rah, ram, ras)
    ra = quantity("%s%dH%dM%f" % (sign, rah, ram, ras)).get_value()
    if abs(ra) >= 360:
        raise ValueError("coordinates out of range")
    return ra


def dmstodec(decd, decm, decs):
    """Convert Dec in degrees, minutes, seconds format to decimal
    degrees format.

    Keyword arguments:
    decd, decm, decs -- list of Dec values (d,m,s)

    Return value:
    decdegs -- Dec in decimal degrees

    """
    sign, decd, decm, decs = propagate_sign(decd, decm, decs)
    dec = quantity("%s%dD%dM%f" % (sign, decd, decm, decs)).get_value()
    if abs(dec) > 90:
        raise ValueError("coordinates out of range")
    return dec


def angsep(ra1, dec1, ra2, dec2):
    """Find the angular separation of two sources, in arcseconds,
    using the proper spherical trig formula

    Keyword arguments:
    ra1,dec1 - RA and Dec of the first source, in decimal degrees
    ra2,dec2 - RA and Dec of the second source, in decimal degrees

    Return value:
    angsep - Angular separation, in arcseconds

    """

    b = (math.pi / 2) - math.radians(dec1)
    c = (math.pi / 2) - math.radians(dec2)
    temp = (math.cos(b) * math.cos(c)) + (math.sin(b) * math.sin(c) * math.cos(math.radians(ra1 - ra2)))

    # Truncate the value of temp at +- 1: it makes no sense to do math.acos()
    # of a value outside this range, but occasionally we might get one due to
    # rounding errors.
    if abs(temp) > 1.0:
        temp = 1.0 * cmp(temp, 0)

    return 3600 * math.degrees(math.acos(temp))


def alphasep(ra1, ra2, dec1, dec2):
    """Find the angular separation of two sources in RA, in arcseconds

    Keyword arguments:
    ra1,dec1 - RA and Dec of the first source, in decimal degrees
    ra2,dec2 - RA and Dec of the second source, in decimal degrees

    Return value:
    angsep - Angular separation, in arcseconds

    """

    return 3600 * (ra1 - ra2) * math.cos(math.radians((dec1 + dec2) / 2.0))


def deltasep(dec1, dec2):
    """Find the angular separation of two sources in Dec, in arcseconds

    Keyword arguments:
    dec1 - Dec of the first source, in decimal degrees
    dec2 - Dec of the second source, in decimal degrees

    Return value:
    angsep - Angular separation, in arcseconds

    """

    return 3600 * (dec1 - dec2)


# Find angular separation in Dec of 2 positions, in arcseconds
def alpha(l, m, alpha0, delta0):
    """Convert a coordinate in l,m into an coordinate in RA

    Keyword arguments:
    l,m -- direction cosines, given by (offset in cells) x cellsi (radians)
    alpha_0, delta_0 -- centre of the field

    Return value:
    alpha -- RA in decimal degrees
    """
    return (alpha0 + (math.degrees(math.atan2(l, (
        (math.sqrt(1 - (l*l) - (m*m)) * math.cos(math.radians(delta0))) -
        (m * math.sin(math.radians(delta0))))))))

def alpha_inflate(theta, decl):
    """Compute the ra expansion for a given theta at a given declination
    
    Keyword arguments:
    theta, decl are both in decimal degrees.
    
    Return value:
    alpha -- RA inflation in decimal degrees

    For a derivation, see MSR TR 2006 52, Section 2.1
    http://research.microsoft.com/apps/pubs/default.aspx?id=64524

    """
    if abs(decl) + theta > 89.9:
        return 180.0
    else:
        return math.degrees(abs(math.atan(math.sin(math.radians(theta)) / math.sqrt(abs(math.cos(math.radians(decl - theta)) * math.cos(math.radians(decl + theta)))))))

# Find the RA of a point in a radio image, given l,m and field centre
def delta(l, m, delta0):
    """Convert a coordinate in l, m into an coordinate in Dec

    Keyword arguments:
    l, m -- direction cosines, given by (offset in cells) x cellsi (radians)
    alpha_0, delta_0 -- centre of the field

    Return value:
    delta -- Dec in decimal degrees
    """
    return math.degrees(math.asin(m * math.cos(math.radians(delta0)) +
                                  (math.sqrt(1 - (l*l) - (m*m)) *
                                   math.sin(math.radians(delta0)))))


def l(ra, dec, cra, incr):
    """Convert a coordinate in RA,Dec into a direction cosine l

    Keyword arguments:
    ra,dec -- Source location
    cra -- RA centre of the field
    incr -- number of degrees per pixel (negative in the case of RA)

    Return value:
    l -- Direction cosine

    """
    return ((math.cos(math.radians(dec)) * math.sin(math.radians(ra - cra))) /
            (math.radians(incr)))


def m(ra, dec, cra, cdec, incr):
    """Convert a coordinate in RA,Dec into a direction cosine m

    Keyword arguments:
    ra,dec -- Source location
    cra,cdec -- centre of the field
    incr -- number of degrees per pixel

    Return value:
    m -- direction cosine

    """
    return ((math.sin(math.radians(dec)) * math.cos(math.radians(cdec))) -
            (math.cos(math.radians(dec)) * math.sin(math.radians(cdec)) *
             math.cos(math.radians(ra-cra)))) / math.radians(incr)



def lm_to_radec(ra0, dec0, l, m):
    """
    Find the l direction cosine in a radio image, given an RA and Dec and the
    field centre
    """
    # This function should be the inverse of radec_to_lmn, but it is
    # not. There is likely an error here.

    sind0 = math.sin(dec0)
    cosd0 = math.cos(dec0)
    dl = l
    dm = m
    d0 = dm * dm * sind0 * sind0 + dl * dl - 2 * dm * cosd0 * sind0
    sind = math.sqrt(abs(sind0 * sind0 - d0))
    cosd = math.sqrt(abs(cosd0 * cosd0 + d0))
    if (sind0 > 0):
        sind = abs(sind)
    else:
        sind = -abs(sind)

    dec = math.atan2(sind, cosd)

    if l != 0:
        ra = math.atan2(-dl, (cosd0 - dm * sind0)) + ra0
    else:
        ra = math.atan2((1e-10), (cosd0 - dm * sind0)) + ra0

     # Calculate RA,Dec from l,m and phase center.  Note: As done in
     # Meqtrees, which seems to differ from l, m functions above.  Meqtrees
     # equation may have problems, judging from my difficulty fitting a
     # fringe to L4086 data.  Pandey's equation is now used in radec_to_lmn

    return (ra, dec)


def radec_to_lmn(ra0, dec0, ra, dec):
    l = math.cos(dec) * math.sin(ra - ra0)
    sind0 = math.sin(dec0)
    if sind0 != 0:
        # from pandey;  gives same results for casa and cyga
        m = (math.sin(dec) * math.cos(dec0) -
             math.cos(dec) * math.sin(dec0) * math.cos(ra - ra0))
    else:
        m = 0
    n = math.sqrt(1 - l**2 - m**2)
    return (l, m, n)


def eq_to_gal(ra, dec):
    """Find the Galactic co-ordinates of a source given the equatorial
    co-ordinates

    Keyword arguments:
    (alpha,delta) -- RA, Dec in decimal degrees

    Return value:
    (l,b) -- Galactic longitude and latitude, in decimal degrees

    """
    dm = measures()

    result = dm.measure(
        dm.direction("J200", "%fdeg" % ra, "%fdeg" % dec),
        "GALACTIC"
    )
    lon_l = math.degrees(result['m0']['value']) % 360 # 0 < ra < 360
    lat_b = math.degrees(result['m1']['value'])

    return lon_l, lat_b


def gal_to_eq(lon_l, lat_b):
    """Find the Galactic co-ordinates of a source given the equatorial
    co-ordinates

    Keyword arguments:
    (l, b) -- Galactic longitude and latitude, in decimal degrees

    Return value:
    (alpha, delta) -- RA, Dec in decimal degrees

    """
    dm = measures()

    result = dm.measure(
        dm.direction("GALACTIC", "%fdeg" % lon_l, "%fdeg" % lat_b),
        "J2000"
    )
    ra = math.degrees(result['m0']['value']) % 360 # 0 < ra < 360
    dec = math.degrees(result['m1']['value'])

    return ra, dec

def eq_to_cart(ra, dec):
    """Find the cartesian co-ordinates on the unit sphere given the eq. co-ords.

        ra, dec should be in degrees.
    """
    return (math.cos(math.radians(dec)) * math.cos(math.radians(ra)), # Cartesian x
            math.cos(math.radians(dec)) * math.sin(math.radians(ra)), # Cartesian y
            math.sin(math.radians(dec))) # Cartesian z

class CoordSystem(object):
    """A container for constant strings representing different coordinate
    systems."""
    FK4 = "B1950 (FK4)"
    FK5 = "J2000 (FK5)"


def coordsystem(name):
    """Given a string, return a constant from class CoordSystem."""
    mappings = {
        'j2000': CoordSystem.FK5,
        'fk5': CoordSystem.FK5,
        CoordSystem.FK5.lower(): CoordSystem.FK5,
        'b1950': CoordSystem.FK4,
        'fk4': CoordSystem.FK4,
        CoordSystem.FK4.lower(): CoordSystem.FK4
        }
    return mappings[name.lower()]


def convert_coordsystem(ra, dec, insys, outsys):
    """
    Convert RA & dec (given in decimal degrees) between equinoxes.
    """
    dm = measures()

    if insys == CoordSystem.FK4:
        insys = "B1950"
    elif insys == CoordSystem.FK5:
        insys = "J2000"
    else:
        raise Exception("Unknown Coordinate System")

    if outsys == CoordSystem.FK4:
        outsys = "B1950"
    elif outsys == CoordSystem.FK5:
        outsys = "J2000"
    else:
        raise Exception("Unknown Coordinate System")

    result = dm.measure(
        dm.direction(insys, "%fdeg" % ra, "%fdeg" % dec),
        outsys
    )

    ra = math.degrees(result['m0']['value']) % 360 # 0 < ra < 360
    dec = math.degrees(result['m1']['value'])

    return ra, dec


class WCS(object):
    """
    Wrapper around pywcs.WCS.

    This is primarily to preserve API compatibility with the earlier,
    home-brewed python-wcslib wrapper. It includes:

      * A fix for the reference pixel lying at the zenith;
      * Raises ValueError if coordinates are invalid.
    """
    # ORIGIN is the upper-left corner of the image. pywcs supports both 0
    # (NumPy, C-style) or 1 (FITS, Fortran-style). The TraP uses 1.
    ORIGIN = 1

    # We can set these attributes on the pywcs.WCS().wcs object to configure
    # the coordinate system.
    WCS_ATTRS = ("crpix", "cdelt", "crval", "ctype", "cunit", "crota")

    def __init__(self):
        # Currently, we only support two dimensional images.
        self.wcs = pywcs.WCS(naxis=2)

    def __setattr__(self, attrname, value):
        if attrname in self.WCS_ATTRS:
            # Account for arbitrary coordinate rotations in images pointing at
            # the North Celestial Pole. We set the reference direction to
            # infintesimally less than 90 degrees to avoid any ambiguity. See
            # discussion at #4599.
            if attrname == "crval" and (value[1] == 90 or value[1] == math.pi/2):
                value = (value[0], value[1] * (1 - sys.float_info.epsilon))
            self.wcs.wcs.__setattr__(attrname, value)
        else:
            super(WCS, self).__setattr__(attrname, value)

    def __getattr__(self, attrname):
        if attrname in  self.WCS_ATTRS:
            return getattr(self.wcs.wcs, attrname)
        else:
            super(WCS, self).__getattr__(attrname)

    def p2s(self, pixpos):
        """
        Pixel to Spatial coordinate conversion.

        Args:
            pixpos (list):  [x, y] pixel position

        Returns:
            ra (float):     Right ascension corresponding to position [x, y]
            dec (float):    Declination corresponding to position [x, y]
        """
        [ra], [dec] =  self.wcs.wcs_pix2sky(pixpos[0], pixpos[1], self.ORIGIN)
        if math.isnan(ra) or math.isnan(dec):
            raise RuntimeError("Spatial position is not a number")
        return ra, dec

    def s2p(self, spatialpos):
        """
        Spatial to Pixel coordinate conversion.

        Args:
            pixpos (list):  [ra, dec] spatial position

        Returns:
            x (float):      X pixel value corresponding to position [ra, dec]
            y (float):      Y pixel value corresponding to position [ra, dec]
        """
        [x], [y] =  self.wcs.wcs_sky2pix(spatialpos[0], spatialpos[1], self.ORIGIN)
        if math.isnan(x) or math.isnan(y):
            raise RuntimeError("Pixel position is not a number")
        return x, y
