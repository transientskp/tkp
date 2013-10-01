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
    old_stream = os.dup(output_stream.fileno())
    try:
        with SpooledTemporaryFile() as s:
            os.dup2(s.fileno(), output_stream.fileno())
            yield
            s.seek(0)
            destination.write(s.read())
        os.dup2(old_stream, output_stream.fileno())
    finally:
        # Clean up the file descriptor
        os.close(old_stream)
