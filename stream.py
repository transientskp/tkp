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

import socket
import StringIO
import struct
import astropy.io.fits.header
import astropy.io.fits
import numpy as np
from itertools import count
import dateutil.parser
import multiprocessing

HOSTNAME = 'localhost'
PORT = 6000


checksum = 0x47494A53484F4D4F


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
    assert magic == checksum, str(magic) + '!=' + str(checksum)
    fits_bytes = getbytes(socket_, fits_length)
    image_bytes = getbytes(socket_, array_length)
    return fits_bytes, image_bytes


def reconstruct_fits(fits_bytes, image_bytes):
    hdu_header = astropy.io.fits.header.Header.fromstring(fits_bytes)   
    width = hdu_header["NAXIS1"]
    length = hdu_header["NAXIS2"]
    image_array = struct.unpack(str(len(image_bytes)/4) + 'f', image_bytes)
    image_matrix = np.reshape(image_array, (width, length))
    hdu = astropy.io.fits.PrimaryHDU(image_matrix)
    hdu.header = hdu_header
    hdulist = astropy.io.fits.HDUList([hdu])
    return hdulist


def main(host, port):
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_.connect((host, port))

    previous_timestamp = None
    collection = []
    for i in range(2):
        print("tik: " + str(i))
        fits_bytes, image_bytes = read_window(socket_)
        hdulist = reconstruct_fits(fits_bytes, image_bytes)
        timestamp = dateutil.parser.parse(hdulist[0].header['date-obs'])
        collection.append(hdulist)
    return collection


if __name__ == '__main__':
    main(HOSTNAME, PORT)

