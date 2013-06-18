"""
Test functions used for manipulating coordinates in the TKP pipeline.
"""

import pytz

import unittest2 as unittest
from pyrap.measures import measures

import datetime
from tkp.utility import coordinates


class mjd2lstTest(unittest.TestCase):
    # Note that the precise conversion can vary slightly depending on the
    # casacore measures database, so we allow for a 1s uncertainty in the
    # results
    MJD = 56272.503491875

    def testDefaultLocation(self):
        last = 64496.73666805029
        self.assertTrue(abs(coordinates.mjd2lst(self.MJD) - last) < 1.0)

    def testSpecificLocation(self):
        last = 73647.97547170892
        dm = measures()
        position = dm.position("itrf", "1m", "1m", "1m")
        self.assertTrue(abs(coordinates.mjd2lst(self.MJD, position) - last) < 1.0)


class jd2lsttest(unittest.TestCase):
    # Note that the precise conversion can vary slightly depending on the
    # casacore measures database, so we allow for a 1s uncertainty in the
    # results
    JD = 56272.503491875 + 2400000.5

    def testdefaultlocation(self):
        last = 64496.73666805029
        self.assertTrue(abs(coordinates.jd2lst(self.JD) - last) < 1.0)

    def testspecificlocation(self):
        last = 73647.97547170892
        dm = measures()
        position = dm.position("itrf", "1m", "1m", "1m")
        self.assertTrue(abs(coordinates.jd2lst(self.JD, position) - last) < 1.0)


class gal_to_eq_and_eq_to_gal_Test(unittest.TestCase):
    knownValues = (
        [(10, 10), (262.89288972929216, -15.207965232900214)],
        [(350, -10), (271.0071629114459, -42.544903877104645)],
        [(1, 1), (266.0298496879791, -27.561144848129747)],
        [(118.27441982715264, -52.7682822322771), (10, 10)],
        [(67.05481764677926, -62.47515197465108), (350, -10)],
        [(98.9410284460564, -59.6437963999095), (1, 1)]
    )

    def testKnownValues(self):
        for coord_pair in self.knownValues:
            gal_l, gal_b = coord_pair[0]
            ra, dec = coord_pair[1]

            self.assertAlmostEqual(coordinates.gal_to_eq(gal_l, gal_b)[0], ra, 3)
            self.assertAlmostEqual(coordinates.gal_to_eq(gal_l, gal_b)[1], dec, 3)

            self.assertAlmostEqual(coordinates.eq_to_gal(ra, dec)[0], gal_l, 3)
            self.assertAlmostEqual(coordinates.eq_to_gal(ra, dec)[1], gal_b, 3)


class ratohmsTest(unittest.TestCase):
    knownValues = ((0, (0, 0, 0)),
        (90, (6, 0, 0)),
        (180, (12, 0, 0)),
        (-180, (12, 0, 0)),
        (-540, (12, 0, 0)),
        (270, (18, 0, 0)),
        (360, (0, 0, 0)),
        (450, (6, 0, 0)),
        (0.1, (0, 0, 24)),
        (1.0, (0, 4, 0)),
        )

    def testknownValues(self):
        for input, output in self.knownValues:
            result = coordinates.ratohms(input)
            self.assertEqual(result, output)

    def testTypes(self):
        self.assertRaises(TypeError, coordinates.ratohms, 'a')


class dectodmsTest(unittest.TestCase):
    knownValues = ((0, (0, 0, 0)),
        (45, (45, 0, 0)),
        (-45, (-45, 0, 0)),
        (90, (90, 0, 0)),
        (-90, (-90, 0, 0)),
        (0.5, (0, 30, 0)),
        (1.0/60**2, (0, 0, 1)),
        )

    def testknownValues(self):
        for input, output in self.knownValues:
            result = coordinates.dectodms(input)
            self.assertEqual(result, output)

    def testTypes(self):
        self.assertRaises(TypeError, coordinates.dectodms, 'a')

    def testRange(self):
        self.assertRaises(ValueError, coordinates.dectodms, 91)


class hmstoraTest(unittest.TestCase):
    knownValues = (((0, 0, 0), 0),
        ((6, 0, 0), 90),
        ((12, 0, 0), 180),
        ((18, 0, 0), 270),
        ((0, 0, 24), 0.1),
        ((0, 4, 0), 1.0),
        )

    def testknownValues(self):
        for input, output in self.knownValues:
            result = coordinates.hmstora(*input)
            self.assertEqual(result, output)

    def testTypes(self):
        self.assertRaises(TypeError, coordinates.hmstora, 'a')

    def testSanity(self):
        for h in range(0, 24):
            for m in range(0, 60):
                for s in range(0, 60):
                    ra = coordinates.dmstodec(h, m, s)
                    ch, cm, cs = coordinates.dectodms(ra)
                    self.assertEqual(h, ch)
                    self.assertEqual(m, cm)
                    self.assertAlmostEqual(s, cs)

    def testRange(self):
        self.assertRaises(ValueError, coordinates.hmstora, 24, 0, 1)
        self.assertRaises(ValueError, coordinates.hmstora, 25, 0, 0)
        self.assertRaises(ValueError, coordinates.hmstora, -1, 0, 0)
        self.assertRaises(ValueError, coordinates.hmstora, 0, -1, 0)
        self.assertRaises(ValueError, coordinates.hmstora, -1, 0, -1)
        self.assertRaises(ValueError, coordinates.hmstora, 12, 60, 0)
        self.assertRaises(ValueError, coordinates.hmstora, 12, 0, 60)

class dmstodecTest(unittest.TestCase):
    knownValues = (((0, 0, 0), 0),
        ((45, 0, 0), 45),
        ((-45, 0, 0), -45),
        ((90, 0, 0), 90),
        ((-90, 0, 0), -90),
        ((0, 30, 0), 0.5),
        ((0, 0, 1), 1.0/60**2)
        )

    def testknownValues(self):
        for input, output in self.knownValues:
            result = coordinates.dmstodec(*input)
            self.assertEqual(result, output)

    def testTypes(self):
        self.assertRaises(TypeError, coordinates.dmstodec, 'a')

    def testSanity(self):
        for d in range(-89, 90):
            for m in range(0, 60):
                for s in range(0, 60):
                    dec = coordinates.dmstodec(d, m, s)
                    cd, cm, cs = coordinates.dectodms(dec)
                    self.assertEqual(d, cd)
                    self.assertEqual(m, cm)
                    self.assertAlmostEqual(s, cs)
        dec = coordinates.dmstodec(90, 0, 0)
        cd, cm, cs = coordinates.dectodms(dec)
        self.assertEqual(90, cd)
        self.assertEqual(0, cm)
        self.assertAlmostEqual(0, cs)
        dec = coordinates.dmstodec(0, -30, 0)
        cd, cm, cs = coordinates.dectodms(dec)
        self.assertEqual(0, cd)
        self.assertEqual(-30, cm)
        self.assertAlmostEqual(0, cs)

    def testRange(self):
        self.assertRaises(ValueError, coordinates.dmstodec, 91, 0, 0)
        self.assertRaises(ValueError, coordinates.dmstodec, 90, 0, 1)
        self.assertRaises(ValueError, coordinates.dmstodec, -90, 0, 1)
        self.assertRaises(ValueError, coordinates.dmstodec, 0, 60, 0)
        self.assertRaises(ValueError, coordinates.dmstodec, 0, 0, 60)


class juliandate(unittest.TestCase):
    knownValues = (
        (datetime.datetime(2008, 4, 17, 12, 30, tzinfo=pytz.utc), 2454574.0208333),
        (datetime.datetime(2007, 1, 14, 13, 18, 59, 900000, tzinfo=pytz.utc), 2454115.05486),
        (datetime.datetime(1858, 11, 17, tzinfo=pytz.utc), 2400000.5),
    )

    def testknownValues(self):
        for date, jd in self.knownValues:
            calc_jd = coordinates.julian_date(date)
            self.assertAlmostEqual(calc_jd, jd)
            calc_mjd = coordinates.julian_date(date, modified=True)
            self.assertAlmostEqual(calc_mjd, jd - 2400000.5)

    def testNow(self):
        now = coordinates.julian_date()
        self.failUnless(now > 2454574)

class coordsystemTest(unittest.TestCase):
    knownValues = (
        {"fk4": (10.0, 10.0), "fk5": (10.64962347, 10.273829)},
        {"fk4": (9.351192, 9.725562), "fk5": (10.0, 10.0)},
        {"fk4": (179.357791, 45.278329), "fk5": (180, 45)},
        {"fk4": (180, 45), "fk5": (180.63913, 44.721730)},
        {"fk4": (349.35037, -10.27392), "fk5": (-10, -10)},
        {"fk4": (-10, -10), "fk5": (350.648870, -9.725590)}
    )

    def testKnownValues(self):
        # Note that RA is always positive in the range 0 < RA < 360
        for coord_pair in self.knownValues:
            ra, dec = coordinates.convert_coordsystem(
                coord_pair["fk4"][0], coord_pair["fk4"][1],
                coordinates.CoordSystem.FK4,
                coordinates.CoordSystem.FK4
            )
            self.assertAlmostEqual(ra, coord_pair["fk4"][0] % 360, 3)
            self.assertAlmostEqual(dec, coord_pair["fk4"][1], 3)

            ra, dec = coordinates.convert_coordsystem(
                coord_pair["fk5"][0], coord_pair["fk5"][1],
                coordinates.CoordSystem.FK4,
                coordinates.CoordSystem.FK4
            )
            self.assertAlmostEqual(ra, coord_pair["fk5"][0] % 360, 3)
            self.assertAlmostEqual(dec, coord_pair["fk5"][1], 3)

            ra, dec = coordinates.convert_coordsystem(
                coord_pair["fk4"][0], coord_pair["fk4"][1],
                coordinates.CoordSystem.FK4,
                coordinates.CoordSystem.FK5
            )
            self.assertAlmostEqual(ra, coord_pair["fk5"][0] % 360, 3)
            self.assertAlmostEqual(dec, coord_pair["fk5"][1], 3)

            ra, dec = coordinates.convert_coordsystem(
                coord_pair["fk5"][0], coord_pair["fk5"][1],
                coordinates.CoordSystem.FK5,
                coordinates.CoordSystem.FK4
            )
            self.assertAlmostEqual(ra, coord_pair["fk4"][0] % 360, 3)
            self.assertAlmostEqual(dec, coord_pair["fk4"][1], 3)


if __name__ == '__main__':
    unittest.main()
