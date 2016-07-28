import struct
import time
import monotonic
from datetime import datetime
import socket
import logging
from Queue import Queue
import atexit
from itertools import repeat
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from astropy.io import fits
from tkp.stream import checksum


checksum = 0x47494A53484F4D4F
ports = range(6666, 6672)
freqs = range(6*10**6, 9*10**6, 5*10**5)

logger = logging.getLogger(__name__)


def create_fits_hdu():
    data = np.eye(10, dtype=float)
    hdu = fits.PrimaryHDU(data)
    return hdu


def serialize_hdu(hdu):
    data = struct.pack('=%sf' % hdu.data.size, *hdu.data.flatten('F'))
    header = hdu.header.tostring()
    return data, header


def create_header(fits_length, array_length):
    # 512 - 16: Q = 8, L = 4
    return struct.pack('=QLL496x', checksum, fits_length, array_length)


def client_handler(conn, addr, freq, queue):
    logging.info('connection from {}'.format(addr))
    hdu = create_fits_hdu()
    hdu.header['RESTFREQ'] = str(freq)
    while True:
        timestamp = queue.get()
        logging.info("sending fits with timestamp {}".format(timestamp))
        hdu.header['date-obs'] = timestamp.isoformat()
        data, fits_header = serialize_hdu(hdu)
        header = create_header(len(fits_header), len(data))
        try:
            conn.send(header)
            conn.send(fits_header)
            conn.send(data)
        except socket.error:
            logging.info("client {} disconnected".format(addr))
            break
    conn.close()


def socket_listener(port, freq, executor, queue):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    while True:
        try:
            sock.bind(('', port))
        except socket.error as e:
            logging.error("can't bind to port {}: {}".format(port, str(e)))
            logging.error("retrying in 5 seconds...")
            time.sleep(5)
        else:
            break
    sock.listen(10)
    atexit.register(lambda s: s.close(), sock)  # close socket on exit
    logging.info("Server listening on port {}".format(port))
    while True:
        conn, addr = sock.accept()
        executor.submit(client_handler, conn, addr, freq, queue)
        #client_handler(conn, addr, freq, queue)


def timer(queue):
    while True:
        now = datetime.now()
        logging.debug("timer is pushing {}".format(now))
        queue.put(now)
        time.sleep(1 - monotonic.monotonic() % 1)


def main():
    queue = Queue()
    with ThreadPoolExecutor(max_workers=24) as ex:
        ex.submit(timer, queue)
        socket_listener(ports[0], freqs[0], ex, queue)
        fs = [ex.submit(socket_listener, *i) for i in zip(ports, freqs, repeat(ex), repeat(queue))]


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
