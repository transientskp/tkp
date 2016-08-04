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
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
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
    #data = np.eye(10, dtype=float)
    #hdu = fits.PrimaryHDU(data)
    #hdu.header.update(emu_header_data)
    hdulist = fits.open(path.join(DATAPATH, 'accessors/aartfaac.fits'))
    hdu = hdulist[0]
    return hdu


def serialize_hdu(hdu):
    data = struct.pack('=%sf' % hdu.data.size, *hdu.data.flatten('F'))
    header = hdu.header.tostring()
    return data, header


def create_header(fits_length, array_length):
    # 512 - 16: Q = 8, L = 4
    return struct.pack('=QLL496x', CHECKSUM, fits_length, array_length)


def make_window(hdu):
    """
    Construct a complete serialised image including aartfaac header
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
    Will listen on a specific socket and fire of threads if a client connects

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

    with ThreadPoolExecutor(max_workers=4) as ex:
        # block until incoming connection, start handler thread
        while True:
            conn, addr_port = sock.accept()
            if DEBUGGING:
                client_handler(conn, addr_port[0], freq)
            else:
                ex.submit(client_handler, conn, addr_port[0], freq)


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
    heartbeat_queue = Queue()
    repeater = Repeater()

    with ThreadPoolExecutor(max_workers=len(ports) + 2) as ex:
        ex.submit(timer, heartbeat_queue)
        ex.submit(repeater.run, heartbeat_queue)
        if DEBUGGING:
            socket_listener(ports[0], freqs[0])
        else:
            fs = ex.map(socket_listener, ports, freqs)
            for f in as_completed(fs):
                logging.info(f.result())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    emulator()
