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
