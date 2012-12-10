# Test functions used for manipulating coordinates in the TKP pipeline.

import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import datetime
import pytz
from tkp.utility import coordinates

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


if __name__ == '__main__':
    unittest.main()
