#!/usr/bin/env python
"""A small wrapper around nosetests.
Avoids disruptive messages when viewing error messages.
"""
import pytest
import sys

def main():
    import logging
    logging.basicConfig(level=logging.DEBUG)
    # Suppress sigma-clipping debug log:
    logging.getLogger('tkp.sourcefinder.image.sigmaclip').setLevel(logging.ERROR)
    pytest.main(sys.argv[1:])

if __name__ == '__main__':
    main()


