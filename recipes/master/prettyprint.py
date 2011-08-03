from __future__ import with_statement

"""

Pretty print the classified transients

"""

__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2011, University of Amsterdam'
__version__ = '0.1'
__last_modification__ = 'feb 2011'


import sys
import os
from operator import itemgetter

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support import lofaringredient
from lofarpipe.cuisine.parset import Parset


class prettyprint(BaseRecipe):

    inputs = {
        'transients': lofaringredient.ListField(
            '--transients',
            help="List of tkp.classification.manual.transient.Transent objects"
        )
    }

    outputs = {}

    def go(self):
        super(prettyprint, self).go()
        self.logger.info("\n====== Results ======\n")
        for transient in self.inputs['transients']:
            indent = 8 * " "
            features = ""
            for key, value in sorted(transient.features.iteritems(),
                                     key=itemgetter(1)):
                try:
                    features += "|" + indent + "%s: %.3f\n" % (key, value)
                except TypeError:  # incorrect format argument
                    features += "|" + indent + "%s: %s\n" % (key, str(value))
            classification = ""
            for key, value in sorted(transient.classification.iteritems(),
                                     key=itemgetter(1), reverse=True):
                classification += "|" + indent + "%s: %.1f\n" % (key, value)
            self.logger.info("""\
\033[36m
| transient #%d (dataset %s):
|   T0: %s  %s
|   position: %s
|   features:
%s
|   classification:
%s
\033[0m
""", transient.srcid, transient.dataset,
     transient.timezero, transient.duration,
     transient.position,
     features,
     classification)

        self.logger.info("\n--------------------\n")
        return 0


if __name__ == '__main__':
    sys.exit(prettyprint().main())
