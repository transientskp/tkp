"""
Utility routines to help in the construction of test cases. Not required for
core pipeline functionality.
"""
import contextlib
import sys

@contextlib.contextmanager
def nostderr():
    savestderr = sys.stderr
    class Devnull(object):
        def write(self, _):
            pass
    sys.stderr = Devnull()
    yield
    sys.stderr = savestderr
