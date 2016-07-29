import struct
import time
import monotonic
from datetime import datetime
import socket
import logging
from Queue import Queue
import atexit
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import numpy as np
from astropy.io import fits
from tkp.stream import checksum


checksum = 0x47494A53484F4D4F
ports = range(6666, 6672)
freqs = range(6*10**6, 9*10**6, 5*10**5)

logger = logging.getLogger(__name__)


class Repeater(object):
    """
    repeats incoming queue messages to subscribed queues
    """
    mutex = Lock()
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
        self.mutex.acquire()
        logger.debug("relaying to {} subscribers".format(len(self.receivers)))
        [r.put(mesg) for r in self.receivers]
        self.mutex.release()

    def subscribe(self, queue):
        """
        Add a queue to the subscription list

        args:
            out_queue (Queue.Queue):
        """
        logger.debug("subscriber")
        self.mutex.acquire()
        self.receivers.append(queue)
        self.mutex.release()

    def unsubscribe(self, out_queue):
        """
        Remove a queue from the subscription list

        args:
            out_queue (Queue.Queue):
        """
        logger.debug("unsubscriber")
        self.mutex.acquire()
        try:
            self.receivers.remove(out_queue)
        except ValueError:
            logging.error("item not in queue")
        self.mutex.release()


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
    logging.info('connection from {} on {}'.format(addr, port))
    hdu = create_fits_hdu()
    hdu.header['RESTFREQ'] = str(freq)
    queue = Queue()
    repeater.subscribe(queue)
    while True:
        # block until we get a timestamp
        timestamp = queue.get()
        logging.info("sending to {} on {} ts {}".format(addr, port, timestamp))
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
    repeater.unsubscribe(queue)


def socket_listener(port, freq):
    """
    Will listen on a specific socket and fire of threads if a client connects

    args:
        port (int): On that port to listen
        freq (int): The corresponds frequency that belongs to the port
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # don't wait for socket release, useful when restarting service often
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # loop and sleep for 5 until we can bind
    while True:
        try:
            sock.bind(('', port))
        except socket.error as e:
            logging.error("can't bind to port {}: {}".format(port, str(e)))
            logging.error("retrying in 5 seconds...")
            time.sleep(5)
        else:
            break

    sock.listen(2)
    atexit.register(lambda s: s.close(), sock)  # close socket on exit
    logging.info("Server listening on port {}".format(port))

    with ThreadPoolExecutor(max_workers=4) as ex:
        # block until incoming connection, start handler thread
        while True:
            conn, addr_port = sock.accept()
            ex.submit(client_handler, conn, addr_port[0], freq)


def timer(queue):
    """
    Pushes a timestamp on a Queue exactly every second.

    args:
        queue (Queue.Queue): a queue
    """
    while True:
        # We use monotonic so the timing doesn't drift.
        time.sleep(1 - monotonic.monotonic() % 1)
        now = datetime.now()
        logging.debug("timer is pushing {}".format(now))
        queue.put(now)


def main():
    heartbeat_queue = Queue()
    repeater = Repeater()

    with ThreadPoolExecutor(max_workers=len(ports) + 2) as ex:
        ex.submit(timer, heartbeat_queue)
        ex.submit(repeater.run, heartbeat_queue)
        fs = [ex.submit(socket_listener, *i) for i in zip(ports, freqs)]
        for f in as_completed(fs):
            logging.info(f.results())

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
