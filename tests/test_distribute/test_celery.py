"""
Tests the log message transportation mechanism.

Requires a running broker and a TKP worker accepting jobs and configured with
INFO level logging (-l INFO). Don't run with DEBUG, the worker will hang.
If not ran with logging level INFO the test will fail.
"""
import unittest
import logging
from tkp.distribute.celery.log import setup_event_listening
from tkp.distribute.celery import celery_app
from tkp.distribute.celery.tasks import bogus


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.records.append(record)

    def reset(self):
        self.records = []


@unittest.skip("disabled for now since it is quite fragile")
class TestCelery(unittest.TestCase):
    """
    Tests related to distributing jobs using celery
    """
    def testTaskLogging(self):
        """
        make sure the worker log->event->client log mechanism is working.
        """
        setup_event_listening(celery_app)
        mock_handler = MockLoggingHandler()
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(mock_handler)
        check = {logging.INFO, logging.WARNING, logging.ERROR}
        mock_handler.reset()
        bogus.delay().get()
        for record in mock_handler.records:
            if record.name == 'tkp.distribute.celery.tasks':
                self.assertTrue(record.levelno in check)
                check.remove(record.levelno)
        self.assertFalse(len(check))