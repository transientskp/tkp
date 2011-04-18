# Test functions used for manipulating coordinates in the TKP pipeline.

import unittest
import tkp.utility.coordinates as coordinates

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
        ((36, 0, 0), 180),
        ((48, 0, 0), 0)
        )

    def testknownValues(self):
        for input, output in self.knownValues:
            result = coordinates.hmstora(*input)
            self.assertEqual(result, output)

    def testTypes(self):
        self.assertRaises(TypeError, coordinates.hmstora, 'a')

    def testSanity(self):
        import random
        h = random.randrange(0, 24)
        m = random.randrange(0, 60)
        s = random.randrange(0, 60)
        ra = coordinates.hmstora(h, m, s)
        ch, cm, cs = coordinates.ratohms(ra)
        self.assertEqual(h, ch)
        self.assertEqual(m, cm)
        self.assertAlmostEqual(s, cs)


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
        import random
        d = random.randrange(-90, 90)
        m = random.randrange(0, 60)
        s = random.randrange(0, 60)
        dec = coordinates.dmstodec(d, m, s)
        cd, cm, cs = coordinates.dectodms(dec)
        self.assertEqual(d, cd)
        self.assertEqual(m, cm)
        self.assertAlmostEqual(s, cs)

    def testRange(self):
        self.assertRaises(ValueError, coordinates.dmstodec, 91, 0, 0)


class juliandate(unittest.TestCase):
    import datetime, pytz
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


class wcstoolsTest(unittest.TestCase):
    def testLoad(self):
        import ctypes
        try:
            wcstools = ctypes.cdll.LoadLibrary(coordinates.WCSTOOLS_NAME)
        except OSError, message:
            self.fail(message)


if __name__ == '__main__':
    unittest.main()
