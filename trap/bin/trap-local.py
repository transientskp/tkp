#!/usr/bin/env python
"""
This runs the TRAP locally (not using the lofar clustering mechanisms).
This is for development purposes only.
"""
import sys
import logging
import trap.run.local

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(trap.run.local.TrapLocal().main())
