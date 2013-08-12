import os
from tempfile import SpooledTemporaryFile
from contextlib import contextmanager

@contextmanager
def redirect_stream(output_stream, destination):
    """
    Redirect anything written to ``output_stream`` (typically ``sys.stdin`` or
    ``sys.stdout``) to ``destination`` for the duration of this context.

    ``destination`` must provide a ``write()`` method.
    """
    while not isinstance(output_stream, file):
        # Looks like this is an XUnit Tee object. Try and find the "real"
        # stderr in its history.
        output_stream = output_stream._streams[-1]

    old_stream = os.dup(output_stream.fileno())
    with SpooledTemporaryFile() as s:
        os.dup2(s.fileno(), output_stream.fileno())
        yield
        s.seek(0)
        destination.write(s.read())
    os.dup2(old_stream, output_stream.fileno())
