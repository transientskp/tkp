import socket
import unittest
from datetime import datetime
import dateutil
from concurrent.futures import ThreadPoolExecutor
from tkp.stream import reconstruct_fits, read_window
from tkp.testutil.stream import create_fits_hdu, serialize_hdu, create_header

HOST = 'localhost'
PORT = 6666


class TestStream(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hdu = create_fits_hdu()
        now = datetime.now()
        cls.hdu.header['date-obs'] = now.isoformat()

    def test_reconstruct(self):
        data, header = serialize_hdu(self.hdu)
        hdulist = reconstruct_fits(header, data)
        timestamp = dateutil.parser.parse(hdulist[0].header['date-obs'])

    def test_network(self):
        now = datetime.now()
        self.hdu.header['date-obs'] = now.isoformat()
        data, fits_header = serialize_hdu(self.hdu)
        header = create_header(len(fits_header), len(data))
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen(1)
        e = ThreadPoolExecutor(max_workers=1)
        future = e.submit(server.accept)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))
        conn, _ = future.result()
        conn.send(header)
        conn.send(fits_header)
        conn.send(data)
        fits_bytes, image_bytes = read_window(client)
        hdulist = reconstruct_fits(fits_bytes, image_bytes)
        timestamp = dateutil.parser.parse(hdulist[0].header['date-obs'])
        e.shutdown()
        self.assertEqual(timestamp, now)
