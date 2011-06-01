#
# LOFAR Transients Key Project
"""
General purpose astronomical coordinate handling routines.
"""


import math
import wcslib
import logging
import datetime
import pytz
import ctypes

# Note that wcstools takes a +ve longitude as WEST.
CORE_LAT = 52.9088
CORE_LON = -6.8689
# We'll need the libwcstools library (available in the TKP repository as
# external/libwcstools) somewhere on the ctypes library search path.
WCSTOOLS_NAME = "libwcstools.so"


def julian_date(time=None, modified=False):
    """Return the Julian Date: the number of days (including fractions) which
    have elapsed between noon, UT on 1 January 4713 BC and the specified time.

    If modified is True, return the Modified Julian Date: the number of days
    (including fractions) which have elapsed between the start of 17 November
    1858 AD and the specified time. Takes a datetime.datetime object as
    input.
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


def jd2lst(jd, lon=CORE_LON):
    """Return the Local Sidereal Time in seconds.

    Starts with Julian Date. Default logitude is that of LOFAR core:
    note that wcstools takes a positive longitude as being WEST.
    """
    wcstools = ctypes.cdll.LoadLibrary(WCSTOOLS_NAME)
    wcstools.setlongitude(ctypes.c_double(lon))
    wcstools.jd2lst.restype = ctypes.c_double
    c_jd = ctypes.c_double(jd)
    return wcstools.jd2lst(c_jd)


def mjd2lst(mjd, lon=CORE_LON):
    """Modified Julian Date to Local Sidereal Time; uses jd2lst"""
    return jd2lst(mjd + 2400000.5, lon=lon)


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


def mjds2lst(mjds, lon=CORE_LON):
    """Return the local sidereal time in degrees.  Starts with mean julian
    date in seconds, as is the time column from a measurement set.  Default
    logitude is that of LOFAR core."""
    # That is, this should be a drop-in replacement for old_mjds2lst(), below.
    return sec2deg(mjd2lst(sec2days(mjds), lon=lon))


def old_mjds2lst(MJDs, lon=6.8689):
    """DEPRECATED
    Return the local sidereal time in degrees.  Starts with mean julian
    date in seconds, as is the time column from a measurement set.  Default
    logitude is that of LOFAR core."""

    logging.debug("old_mjds2lst() is deprecated: try mjds2lst() instead")

    # MJD of midnight (am) on 2000 Jan 1 (which I think is where the
    # MS times in seconds date from) - this is some kind of reference
    # date --editor's note -- MJD starts at Nov 17, 1858
    t0 = 51544
    l0 = 99.967794687
    l1 = 360.98564736628603
    l2 = 2.907879e-13
    l3 = -5.302e-22
    # MJD days from 1 Jan 2000  -- compared this to web and it is ok
    MJD_2000 = MJDs / (24 * 3600) - t0
    sidereal_time = (l0 + (l1 * MJD_2000) + (l2 * MJD_2000 * MJD_2000) +
                     (l3 * MJD_2000 * MJD_2000) + lon)
    mst = sidereal_time - (360 * math.floor(sidereal_time / 360.0))
    #print 'LST: %5.3f' % mst

    return mst


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


def hmstora(rah, ram, ras):
    """Convert RA in hours, minutes, seconds format to decimal
    degrees format.

    Keyword arguments:
    rah,ram,ras -- RA values (h,m,s)

    Return value:
    radegs -- RA in decimal degrees

    """
    if rah > 360 or ram > 59 or ras > 59:
        raise ValueError("coordinate out of range")
    if rah < 0 or ram < 0 or ras < 0:
        raise ValueError("coordinate out of range")
    hrs = (float(rah)+(float(ram)/60)+(float(ras)/3600.0))
    if hrs > 24:
        raise ValueError("coordinate out of range")
    return 15 * hrs


def dmstodec(decd, decm, decs):
    """Convert Dec in degrees, minutes, seconds format to decimal
    degrees format.

    Keyword arguments:
    decd, decm, decs -- list of Dec values (d,m,s)

    Return value:
    decdegs -- Dec in decimal degrees

    """
    if decd > 90 or decd < -90:
        raise ValueError("degrees out of range")
    if decm > 59 or decm < -59:
        raise ValueError("minutes out of range")
    if decs > 59 or decs < -59:
        raise ValueError("seconds out of range")
    sign = -1 if decd < 0 or decm < 0 or decs < 0 else 1
    decdegs = abs(decd) + abs(decm) / 60. + abs(decs) / 3600.
    if decdegs > 90:
        raise ValueError("coordinates out of range")

    return sign * decdegs


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

    return (3600 * math.degrees(math.acos(
        (math.cos(b) * math.cos(c)) + (math.sin(b) * math.sin(c) *
                                       math.cos(math.radians(ra1 - ra2))))))


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


# Find the declination of a point in a radio image, given l,m and field centre
def l(ra, dec, cra, incr):
    """Convert a coordinate in RA,Dec into a direction cosine m

    Keyword arguments:
    ra,dec -- Source location
    cra -- RA centre of the field
    incr -- number of degrees per pixel (negative in the case of RA)

    Return value:
    l -- Direction cosine

    """
    return ((math.cos(math.radians(dec)) * math.sin(math.radians(ra - cra))) /
            (math.radians(incr)))


# Find the l direction cosine in a radio image, given an RA and Dec and the
# field centre
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


# Find the l direction cosine in a radio image, given an RA and Dec and the
# field centre
def lm_to_radec(ra0, dec0, l, m):
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


# Calculate l, m, n from RA,Dec and phase center.
# Note: As done in Meqtrees, which seems to differ slightly from
# l, m functions above.
def eq_to_gal(ra, dec):
    """Find the Galactic co-ordinates of a source given the equatorial
    co-ordinates

    Keyword arguments:
    (alpha,delta) -- RA, Dec in decimal degrees

    Return value:
    (l,b) -- Galactic longitude and latitude, in decimal degrees

    """

    R = [[-0.054875539726, -0.873437108010, -0.483834985808],
         [0.494109453312, -0.444829589425, +0.746982251810],
         [-0.867666135858, -0.198076386122, +0.455983795705]]
    s = [math.cos(math.radians(ra)) * math.cos(math.radians(dec)),
         math.sin(math.radians(ra)) * math.cos(math.radians(dec)),
         math.sin(math.radians(dec))]
    sg = []
    sg.append(s[0] * R[0][0] + s[1] * R[0][1] + s[2] * R[0][2])
    sg.append(s[0] * R[1][0] + s[1] * R[1][1] + s[2] * R[1][2])
    sg.append(s[0] * R[2][0] + s[1] * R[2][1] + s[2] * R[2][2])
    b = math.degrees(math.asin(sg[2]))
    l = math.degrees(math.atan2(sg[1], sg[0]))

    if l < 0:
        l += 360

    return (l, b)


# Return the Galactic co-ordinates of a point given in equatorial co-ordinates
def gal_to_eq(l, b):
    """Find the Galactic co-ordinates of a source given the equatorial
    co-ordinates

    Keyword arguments:
    (l, b) -- Galactic longitude and latitude, in decimal degrees

    Return value:
    (alpha, delta) -- RA, Dec in decimal degrees

    """

    Rinv = [[-0.054875539692115144, 0.49410945328828509, -0.86766613584223429],
            [-0.87343710799750596, -0.44482958942460415, -0.19807638609701342],
            [-0.4838349858324969, 0.74698225182667777, 0.45598379574707293]]
    sg = [math.cos(math.radians(l)) * math.cos(math.radians(b)),
          math.sin(math.radians(l)) * math.cos(math.radians(b)),
          math.sin(math.radians(b))]
    s = []
    s.append(sg[0] * Rinv[0][0] + sg[1] * Rinv[0][1] + sg[2] * Rinv[0][2])
    s.append(sg[0] * Rinv[1][0] + sg[1] * Rinv[1][1] + sg[2] * Rinv[1][2])
    s.append(sg[0] * Rinv[2][0] + sg[1] * Rinv[2][1] + sg[2] * Rinv[2][2])
    dec = math.degrees(math.asin(s[2]))
    ra = math.degrees(math.atan2(s[1], s[0]))
    if ra < 0:
        ra = ra + 360

    return (ra, dec)


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
    wcstools = ctypes.cdll.LoadLibrary(WCSTOOLS_NAME)
    c_ra, c_dec = ctypes.c_double(ra), ctypes.c_double(dec)
    p_ra, p_dec = ctypes.pointer(c_ra), ctypes.pointer(c_dec)

    if insys == CoordSystem.FK4:
        if outsys == CoordSystem.FK5:
            wcstools.fk425(p_ra, p_dec)
    elif insys == CoordSystem.FK5:
        if outsys == CoordSystem.FK4:
            wcstools.fk524(p_ra, p_dec)

    return c_ra.value, c_dec.value


class WCS(wcslib.wcs):
    """
    wcslib.wcs, extended to support different coordinate systems using
    wcstools.
    """

    # A signal to use for message passing.
    change = "WCS changed"

    def __setattr__(self, attrname, value):
        if attrname == "coordsys" or attrname == "outputsys":
            wcslib.wcs.__setattr__(self, attrname, coordsystem(value))
            # Notify any objects which depend on this that their parameters
            # have changed.
        else:
            wcslib.wcs.__setattr__(self, attrname, value)

    def p2s(self, pixpos):
        ra, dec = wcslib.wcs.p2s(self, pixpos)
        try:
            if self.outputsys != self.coordsys:
                ra, dec = convert_coordsystem(ra, dec,
                    self.coordsys, self.outputsys)
        except AttributeError:
            logging.debug("Equinox conversion undefined.")
        return [ra, dec]

    def s2p(self, spatialpos):
        ra, dec = spatialpos
        try:
            if self.outputsys != self.coordsys:
                ra, dec = convert_coordsystem(ra, dec,
                    self.outputsys, self.coordsys)
        except AttributeError:
            logging.debug("Equinox conversion undefined.")
        x, y = wcslib.wcs.s2p(self, [ra, dec])
        return [x, y]
