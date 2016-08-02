"""
Parsing a image stream.

The window layout:

 #pragma once
 #include <stdint.h>
 #define MAGIC 0x47494A53484F4D4F
 struct output_hdr_t
 {
   uint64_t magic;               # unsigned long long
   uint32_t fits_header_size;    # unsigned long
   uint32_t array_size;          # unsigned long
   uint8_t pad[512-16];
 };
"""
from __future__ import print_function

import logging
import socket
import StringIO
import struct
import astropy.io.fits.header
import astropy.io.fits
import numpy as np
import time
import dateutil.parser
import monotonic
from itertools import repeat
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import Manager


logger = logging.getLogger(__name__)

ports = range(6666, 6672)
# the checksum is used to check if we are not drifting in the data flow
CHECKSUM = 0x47494A53484F4D4F


def extract_timestamp(hdulist):
    return dateutil.parser.parse(hdulist[0].header['date-obs'])


def getbytes(socket_, bytes_):
    """Read an amount of bytes from the socket"""
    result = StringIO.StringIO()
    count = bytes_
    while count > 0:
        recv = socket_.recv(count)
        if len(recv) == 0:
            raise Exception("Server closed connection")
        count -= len(recv)
        result.write(recv)
    return result.getvalue()


def read_window(socket_):
    """
    read raw aarfaac protocol window
    
    returns: fits_bytes, image_bytes
    """
    header_bytes = getbytes(socket_, 512)
    magic = struct.unpack('Q', header_bytes[:8])[0]
    fits_length = struct.unpack('=L', header_bytes[8:12])[0]
    array_length = struct.unpack('=L', header_bytes[12:16])[0]
    assert magic == CHECKSUM, str(magic) + '!=' + str(CHECKSUM)
    fits_bytes = getbytes(socket_, fits_length)
    image_bytes = getbytes(socket_, array_length)
    return fits_bytes, image_bytes


def reconstruct_fits(fits_bytes, image_bytes):
    """
    reconstruct a fits object from serialised fits header and data.
    """
    hdu_header = astropy.io.fits.header.Header.fromstring(fits_bytes)   
    width = hdu_header["NAXIS1"]
    length = hdu_header["NAXIS2"]
    image_array = struct.unpack(str(len(image_bytes)/4) + 'f', image_bytes)
    image_matrix = np.reshape(image_array, (width, length))
    hdu = astropy.io.fits.PrimaryHDU(image_matrix)
    hdu.header = hdu_header
    hdulist = astropy.io.fits.HDUList([hdu])
    return hdulist


def connection_handler(socket_, queue):
    """
    Handles the connection, waits until a windows is returned and puts it in
    the queue.
    """
    while True:
        try:
            fits_bytes, image_bytes = read_window(socket_)
        except Exception as e:
            logger.error("error reading data: {}".format(str(e)))
            logger.error(str(type(e)))
            break
        else:
            hdulist = reconstruct_fits(fits_bytes, image_bytes)
            queue.put(hdulist)


def connector(host, port, queue):
    """
    Tries to connect to a specific host and port, if succesful will call
    connection_handler() with the connection.
    """
    while True:
        logger.info("connecting to {}:{}".format(host, port))
        try:
            socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_.connect((host, port))
        except socket.error as e:
            logger.error("cant connect to {}:{}: {}".format(host, port, str(e)))
            logger.info("will try reconnecting in 5 seconds")
            time.sleep(5)
        else:
            connection_handler(socket_, queue)


def merger(image_queue):
    """
    Will monitor the queue for images and group them by timestamp. When an image
    with an successive timestamp is received the group is processed.
    """
    logging.info("merger thread started")
    first_image = image_queue.get()
    logging.info("merged received first image")
    images = [first_image]
    previous_timestamp = extract_timestamp(first_image)

    while True:
        new_image = image_queue.get()
        new_timestamp = extract_timestamp(new_image)
        logging.info("merged received image with timestamp {}".format(new_timestamp))
        if new_timestamp < previous_timestamp:
            logging.error("timing error, older image received after newer image")
        if new_timestamp == previous_timestamp:
            images.append(new_image)
        else:
            previous_timestamp = new_timestamp
            logging.info("collected {} images, processing...".format(len(images)))
            images = [new_image]


class AartfaacStream(object):
    def __init__(self):
        self.manager = None
        self.image_queue = None
        self.threadpool = None
        self.processpool = None
        self.connection_futures = None

    def __enter__(self):
        self.start()
        return self

    def start(self):
        self.manager = Manager()
        self.image_queue = self.manager.Queue()

        self.threadpool = ThreadPoolExecutor(max_workers=2)
        self.processpool = ProcessPoolExecutor()

        self.threadpool.submit(merger, self.image_queue)
        self.connection_futures = self.processpool.map(connector,
                                                       repeat('localhost'),
                                                       ports,
                                                       repeat(self.image_queue))

    def __exit__(self, exc_type, exc_value, traceback):
        self.threadpool.shutdown()
        self.processpool.shutdown()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    with AartfaacStream() as stream:
        for f in as_completed(stream.connection_futures):
            if f.exception() is not None:
                print('%r generated an exception: {}'.format(f.exception()))
            else:
                print(f.result())
