import logging
from tkp.distribute.celery.tasks import celery


class EventHandler(logging.Handler):
    """
    This log handler will emit talk-log events, which a client can listen to
    to rebroadcast the logging event.
    """
    def emit(self, record):
        with celery.events.default_dispatcher() as d:
            d.send('task-log', msg=record.getMessage(), levelno=record.levelno,
                   filename=record.filename)


def monitor_events(app):
    """
    This will add a 'task-log' event listener to the celery app, which will
    log these worker event as python log messages.
    """
    def on_event(event):
        logger = logging.getLogger(event['filename'])
        logger.log(event['levelno'], event['msg'])
    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={'task-log': on_event})
        recv.capture(limit=None, timeout=None, wakeup=True)