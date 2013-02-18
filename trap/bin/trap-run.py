#!/usr/bin/env python
"""
This main recipe accepts a list of images (through images_to_process.py).
Images should be prepared with the correct keywords.
"""
import sys
import trap.run.distributed

if __name__ == '__main__':
    sys.exit(trap.run.distributed.Trap().main())