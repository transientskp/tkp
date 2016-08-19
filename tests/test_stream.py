import unittest
from datetime import datetime
import dateutil
import tkp.stream
from tkp.testutil.stream_emu import create_fits_hdu, serialize_hdu, make_window


class TestStream(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hdu = create_fits_hdu()
        now = datetime.now()
        cls.hdu.header['date-obs'] = now.isoformat()

    def test_reconstruct(self):
        data, header = serialize_hdu(self.hdu)
        hdulist = tkp.stream.reconstruct_fits(header, data)
        dateutil.parser.parse(hdulist[0].header['date-obs'])

    def test_get_bytes(self):
        class MockSocket(object):
            def recv(self, count):
                return count * "s"

        x = tkp.stream.getbytes(MockSocket(), 10)
        self.assertEqual(x, 10 * "s")

    def test_get_bytes_closed(self):
        class MockSocket(object):
            def recv(self, _):
                return ""
        self.assertRaises(Exception, tkp.stream.getbytes, MockSocket(), 10)

    def test_read_window(self):
        window = make_window(self.hdu)
        data, header = serialize_hdu(self.hdu)

        class MockSocket(object):
            counter = 0

            def recv(self2, bytes):
                data = window[self2.counter:self2.counter+bytes]
                self2.counter += bytes
                return data

        fits_bytes, image_bytes = tkp.stream.read_window(MockSocket())
        self.assertEqual(header, fits_bytes)
        self.assertEqual(data, image_bytes)

    def test_reconstruct_fits(self):
        data, header = serialize_hdu(self.hdu)
        hdulist = tkp.stream.reconstruct_fits(header, data)
        self.assertEqual(self.hdu.data.all(), hdulist[0].data.all())
        self.assertEqual(self.hdu.header, hdulist[0].header)
