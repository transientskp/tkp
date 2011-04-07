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
from contextlib import nested, closing

from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time

import numpy
import monetdb
import tkp.database.database as tkpdb
from tkp.classification.features.lightcurve import extract as extract_lightcurve
from tkp.classification.features.lightcurve import calc_background
from tkp.classification.features.lightcurve import calc_duration
from tkp.classification.features.lightcurve import calc_fluxincrease
from tkp.classification.features.lightcurve import calc_risefall
from tkp.utility.sigmaclip import sigmaclip, calcsigma, calcmean
from tkp.classification.database import STATUS
from tkp.classification.manual import (
    Transient, Position, DateTime)
from tkp.classification.features.sql import fluxincrease as sql_fluxincrease
from tkp.classification.features.sql import status as sql_status

SECONDS_IN_DAY = 86400.



class feature_extraction(LOFARnodeTCP):

    def run(self, transient, dblogin):
        with nested(log_time(self.logger),
                    closing(tkpdb.connection(**dblogin))) as (dummy, dbconnection):
                try:
                    self.cursor = dbconnection.cursor()
                    #transient = self.create_transient()
                    self.cursor.execute(sql_status, (transient.srcid,))
                    status = int(self.cursor.fetchone()[0])

                    # estimate flux incrase
                    self.cursor.execute(sql_fluxincrease,
                                        (transient.srcid,))
                    results = self.cursor.fetchall()
                    delta_t = ((results[0][0] + timedelta(results[0][1]/2.)) - 
                               (results[1][0] + timedelta(results[1][1]/2.)))
                    delta_t = delta_t.days + delta_t.seconds/SECONDS_IN_DAY
                    fluxincrease = (results[0][2]-results[1][2])
                    transient.fluxincrease_absolute = fluxincrease
                    transient.fluxincrease_time = delta_t
                    try:
                        transient.fluxincrease_relative = (
                            fluxincrease/delta_t/results[0][2])
                    except ZeroDivisionError:
                        transient.fluxincrease_relative = 0.
        
                    # get the light curve, and estimate the background
                    args = (transient.srcid,)
                    lightcurve = extract_lightcurve(self.cursor, args)

                    mean, sigma, indices = calc_background(
                        lightcurve)
                    background = {'mean': mean, 'sigma': sigma}
                    transient.background = mean

                    tstart, tend, duration = calc_duration(
                        lightcurve['obstimes'], lightcurve['inttimes'],
                        indices)
                    if tstart is not None:
                        transient.timezero = tstart
                    if duration is not None:
                        transient.duration = duration
        
                    # Calculate flux increases, over the total & relative time
                    # interval, absolute and relative increases/decreases
                    peakflux, increase, ipeak = calc_fluxincrease(
                        lightcurve, background, indices)
                    rise, fall, ratio = calc_risefall(
                        lightcurve, background, indices, ipeak)
                    transient.peakflux = peakflux
                    transient.rise = rise
                    transient.fall = fall
                    transient.ratio = ratio
        
                    # temporory fix; otherwise the algorithm can't work
                    try:
                        if (transient.fall['time'] > 0 and
                            transient.rise['time'] > 0):
                            # we're back to background; turn active status off
                            status &= ~(1 << STATUS['ACTIVE'])
                    except KeyError:
                        pass
                    transient.risefall_ratio = transient.ratio
                    try:
                        transient.risetime = transient.rise['time']
                        transient.rise = transient.rise['flux']
                    except KeyError:
                        pass
                    try:
                        transient.falltime = transient.fall['time']
                        transient.fall = transient.fall['flux']
                    except KeyError:
                        pass
                    transient.status = status
                    try:
                        transient.fluxincrease_total = increase['absolute']
                    except KeyError:
                        pass
                    try:
                        transient.fluxincrease_totalrelative = increase['percent']
                    except KeyError:
                        pass
                    self.cursor.close()
                except Exception, e:
                    self.logger.error(str(e))
                    return 1
        self.outputs['transient'] = transient
        return 0


if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(feature_extraction(jobid, jobhost, jobport).run_with_stored_arguments())
