from __future__ import with_statement

"""

For info, see corresponding recipe in the ../master/ directory

"""

__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010, University of Amsterdam'
__version__ = '0.1'
__last_modification__ = '2010-09-01'


import sys, os
import traceback
import imp

from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time

from tkp.classification.manual.classification import Main
from tkp.classification.manual.classifier import Classifier
from tkp.classification.manual.transient import Transient


class classification(LOFARnodeTCP):

    def run(self, schema, path, transient, weight_cutoff):
        with log_time(self.logger):
            try:
                self.logger.info("Classifying transient #%d", 
                    transient.srcid)
                classifier = Classifier(transient)
                results = classifier.classify()
                transient.classification = {}
                for key, value in results:
                    if value > weight_cutoff:
                        transient.classification[key] = value
            except Exception, e:
                    self.logger.error(str(e))
                    self.logger.error(traceback.format_exc())
                    return 1
        self.outputs['transient'] = transient
        return 0


if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(classification(jobid, jobhost, jobport).run_with_stored_arguments())
