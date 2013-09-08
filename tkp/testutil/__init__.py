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

class Mock(object):
    def __init__(self, returnvalue=None):
        self.callcount = 0
        self.callvalues = []
        self.returnvalue = returnvalue

    def __call__(self, *args, **kwargs):
        self.callcount += 1
        self.callvalues.append((args, kwargs))
        return self.returnvalue
