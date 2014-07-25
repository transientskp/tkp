import unittest

from tkp.utility import coordinates
from tkp.sourcefinder import extract
from tkp.utility.uncertain import Uncertain


# Specify the number of digits you want to include when checking if positions are equal.
nod=12

class TestNCP(unittest.TestCase):
    """
    Check that we retrieve the correct position for objects in images centred
    on the North Celestial Pole.

    At the NCP (dec=90), our coordinate system becomes ambiguous. We avoid the
    problem by subtracting an infintesimal quantity from the reference dec,
    such that it is never quite 90 degrees.

    See discussion at issue #4599.
    """
    def test_3c61(self):
        # Coordinate system and position of 3C 61.1 based on an image of the
        # NCP provided by Adam Stewart.
        wcs = coordinates.WCS()
        wcs.ctype = ('RA---SIN', 'DEC--SIN')
        wcs.crval = (15.0, 90.0)
        wcs.cdelt = (-0.01111111111111, 0.01111111111111)
        wcs.crpix = (1025.0, 1025.0)
        wcs.unit  = ("deg", "deg")
        calculated_position = wcs.p2s([908, 715])
        self.assertAlmostEqual(calculated_position[0], 35.7, 1)
        self.assertAlmostEqual(calculated_position[1], 86.3, 1)


class Sanity(unittest.TestCase):
    """Some sanity checks because of issue #2787.

    Previously, 1 was added or subtracted in the
    pixel <-> sky conversion, resulting in positions
    being one pixel off in both x and y
    """

    def setUp(self):
        self.wcs = coordinates.WCS()
        self.wcs.crota = [0, 0]
        self.wcs.cdelt = [1, 1]
        self.wcs.crpix = [10, 10]
        self.wcs.crval = [10, 10]

    def tests2p(self):
        x, y = self.wcs.s2p([10, 10])
        self.assertAlmostEqual(x, 10)
        self.assertAlmostEqual(y, 10)
        x, y = self.wcs.s2p([0, 0])
        self.assertAlmostEqual(x, 0)
        self.assertAlmostEqual(y, 0)
        x, y = self.wcs.s2p([1, 1])
        self.assertAlmostEqual(x, 1)
        self.assertAlmostEqual(y, 1)

    def testp2s(self):
        r, d = self.wcs.p2s([10, 10])
        self.assertAlmostEqual(r, 10)
        self.assertAlmostEqual(d, 10)
        r, d = self.wcs.p2s([0, 0])
        self.assertAlmostEqual(r, 0)
        self.assertAlmostEqual(d, 0)
        r, d = self.wcs.p2s([1, 1])
        self.assertAlmostEqual(r, 1)
        self.assertAlmostEqual(d, 1)


class wcsSin(unittest.TestCase):
    known_values = (
        ([1442.0, 1442.0], [350.785563529949, 58.848317299883],),
        ([1441.0, 1501.0], [350.85000000000002, 60.815406379421418],),
        ([1441.0, 1381.0], [350.85000000000002, 56.814593620578577],),
        ([1381.0, 1441.0], [354.70898191482644, 58.757358624100824],),
        ([1501.0, 1441.0], [346.99101808517361, 58.757358624100824],),
    )

    # "header" parameters for this test
    # (Taken from arbitrary FITS file)
    crval = (3.508500000000E+02, 5.881500000000E+01)
    crpix = (1.441000000000E+03, 1.441000000000E+03)
    cdelt = (-3.333333333333E-02, 3.333333333333E-02)
    ctype = ('RA---SIN', 'DEC--SIN')
    crota = (0, 0)
    cunit = ('deg', 'deg')

    def setUp(self):
        # Initialise a wcs object with the above parameters
        self.wcs = coordinates.WCS()
        self.wcs.crval = self.crval
        self.wcs.crpix = self.crpix
        self.wcs.cdelt = self.cdelt
        self.wcs.ctype = self.ctype
        self.wcs.crota = self.crota
        self.wcs.cunit = self.cunit

    def testPixelToSpatial(self):
        for pixel, spatial in self.known_values:
            result = self.wcs.p2s(pixel)
            self.assertEqual([round(result[0],nod),round(result[1],nod)], [round(spatial[0],nod),round(spatial[1],nod)])

    def testSpatialToPixel(self):
        for pixel, spatial in self.known_values:
            result = map(round, self.wcs.s2p(spatial))
            self.assertEqual(result, pixel)

    def testSanity(self):
        import random
        pixel = [random.randrange(500, 1500), random.randrange(500, 1500)]
        result = map(round, self.wcs.s2p(self.wcs.p2s(pixel)))
        self.assertEqual(result, pixel)


if __name__ == '__main__':
    unittest.main()
