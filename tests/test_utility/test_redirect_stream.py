from builtins import range
import unittest
import sys
import resource
from io import BytesIO
from tkp.utility.redirect_stream import redirect_stream

class RedirectStreamTestCase(unittest.TestCase):
    def test_file_limit(self):
        """
        Check that we don't leave file handles unclosed.
        """
        max_files = resource.getrlimit(resource.RLIMIT_NOFILE)[1] # hard limit
        dest = BytesIO()
        for _ in range(max_files):
            with redirect_stream(sys.__stdout__, dest):
                pass
        # If we get through that without raising an exception, we're home free

