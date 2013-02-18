#!/usr/bin/env python
"""
this is here for backwards compatibility
"""
import sys
import trap.run.distributed

if __name__ == '__main__':
    print "WARNING: this script is here for backwards compatibility."
    print "Please use the trap-run.py script in <TRAP_INSTALL_PREFIX>/bin"
    sys.exit(trap.run.distributed.Trap().main())
