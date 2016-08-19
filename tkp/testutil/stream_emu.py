#!/usr/bin/env python
"""
This is an AARTFAAC imaging pipeline simulator. It will spawn 6 server sockets
where multiple clients can connect to. once connected the server will
send out empty fits images, with increasing timestamps. Each port has a
different band.
"""
import struct
import time
import monotonic
from datetime import datetime
import socket
import StringIO
import logging
from Queue import Queue
from os import path
import atexit
from threading import Lock, Thread, active_count
from tkp.testutil.data import DATAPATH
from astropy.io import fits
from tkp.stream import CHECKSUM

# if true only start one thread on the first port, useful for debugging
DEBUGGING = False

DEFAULT_PORTS = range(6666, 6672)
DEFAULT_FREQS = range(int(6e6), int(9e6), int(5e5))

logger = logging.getLogger(__name__)


class Repeater(object):
    """
    repeats incoming queue messages to subscribed queues
    """
    lock = Lock()
    receivers = []

    def __init__(self):
        pass

    def run(self, in_queue):
        """
        Monitor incoming queue for message, repeat them to all subscribers
        """
        while True:
            mesg = in_queue.get()
            self.put(mesg)

    def put(self, mesg):
        """
        broadcast message to all subscribers

        args:
            mesg (object):
        """
        with self.lock:
            logger.debug("relaying to {} subscribers".format(len(self.receivers)))
            [r.put(mesg) for r in self.receivers]

    def subscribe(self, queue):
        """
        Add a queue to the subscription list

        args:
            out_queue (Queue.Queue):
        """
        logger.debug("subscriber")
        with self.lock:
            self.receivers.append(queue)

    def unsubscribe(self, out_queue):
        """
        Remove a queue from the subscription list

        args:
            out_queue (Queue.Queue):
        """
        logger.debug("unsubscriber")
        with self.lock:
            try:
                self.receivers.remove(out_queue)
            except ValueError:
                logger.error("item not in queue")


def create_fits_hdu():
    """
    Create a fake AARTFAAC file used as a base for the emulated servers. Could
    be anything but for now we just take the fits file from the test data.

    returns:
        astropy.io.fits.HDUList: a fits object
    """
    hdulist = fits.open(path.join(DATAPATH, 'accessors/aartfaac.fits'))
    hdu = hdulist[0]
    return hdu


def serialize_hdu(hdu):
    """
    Serialize a fits object.

    args:
        hdu (astropy.io.fits.HDUList): a fits object
    returns:
        str: a serialized fits object.
    """
    data = struct.pack('=%sf' % hdu.data.size, *hdu.data.flatten('F'))
    header = hdu.header.tostring()
    return data, header


def create_header(fits_length, array_length):
    """
    make a AARTFAAC header. Header is padded with zeros up to 512 bytes.

    args:
        fits_lenght (int): how long will the fits header be
        array_length (int): How long will the data be

    returns:
        str: aartfaac header ready for transmission.
    """
    # 512 - 16: Q = 8, L = 4
    return struct.pack('=QLL496x', CHECKSUM, fits_length, array_length)


def make_window(hdu):
    """
    Construct a complete serialised image including aartfaac header

    args:
        hdu (astropy.io.fits.HDUList): the first header
    returns:
        str: serialised fits file
    """
    result = StringIO.StringIO()
    data, fits_header = serialize_hdu(hdu)
    header = create_header(len(fits_header), len(data))
    result.write(header)
    result.write(fits_header)
    result.write(data)
    return result.getvalue()


def client_handler(conn, addr, freq):
    """
    Handling a client connection. Will push a serialised fits image plus
    AARTFAAC header to the connected client, triggered by an external queue
    supplying timestamps.

    args:
        conn (socket.socket): The connection with the client
        addr (str): address of the client
        freq (int): the subband frequency of this connection
    """
    repeater = Repeater()
    port = conn.getsockname()[1]
    logger.info('connection from {} on {}'.format(addr, port))
    hdu = create_fits_hdu()
    hdu.header['RESTFREQ'] = str(freq)
    queue = Queue()
    repeater.subscribe(queue)
    while True:
        # block until we get a timestamp
        timestamp = queue.get()
        logger.info("sending to {} on {} ts {}".format(addr, port, timestamp))
        hdu.header['date-obs'] = timestamp.isoformat()
        window = make_window(hdu)
        try:
            conn.send(window)
        except socket.error:
            logger.info("client {} disconnected".format(addr))
            break
    conn.close()
    repeater.unsubscribe(queue)


def socket_listener(port, freq):
    """
    Will listen on a specific socket and fire of threads if a client connects.
    Will try to reconnect every 5 seconds in case of connect failure.

    args:
        port (int): On that port to listen
        freq (int): The corresponds frequency that belongs to the port
    """
    # loop and sleep for 5 until we can bind
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # don't wait for socket release
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', port))
        except socket.error as e:
            logger.error("can't bind to port {}: {}".format(port, str(e)))
            logger.error("retrying in 5 seconds...")
            time.sleep(5)
        else:
            break

    sock.listen(2)
    atexit.register(lambda s: s.close(), sock)  # close socket on exit
    logger.info("Server listening on port {}".format(port))

    while True:
        conn, addr_port = sock.accept()
        if DEBUGGING:
            client_handler(conn, addr_port[0], freq)
        else:
            t = Thread(target=client_handler, name='repeater_thread',
                       args=(conn, addr_port[0], freq))
            t.daemon = True
            t.start()


def timer(queue):
    """
    Pushes a timestamp on a Queue exactly every second.

    args:
        queue (Queue.Queue): a queue
    """
    while True:
        # We use monotonic so the timing doesn't drift.
        duty_cycle = 1  # seconds
        time.sleep(duty_cycle - monotonic.monotonic() % duty_cycle)
        now = datetime.now()
        logger.debug("timer is pushing {}".format(now))
        queue.put(now)


def emulator(ports=DEFAULT_PORTS, freqs=DEFAULT_FREQS):
    """
    Run the aartfaac stream emulator. Will listen on all ports defined in ports
    and change the frequency in the fits headers according to the freqs list.

    Daemon function, does not return.

    args:
        ports (list): list of ints representing ports
        freqs (list): list of frequencies
    """
    heartbeat_queue = Queue()
    repeater = Repeater()

    timer_thread = Thread(target=timer, name='timer_thread',
                          args=(heartbeat_queue,))
    timer_thread.daemon = True
    timer_thread.start()

    repeater_thread = Thread(target=repeater.run, name='repeater_thread',
                             args=(heartbeat_queue,))
    repeater_thread.daemon = True
    repeater_thread.start()

    # start all listening threads
    for port, freq in zip(ports, freqs):
        name = 'socket_{}_thread'.format(port)
        args = port, freq
        t = Thread(target=socket_listener, name=name, args=args)
        t.daemon = True
        t.start()

    while active_count():
        time.sleep(1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    emulator()
