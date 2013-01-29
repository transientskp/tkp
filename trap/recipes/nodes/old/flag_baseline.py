#                                                         LOFAR IMAGING PIPELINE
#
#                                                             flag_baseline node
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------
from __future__ import with_statement
from cPickle import load
import os.path
import sys

from pyrap.tables import taql, table

from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time


class flag_baseline(LOFARnodeTCP):
    """
    Completely flag a series of baselines in a MeasurementSet.
    """
    def run(self, infile, baseline_filename):
        """
        baseline_filename points to a file continaing a pickled array of
        antenna pairs.
        """
        with log_time(self.logger):
            if os.path.exists(infile):
                self.logger.info("Processing %s" % (infile))
            else:
                self.logger.error("Dataset %s does not exist" % (infile))
                return 1

            if not os.path.exists(baseline_filename):
                self.logger.error(
                    "baseline file %s not found" % (baseline_filename)
                )
                return 1

            with open(baseline_filename) as file:
                baselines = load(file)

            antenna1, antenna2 = [], []
            for baseline in baselines:
                ant1, ant2 = baseline.split("&")
                antenna1.append(int(ant1))
                antenna2.append(int(ant2))


            if antenna1 and antenna2:
                cmd = "UPDATE %s SET FLAG=True WHERE any(ANTENNA1=%s and ANTENNA2=%s)" % \
                    (infile, str(antenna1), str(antenna2))
                self.logger.info("Running TaQL: " + cmd)

                try:
                    taql(cmd)
                except Exception, e:
                    self.logger.warn(str(e))
                    return 1
            else:
                self.logger.warn("No baselines specified to flag")

            # QUICK HACK: Also flag last timestep
            t = table(infile)
            maxtime = t.getcol('TIME').max()
            t.close()
            cmd = "UPDATE %s SET FLAG=True WHERE TIME=%f" % (infile, maxtime)
            self.logger.info("Running TaQL: " + cmd)
            try:
                taql(cmd)
            except Exception, e:
                self.logger.warn(str(e))
                return 1

        return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(flag_baseline(jobid, jobhost, jobport).run_with_stored_arguments())
