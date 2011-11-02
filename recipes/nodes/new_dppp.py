#                                                         LOFAR IMAGING PIPELINE
#
#                                        DPPP (Data Pre-Procesing Pipeline) node
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement
from subprocess import CalledProcessError
from logging import getLogger
import sys
import os.path
import tempfile
import shutil

from lofarpipe.support.pipelinelogging import CatchLog4CPlus
from lofarpipe.support.pipelinelogging import log_time
from lofarpipe.support.utilities import patch_parset
from lofarpipe.support.utilities import read_initscript
from lofarpipe.support.utilities import create_directory
from lofarpipe.support.utilities import catch_segfaults
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.lofarexceptions import ExecutableMissing

class dppp(LOFARnodeTCP):
    def run(
        self, infile, outfile, parset, executable, initscript,
        start_time, end_time, nthreads, clobber
    ):
        # Time execution of this job
        with log_time(self.logger):
            if os.path.exists(infile):
                self.logger.info("Processing %s" % (infile))
            else:
                self.logger.error("Dataset %s does not exist" % (infile))
                return 1

            if clobber:
                self.logger.info("Removing previous output %s" % outfile)
                shutil.rmtree(outfile, ignore_errors=True)

            self.logger.debug("Time interval: %s %s" % (start_time, end_time))

            #                                             Initialise environment
            #                 Limit number of threads used, per request from GvD
            # ------------------------------------------------------------------
            env = read_initscript(self.logger, initscript)
            if nthreads == "None": nthreads = 1
            self.logger.debug("Using %s threads for NDPPP" % nthreads)
            env['OMP_NUM_THREADS'] = str(nthreads)

            #    If the input and output filenames are the same, DPPP should not
            #       write a new MS, but rather update the existing one in-place.
            #              This is achieved by setting msout to an empty string.
            # ------------------------------------------------------------------
            if outfile == infile:
                outfile = "\"\""
            else:
                create_directory(os.path.dirname(outfile))

            #       Patch the parset with the correct input/output MS names and,
            #                                   if available, start & end times.
            #                            The uselogger option enables log4cplus.
            # ------------------------------------------------------------------
            patch_dictionary = {
                'msin': infile,
                'msout': outfile,
                'uselogger': 'True'
            }
            if start_time and start_time != "None":
                patch_dictionary['msin.starttime'] = start_time
            if end_time and end_time != "None":
                patch_dictionary['msin.endtime'] = end_time
            try:
                temp_parset_filename = patch_parset(parset, patch_dictionary)
            except Exception, e:
                self.logger.error(e)

            try:
                if not os.access(executable, os.X_OK):
                    raise ExecutableMissing(executable)

                working_dir = tempfile.mkdtemp()
                cmd = [executable, temp_parset_filename, '1']

                with CatchLog4CPlus(
                    working_dir,
                    self.logger.name + "." + os.path.basename(infile),
                    os.path.basename(executable),
                ) as logger:
                    #     Catch NDPPP segfaults (a regular occurance), and retry
                    # ----------------------------------------------------------
                    if outfile != infile:
                        cleanup_fn = lambda : shutil.rmtree(outfile, ignore_errors=True)
                    else:
                        cleanup_fn = lambda : None
                    catch_segfaults(
                        cmd, working_dir, env, logger, cleanup=cleanup_fn
                    )
            except ExecutableMissing, e:
                self.logger.error("%s not found" % (e.args[0]))
                return 1
            except CalledProcessError, e:
                #        CalledProcessError isn't properly propagated by IPython
                # --------------------------------------------------------------
                self.logger.error(str(e))
                return 1
            except Exception, e:
                self.logger.error(str(e))
                return 1
            finally:
                os.unlink(temp_parset_filename)
                shutil.rmtree(working_dir)

            return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(dppp(jobid, jobhost, jobport).run_with_stored_arguments())
