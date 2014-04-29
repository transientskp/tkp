import logging
import threading
import time
import os
import socket
import pwd

user = pwd.getpwuid(os.getuid()).pw_name
pid = os.getpid()
host = socket.getfqdn(socket.gethostname())


def monitor_events(celery_app):
    """
    adds a 'task-log' event listener to the celery app, which will log these
    worker event as python log messages.
    """
    def on_event(event):
        logger = logging.getLogger(event['name'])
        msg = "WORKER %(user)s@%(host)s(%(pid)s): %(msg)s" % event
        logger.log(event['levelno'], msg)

    with celery_app.connection() as conn:
        recv = celery_app.events.Receiver(conn, handlers={'task-log': on_event})
        recv.capture(limit=None, timeout=None, wakeup=True)


def setup_event_listening(celery_app):
    """
    capture celery log events in the background
    """
    thread = threading.Thread(target=monitor_events, args=[celery_app])
    thread.daemon = True
    thread.start()

    # we need to wait for the thread to release the import lock
    time.sleep(2)

    return thread


class TaskLogEmitter(logging.Handler):
    """
    This log handler will emit task-log events, which a client can listen to
    to rebroadcast the logging event. This should be run on the worker.
    """
    def __init__(self, celery_app, level=logging.NOTSET):
        self.celery_app = celery_app
        super(TaskLogEmitter, self).__init__(level=level)

    def emit(self, record):
        with self.celery_app.events.default_dispatcher() as d:
            d.send('task-log', msg=record.getMessage(), levelno=record.levelno,
                   pathname=record.pathname, lineno=record.lineno,
                   name=record.name, user=user,  host=host,
                   exc_info=record.exc_info)