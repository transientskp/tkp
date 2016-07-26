import struct
import time
import numpy as np
from astropy.io import fits
from tkp.stream import checksum
import socket
from datetime import datetime
import dateutil
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from tkp.stream import reconstruct_fits, read_window


ports = range(6666, 6672)
freqs = range(6*10**6, 9*10**6, 5*10**5)
assert(len(ports) == len(freqs))


def create_fits_hdu():
    data = np.zeros((10, 10), dtype=float)
    hdu = fits.PrimaryHDU(data)
    return hdu


def serialize_hdu(hdu):
    data = struct.pack('=%sf' % hdu.data.size, *hdu.data.flatten('F'))
    header = hdu.header.tostring()
    return data, header


def create_header(fits_length, array_length):
    # 512 - 16: Q = 8, L = 4
    return struct.pack('=QLL496x', checksum, fits_length, array_length)


def handle_client(port, freq):
    print("starting server for freq {} on port {}".format(freq, port))
    hdu = create_fits_hdu()
    hdu.header['RESTFREQ'] = str(freq)
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.bind(('localhost', port))
    socket_.listen(5)
    conn, addr = socket_.accept()
    print("connection from {} on {}".format(addr, freq))
    while True:
        start = datetime.now()
        print("sending fits with timestamp {}".format(start))
        hdu.header['date-obs'] = start.isoformat()
        data, fits_header = serialize_hdu(hdu)
        header = create_header(len(fits_header), len(data))
        print("sending header")
        conn.send(header)
        print("sending fits header")
        conn.send(fits_header)
        print("sending data")
        conn.send(data)
        print("done sending")
        end = datetime.now()
        sleep = 1 - (end - start).seconds()
        print("sleeping {} seconds".format(sleep))
        time.sleep(sleep)


def run_servers():
    futures = []
    with ProcessPoolExecutor(max_workers=len(ports)) as e:
        for port, freq in zip(ports, freqs):
            futures.append(e.submit(handle_client, port, freq))
    try:
        [x.result() for x in futures]
    except KeyboardInterrupt:
        [x.cancel() for x in futures]


if __name__ == '__main__':
    run_servers()