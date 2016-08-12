"""
Code for parsing streaming telescope data. For now we only support AARTFAAC
data version 1. We implemented an emulator for this stream in
`testutil.stream_emu`.
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

from Queue import Full
from multiprocessing import Manager


# the checksum is used to check if we are not drifting in the data flow
CHECKSUM = 0x47494A53484F4D4F

# how many images groups do we keep before we start dropping
BACK_LOG = 10

# use this for debugging. Will not fork processes but run everything threaded
THREADED = False

logger = logging.getLogger(__name__)


def extract_timestamp(hdulist):
    """
    args:
        hdulist (astropy.io.fits.HDUList): fits header to extract timestamp from

    returns:
        datetime.datetime: extracted timestamp

    """
    return dateutil.parser.parse(hdulist[0].header['date-obs'])


def getbytes(socket_, bytes_):
    """
    Read an amount of bytes from the socket

    args:
        socket_ (socket.socket): socket to use for reading
        bytes_ (int): amount of bytes to read
    returns:
        str: raw bytes from socket
    """
    result = StringIO.StringIO()
    count = bytes_
    while count > 0:
        recv = socket_.recv(count)
        if len(recv) == 0:
            raise socket.error("Server closed connection")
        count -= len(recv)
        result.write(recv)
    return result.getvalue()


def read_window(socket_):
    """
    read raw aarfaac protocol window

    args:
        socket_ (socket.socket): socket to read from
    returns:
        fits_bytes, image_bytes
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

    args:
        fits_bytes (str): a string with serialized fits bytes
        image_bytes (str): a string with serialized image data
    returns:
        astropy.io.fits.HDUList: the fits object

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


def connection_handler(socket_, image_queue):
    """
    Handles the connection, waits until a windows is returned and puts it in
    the queue.

    Daemon thread, will loop forever.

    args:
        socket_ (socket.socket): socket used for reading
        image_queue (Queue.Queue): used for putting images in
    """
    while True:
        try:
            fits_bytes, image_bytes = read_window(socket_)
        except Exception as e:
            logger.error("error reading data: {}".format(str(e)))
            logger.info("sleeping for 5 seconds")
            time.sleep(5)
            break
        else:
            hdulist = reconstruct_fits(fits_bytes, image_bytes)
            image_queue.put(hdulist)


def connector(host, port, image_queue):
    """
    Tries to connect to a specific host and port, if succesfull will call
    connection_handler() with the connection.

    args:
        host (str): host to connect to
        port (int): port to connect to
        image_queue (Queue.Queue): Will be used for putting the images in

    """
    while True:
        logger.info("connecting to {}:{}".format(host, port))
        try:
            socket_ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_.settimeout(5)
            socket_.connect((host, port))
        except socket.error as e:
            logger.error("cant connect to {}:{}: {}".format(host, port, str(e)))
            logger.info("will try reconnecting in 5 seconds")
            time.sleep(5)
        else:
            logger.info("connected to {}:{}".format(host, port))
            connection_handler(socket_, image_queue)


def merger(image_queue, grouped_queue):
    """
    Will monitor image_queue for images and group them by timestamp. When an
    image with an successive timestamp is received the group is put on the
    grouped queue.

    args:
        image_queue (Queue): the incoming image queue
        grouped_queue (Queue): the outgoing grouped image queue
    """
    logger.info("merger thread started")
    first_image = image_queue.get()
    logger.info("merger received first image")
    images = [first_image]
    previous_timestamp = extract_timestamp(first_image)

    while True:
        new_image = image_queue.get()
        new_timestamp = extract_timestamp(new_image)
        logger.info("merger received image with timestamp {}".format(new_timestamp))
        if new_timestamp < previous_timestamp:
            logger.error("timing error, older image received after newer image")
        if new_timestamp == previous_timestamp:
            images.append(new_image)
        else:
            previous_timestamp = new_timestamp
            logger.info("collected {} images, processing...".format(len(images)))
            try:
                grouped_queue.put(images, block=False)
            except Full:
                logger.error("grouped image queue full ({}), dropping group"
                              " ({} images)".format(grouped_queue.qsize(),
                                                    len(images)))

            images = [new_image]


def stream_generator(hosts, ports):
    """
    Connects to all hosts on port in ports. Returns a generator yielding sets of
    images with the same timestamp.

    args:
        hosts (list): list of hosts to connect to
        ports (list): list of ports to connect to
    """

    if THREADED:
        import threading
        from queue import Queue
        method = threading.Thread
        image_queue = Queue()
        grouped_queue = Queue(maxsize=BACK_LOG)
    else:
        import multiprocessing
        manager = Manager()
        image_queue = manager.Queue()
        grouped_queue = manager.Queue(maxsize=BACK_LOG)
        method = multiprocessing.Process

    for host, port in zip(hosts, ports):
        name = 'port_{}_proc'.format(port)
        args = dict(target=connector, name=name, args=(host, port, image_queue))
        con_proc = method(**args)
        con_proc.daemon = True
        con_proc.start()

    args = dict(target=merger, name='merger_proc',
                args=(image_queue, grouped_queue))
    merger_proc = method(**args)
    merger_proc.daemon = True
    merger_proc.start()

    while True:
        yield grouped_queue.get()
