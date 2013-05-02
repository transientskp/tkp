#!/usr/bin/env python
"""A small wrapper around nosetests.

Takes care of a '--datapath' argument (see handle_args)
and turns down the monetdb logging level-
this is otherwise disruptive when viewing error messages.
"""
import sys
import nose
from tkp.testutil.data import DATAPATH

def handle_args(args):
    """
    Quick and dirty routine to grab datapath option. Unfortunately optparse
    doesn't play well at passing arguments to a subprocess.
    """
    usage = """runtests.py [Standard nosetests args]
e.g.

"runtests.py -sv test_database"

Set TKP_TESTPATH environment variable to point to the TKP test data files.

Default path to TKP test data: {0}
""".format(DATAPATH)

    if len(args) == 1:
        print "Usage:"
        print usage
        sys.exit(1)
    return datapath, args

if __name__ == "__main__":
    import logging
    datapath, args = handle_args(sys.argv)
    logging.getLogger('monetdb').setLevel(logging.ERROR) #Suppress MonetDB debug log.
    logging.getLogger().setLevel(logging.ERROR)

    nose.run(argv=args)


