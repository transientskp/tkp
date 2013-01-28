#                                                         LOFAR IMAGING PIPELINE
#
#                                                         ASKAPsoft cimager node
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement

from subprocess import Popen, CalledProcessError, PIPE
from tempfile import mkdtemp
import os
import sys
import shutil

from pyrap.quanta import quantity
from pyrap.tables import table

from lofarpipe.support.pipelinelogging import CatchLog4CXX
from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.utilities import log_time
from lofarpipe.support.pipelinelogging import log_process_output
from lofarpipe.support.parset import Parset, patch_parset, get_parset


class cimager_trap(LOFARnodeTCP):
    #                 Handles running a single cimager process on a compute node
    # --------------------------------------------------------------------------
    def run(self, imager_exec, vds, parset, resultsdir, start_time, end_time):
        #       imager_exec:                          path to cimager executable
        #               vds:           VDS file describing the data to be imaged
        #            parset:                                imager configuration
        #        resultsdir:                         place resulting images here
        #        start_time:                        )    time range to be imaged
        #          end_time:                        )   in seconds (may be None)
        # ----------------------------------------------------------------------
        with log_time(self.logger):
            self.logger.info("Processing %s" % (vds,))

            #    Bail out if destination exists (can thus resume a partial run).
            #                                            Should be configurable?
            # ------------------------------------------------------------------
            parset_data = Parset(parset)
            image_names = parset_data.getStringVector("Cimager.Images.Names")
            for image_name in image_names:
                outputfile = os.path.join(resultsdir, image_name + ".restored")
                self.logger.info(outputfile)
                if os.path.exists(outputfile):
                    self.logger.info("Image already exists: aborting.")
                    return 0
            try:
                working_dir = mkdtemp()

                #   If a time range has been specified, copy that section of the
                #                                  input MS and only image that.
                # --------------------------------------------------------------
                query = []
                if start_time:
                    start_time = quantity(float(start_time), 's')
                    query.append("TIME > %f" % start_time.get('s').get_value())
                if end_time:
                    end_time = quantity(float(end_time), 's')
                    query.append("TIME < %f" % end_time.get('s').get_value())
                query = " AND ".join(query)
                if query:
                    #                             Select relevant section of MS.
                    # ----------------------------------------------------------
                    self.logger.debug("Query is %s" % query)
                    output = os.path.join(working_dir, "timeslice.MS")
                    vds_parset = get_parset(vds)
                    t = table(vds_parset.getString("FileName"))
                    t.query(query, name=output)
                    #       Patch updated information into imager configuration.
                    # ----------------------------------------------------------
                    parset = patch_parset(parset,
                        {
                            'Cimager.dataset': output
                        }
                    )
                else:
                    self.logger.debug("No time range selected")

                self.logger.debug("Running cimager")
                with CatchLog4CXX(
                    working_dir,
                    self.logger.name + "." + os.path.basename(vds)
                ):
                    cimager_process = Popen(
                        [imager_exec, "-inputs", parset],
                        stdout=PIPE, stderr=PIPE, cwd=working_dir
                    )
                    sout, serr = cimager_process.communicate()
                log_process_output("cimager", sout, serr, self.logger)
                if cimager_process.returncode != 0:
                    raise CalledProcessError(
                        cimager_process.returncode, imager_exec
                    )

                #        Dump the resulting images in the pipeline results area.
                #    I'm not aware of a foolproof way to predict the image names
                #                that will be produced, so we read them from the
                #                      parset and add standard cimager prefixes.
                # --------------------------------------------------------------
                parset_data = Parset(parset)
                image_names = parset_data.getStringVector("Cimager.Images.Names")
                prefixes = [
                    "image", "psf", "residual", "weights", "sensitivity"
                ]
                self.logger.debug("Copying images to %s" % resultsdir)
                for image_name in image_names:
                    for prefix in prefixes:
                        filename = image_name.replace("image", prefix, 1)
                        shutil.move(
                            os.path.join(working_dir, filename),
                            os.path.join(resultsdir, filename)
                        )
                    if parset_data.getBool('Cimager.restore'):
                        shutil.move(
                            os.path.join(working_dir, image_name + ".restored"),
                            os.path.join(resultsdir, image_name + ".restored")
                        )
            except CalledProcessError, e:
                self.logger.error(str(e))
                return 1
            finally:
                shutil.rmtree(working_dir)
                if query:
                    #                     If we created a new parset, delete it.
                    # ----------------------------------------------------------
                    os.unlink(parset)
            return 0

if __name__ == "__main__":
    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(cimager_trap(jobid, jobhost, jobport).run_with_stored_arguments())
