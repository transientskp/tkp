from __future__ import with_statement

"""

For info, see corresponding recipe in the ../master/ directory

"""

__author__ = 'Evert Rol / LOFAR Transients Key Project'
__email__ = 'discovery@transientskp.org'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010-2012, University of Amsterdam'
__version__ = '0.2'
__last_modification__ = '2012-01-20'


import sys, os
import traceback
import imp

from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time


class classification(LOFARnodeTCP):

    def run(self, transient, weight_cutoff, tkpconfigdir=None):
        paths = [os.path.expanduser('~/.transientskp')]
        if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
            os.environ['TKPCONFIGDIR'] = tkpconfigdir
            paths.insert(0, tkpconfigdir)
        from tkp.classification.manual.classifier import Classifier
        from tkp.classification.transient import Transient
        import tkp
        with log_time(self.logger):
            try:
                self.logger.info("Classifying transient #%d", 
                    transient.srcid)
                classifier = Classifier(transient, paths=paths)
                results = classifier.classify()
                transient.classification = {}
                for key, value in results.iteritems():
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
