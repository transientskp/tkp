#                                                         LOFAR IMAGING PIPELINE
#
#                                                    rficonsole (AOflagger) node
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement
from subprocess import CalledProcessError
import sys
import os.path
import shutil
import tempfile

from lofarpipe.support.pipelinelogging import log_time
from lofarpipe.support.utilities import catch_segfaults
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.lofarexceptions import ExecutableMissing
from lofarpipe.support.pipelinelogging import CatchLog4CPlus

class rficonsole(LOFARnodeTCP):
    def run(self, executable, nthreads, strategy, indirect, skip_flagged, wd, *infiles):
        with log_time(self.logger):
            self.logger.info("Processing %s" % " ".join(infiles))

            try:
                if not os.access(executable, os.X_OK):
                    raise ExecutableMissing(executable)

                working_dir = tempfile.mkdtemp(dir=wd)
                cmd = [executable, "-j", str(nthreads)]
                if strategy:
                    if os.path.exists(strategy):
                        cmd.extend(["-strategy", strategy])
                    else:
                        raise Exception("Strategy definition not available")
                if indirect:
                    cmd.extend(["-indirect-read"])
                if skip_flagged:
                    cmd.extend(["-skip-flagged"])
                cmd.extend(infiles)
                with CatchLog4CPlus(
                    working_dir,
                    self.logger.name,
                    os.path.basename(executable)
                ) as logger:
                    catch_segfaults(cmd, working_dir, None, logger)
            except ExecutableMissing, e:
                self.logger.error("%s not found" % (e.args[0]))
                return 1
            except CalledProcessError, e:
                self.logger.error(str(e))
                return 1
            except Exception, e:
                self.logger.exception(e)
                return 1
            finally:
                # Try and clean up the working directory, but don't worry if
                # it fails -- it might not have been greated before throwing
                # the exception
                try:
                    shutil.rmtree(working_dir)
                except:
                    pass

            return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(rficonsole(jobid, jobhost, jobport).run_with_stored_arguments())
