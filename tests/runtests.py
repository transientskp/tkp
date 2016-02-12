#!/usr/bin/env python
"""A small wrapper around nosetests.
Turns down the monetdb logging level-
this is otherwise disruptive when viewing error messages.
"""
import sys
import nose

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('monetdb').setLevel(logging.ERROR) #Suppress MonetDB debug log.
    # Suppress sigma-clipping debug log:
    logging.getLogger('tkp.sourcefinder.image.sigmaclip').setLevel(logging.ERROR)
#    logging.getLogger().setLevel(logging.ERROR)
    nose.run(argv=sys.argv)


