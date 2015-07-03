"""
Tests the log message transportation mechanism.
"""
import unittest
import logging

try:
    import celery
    CELERY_INSTALLED = True
except ImportError:
    CELERY_INSTALLED = False

if CELERY_INSTALLED:
    from tkp.distribute.celery.log import setup_event_listening
    from tkp.distribute.celery import celery_app
    from tkp.distribute.celery.tasks import test_log



@unittest.skipUnless(CELERY_INSTALLED, 'requires celery')
class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs."""

    def __init__(self, *args, **kwargs):
        self.reset()
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.records.append(record)

    def reset(self):
        self.records = []

@unittest.skipUnless(CELERY_INSTALLED, 'requires celery')
class TestCelery(unittest.TestCase):
    """
    Tests related to distributing jobs using celery
    """

    @unittest.skip("Enable this if you have broker and worker running")
    def test_remote_task_logger(self):
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
        mock_handler.setLevel(logging.INFO)
        result = test_log()

        for record in mock_handler.records:
            if record.name == 'tkp.distribute.celery.tasks':
                self.assertTrue(record.levelno in check)
                check.remove(record.levelno)
        self.assertFalse(len(check))

    def test_local_task_logger(self):
        """
        Logging should also work if you run it locally
        """
        setup_event_listening(celery_app)
        mock_handler = MockLoggingHandler()
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(mock_handler)
        check = {logging.INFO, logging.WARNING, logging.ERROR, logging.DEBUG}
        mock_handler.reset()
        test_log()
        for record in mock_handler.records:
            if record.name == 'tkp.distribute.celery.tasks':
                self.assertTrue(record.levelno in check)
                check.remove(record.levelno)
        self.assertFalse(len(check))
