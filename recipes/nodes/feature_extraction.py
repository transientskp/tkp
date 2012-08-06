from __future__ import with_statement

"""

For info, see corresponding recipe in the ../master/ directory

"""

__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010, University of Amsterdam'
__version__ = '0.2'
__last_modification__ = '2010-09-01'


import sys, os
from datetime import timedelta
import random
import time
import traceback
from contextlib import closing
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time
import numpy
import monetdb


SECONDS_IN_DAY = 86400.



class feature_extraction(LOFARnodeTCP):

    def run(self, transient, tkpconfigdir=None):
        if tkpconfigdir:   # allow nodes to pick up the TKPCONFIGDIR
            os.environ['TKPCONFIGDIR'] = tkpconfigdir
        from tkp.database import DataBase
        from tkp.classification.features import lightcurve as lcmod
        from tkp.classification.features import catalogs as catmod
        from tkp.database import ExtractedSource
        from tkp.classification.transient import Transient
        from tkp.classification.transient import Position
        from tkp.classification.transient import DateTime
        with log_time(self.logger):
            with closing(DataBase()) as database:
                try:
                    # Dirty harry hack to get the xtrsrc (for now). !!!!!!!!!!! FIXME TIM !!!!!!!!!!!!
                    db.execute("select a.xtrsrc from assocxtrsource a where runcat=%s LIMIT 1", transient.runcatid)
                    srcid = db.fetchall()[0][0]
                    # end dirty harry hack
                    source = ExtractedSource(id=srcid, database=database)
                    lightcurve = lcmod.LightCurve(*zip(*source.lightcurve()))
                    lightcurve.calc_background()
                    lightcurve.calc_stats()
                    lightcurve.calc_duration()
                    lightcurve.calc_fluxincrease()
                    lightcurve.calc_risefall()
                    if lightcurve.duration['total']:
                        variability = (lightcurve.duration['active'] /
                                       lightcurve.duration['total'])
                    else:
                        variability = numpy.NaN
                    features = {
                        'duration': lightcurve.duration['total'],
                        'variability': variability,
                        'wmean': lightcurve.stats['wmean'],
                        'median': lightcurve.stats['median'],
                        'wstddev': lightcurve.stats['wstddev'],
                        'wskew': lightcurve.stats['wskew'],
                        'wkurtosis': lightcurve.stats['wkurtosis'],
                        'max': lightcurve.stats['max'],
                        'peakflux': lightcurve.fluxincrease['peak'],
                        'relpeakflux': lightcurve.fluxincrease['increase']['relative'],
                        'risefallratio': lightcurve.risefall['ratio'],
                        }
                    transient.duration = lightcurve.duration['total']
                    transient.timezero = lightcurve.duration['start']
                    transient.variability = variability
                    transient.features = features
                    transient.catalogs = catmod.match_catalogs(transient)
                except Exception, e:
                    raise
        self.outputs['transient'] = transient
        return 0


if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(feature_extraction(jobid, jobhost, jobport).run_with_stored_arguments())
