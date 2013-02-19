#                                                         LOFAR IMAGING PIPELINE
#
#                                                                AWimager recipe
#                                                                Evert Rol, 2012
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement
from subprocess import CalledProcessError
import sys
import os
import shutil
import tempfile

from lofarpipe.support.pipelinelogging import log_time
from lofarpipe.support.utilities import catch_segfaults
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.lofarexceptions import ExecutableMissing
from lofarpipe.support.pipelinelogging import CatchLog4CPlus


class awimager(LOFARnodeTCP):
    def run(self, executable, options, msfile, wd):
        with log_time(self.logger):
            self.logger.info("Processing %s", msfile)

            try:
                if not os.access(executable, os.X_OK):
                    raise ExecutableMissing(executable)
                wd = os.path.dirname(msfile)
                env = {'OMP_NUM_THREADS': str(options.pop('nthreads', 1)),
                       'HOME': os.environ['HOME']}
                options['ms'] = msfile
                options['image'] = msfile + ".img"
                option_strings = ["%s=%s" % (k, v) for k, v in options.iteritems()]
                cmd = [executable]
                cmd.extend(option_strings)
                catch_segfaults(cmd, wd, env, self.logger)
            except ExecutableMissing, e:
                self.logger.error("%s not found" % (e.args[0]))
                return 1
            except Exception, e:
                self.logger.exception(e)
                return 1
            finally:
                pass
            return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(awimager(jobid, jobhost, jobport).run_with_stored_arguments())
