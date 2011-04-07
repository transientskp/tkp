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
        for transient in self.inputs['transients']:
            try:
                rise, risetime = transient.rise, transient.risetime
            except (AttributeError, TypeError):
                rise = risetime = 0
            try:
                fall, falltime = transient.fall, transient.falltime
            except (AttributeError, TypeError):
                fall = falltime = 0
            try:
                ratio = transient.risefall_ratio
            except (AttributeError, TypeError):
                ratio = 0
            try:
                timezero = transient.timezero
            except (AttributeError, TypeError), e:
                timezero = 'unknown'
            try:
                duration = "%.1f" % transient.duration
            except (AttributeError, TypeError), e:
                duration = 'unknown'
            try:
                fluxincrease_total = "%8.3e" % transient.fluxincrease_total
            except (AttributeError, TypeError), e:
                fluxincrease_total = 'unknown'
            try:
                fluxincrease_totalrelative = "%8.3e" % transient.fluxincrease_totalrelative
            except (AttributeError, TypeError):
                fluxincrease_totalrelative = 'unknown'
            classification = ""
            indent = 8 * " "
            for key, value in sorted(transient.classification.iteritems(),
                                     key=itemgetter(1), reverse=True):
                classification += "|" + indent + "%s: %.1f\n" % (key, value)
            self.logger.info("""\
\033[36m
| transient %d (%s):
|   T_0: %s  %s
|   fluxincrease
|   * total:   %s,   %s
|   rise & fall:
|   * rise:   %g,   %g
|   * fall:   %g,   %g
|   * ratio:  %f
|   classification:
%s
\033[0m
""" % (transient.srcid, transient.dataset,
           timezero, duration,
           fluxincrease_total, fluxincrease_totalrelative,
           rise, risetime, fall, falltime, ratio, classification))
            
                
        return 0


if __name__ == '__main__':
    sys.exit(prettyprint().main())
