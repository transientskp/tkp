#                                                         LOFAR IMAGING PIPELINE
#
#                                                BBS (BlackBoard Selfcal) recipe
#                                                         John Swinbank, 2009-10
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

from __future__ import with_statement
from contextlib import closing
import psycopg2, psycopg2.extensions
import subprocess
import sys
import os
import threading
import tempfile
import shutil
import time
import signal

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.clusterlogger import clusterlogger
from lofarpipe.support.group_data import gvds_iterator
from lofarpipe.support.pipelinelogging import CatchLog4CPlus
from lofarpipe.support.pipelinelogging import log_process_output
from lofarpipe.support.remotecommand import run_remote_command
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.jobserver import job_server
from lofarpipe.support.lofaringredient import LOFARoutput, LOFARinput
import lofarpipe.support.utilities as utilities
import lofarpipe.support.lofaringredient as ingredient

class bbs(BaseRecipe):
    """
    The bbs recipe coordinates running BBS on a group of MeasurementSets. It
    runs both GlobalControl and KernelControl; as yet, SolverControl has not
    been integrated.

    The recipe will also run the sourcedb and parmdb recipes on each of the
    input MeasuementSets.

    **Arguments**

    A mapfile describing the data to be processed.
    """
    inputs = {
        'control_exec': ingredient.ExecField(
            '--control-exec',
            dest="control_exec",
            help="BBS Control executable"
        ),
        'kernel_exec': ingredient.ExecField(
            '--kernel-exec',
            dest="kernel_exec",
            help="BBS Kernel executable"
        ),
        'initscript': ingredient.FileField(
            '--initscript',
            dest="initscript",
            help="Initscript to source (ie, lofarinit.sh)"
        ),
        'parset': ingredient.FileField(
            '-p', '--parset',
            dest="parset",
            help="BBS configuration parset"
        ),
        'key': ingredient.StringField(
            '--key',
            dest="key",
            help="Key to identify BBS session"
        ),
        'db_host': ingredient.StringField(
            '--db-host',
            dest="db_host",
            help="Database host with optional port"
        ),
        'db_user': ingredient.StringField(
            '--db-user',
            dest="db_user",
            help="Database user"
        ),
        'db_name': ingredient.StringField(
            '--db-name',
            dest="db_name",
            help="Database name"
        ),
        'makevds': ingredient.ExecField(
            '--makevds',
            help="makevds executable"
        ),
        'combinevds': ingredient.ExecField(
            '--combinevds',
            help="combinevds executable"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
        'makesourcedb': ingredient.ExecField(
            '--makesourcedb',
            help="makesourcedb executable"
        ),
        'parmdbm': ingredient.ExecField(
            '--parmdbm',
            help="parmdbm executable"
        ),
        'skymodel': ingredient.FileField(
            '-s', '--skymodel',
            dest="skymodel",
            help="Input sky catalogue"
        )
    }

    def go(self):
        self.logger.info("Starting BBS run")
        super(bbs, self).go()

        #             Generate source and parameter databases for all input data
        # ----------------------------------------------------------------------
        inputs = LOFARinput(self.inputs)
        inputs['args'] = self.inputs['args']
        inputs['executable'] = self.inputs['parmdbm']
        outputs = LOFARoutput(self.inputs)
        if self.cook_recipe('parmdb', inputs, outputs):
            self.logger.warn("parmdb reports failure")
            return 1
        inputs['args'] = self.inputs['args']
        inputs['executable'] = self.inputs['makesourcedb']
        inputs['skymodel'] = self.inputs['skymodel']
        outputs = LOFARoutput(self.inputs)
        if self.cook_recipe('sourcedb', inputs, outputs):
            self.logger.warn("sourcedb reports failure")
            return 1

        #              Build a GVDS file describing all the data to be processed
        # ----------------------------------------------------------------------
        self.logger.debug("Building VDS file describing all data for BBS")
        vds_file = os.path.join(
            self.config.get("layout", "job_directory"),
            "vds",
            "bbs.gvds"
        )
        inputs = LOFARinput(self.inputs)
        inputs['args'] = self.inputs['args']
        inputs['gvds'] = vds_file
        inputs['unlink'] = False
        inputs['makevds'] = self.inputs['makevds']
        inputs['combinevds'] = self.inputs['combinevds']
        inputs['nproc'] = self.inputs['nproc']
        inputs['directory'] = os.path.dirname(vds_file)
        outputs = LOFARoutput(self.inputs)
        if self.cook_recipe('vdsmaker', inputs, outputs):
            self.logger.warn("vdsmaker reports failure")
            return 1
        self.logger.debug("BBS GVDS is %s" % (vds_file,))


        #      Iterate over groups of subbands divided up for convenient cluster
        #          procesing -- ie, no more than nproc subbands per compute node
        # ----------------------------------------------------------------------
        for to_process in gvds_iterator(vds_file, int(self.inputs["nproc"])):
            #               to_process is a list of (host, filename, vds) tuples
            # ------------------------------------------------------------------
            hosts, ms_names, vds_files = map(list, zip(*to_process))

            #             The BBS session database should be cleared for our key
            # ------------------------------------------------------------------
            self.logger.debug(
                "Cleaning BBS database for key %s" % (self.inputs["key"])
            )
            with closing(
                psycopg2.connect(
                    host=self.inputs["db_host"],
                    user=self.inputs["db_user"],
                    database=self.inputs["db_name"]
                )
            ) as db_connection:
                db_connection.set_isolation_level(
                    psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
                )
                with closing(db_connection.cursor()) as db_cursor:
                    db_cursor.execute(
                        "DELETE FROM blackboard.session WHERE key=%s",
                        (self.inputs["key"],)
                    )

            #     BBS GlobalControl requires a GVDS file describing all the data
            #          to be processed. We assemble that from the separate parts
            #                                         already available on disk.
            # ------------------------------------------------------------------
            self.logger.debug("Building VDS file describing data for BBS run")
            vds_dir = tempfile.mkdtemp()
            vds_file = os.path.join(vds_dir, "bbs.gvds")
            combineproc = utilities.spawn_process(
                [
                    self.inputs['combinevds'],
                    vds_file,
                ] + vds_files,
                self.logger
            )
            sout, serr = combineproc.communicate()
            log_process_output(self.inputs['combinevds'], sout, serr, self.logger)
            if combineproc.returncode != 0:
                raise subprocess.CalledProcessError(
                    combineproc.returncode, command
                )

            #      Construct a parset for BBS GlobalControl by patching the GVDS
            #           file and database information into the supplied template
            # ------------------------------------------------------------------
            self.logger.debug("Building parset for BBS control")
            bbs_parset = utilities.patch_parset(
                self.inputs['parset'],
                {
                    'Observation': vds_file,
                    'BBDB.Key': self.inputs['key'],
                    'BBDB.Name': self.inputs['db_name'],
                    'BBDB.User': self.inputs['db_user'],
                    'BBDB.Host': self.inputs['db_host'],
    #                'BBDB.Port': self.inputs['db_name'],
                }
            )
            self.logger.debug("BBS control parset is %s" % (bbs_parset,))

            try:
                #        When one of our processes fails, we set the killswitch.
                #      Everything else will then come crashing down, rather than
                #                                         hanging about forever.
                # --------------------------------------------------------------
                self.killswitch = threading.Event()
                self.killswitch.clear()
                signal.signal(signal.SIGTERM, self.killswitch.set)

                #                           GlobalControl runs in its own thread
                # --------------------------------------------------------------
                run_flag = threading.Event()
                run_flag.clear()
                bbs_control = threading.Thread(
                    target=self._run_bbs_control,
                    args=(bbs_parset, run_flag)
                )
                bbs_control.start()
                run_flag.wait()    # Wait for control to start before proceeding

                #      We run BBS KernelControl on each compute node by directly
                #                             invoking the node script using SSH
                #      Note that we use a job_server to send out job details and
                #           collect logging information, so we define a bunch of
                #    ComputeJobs. However, we need more control than the generic
                #     ComputeJob.dispatch method supplies, so we'll control them
                #                                          with our own threads.
                # --------------------------------------------------------------
                command = "python %s" % (self.__file__.replace('master', 'nodes'))
                env = {
                    "LOFARROOT": utilities.read_initscript(self.logger, self.inputs['initscript'])["LOFARROOT"],
                    "PYTHONPATH": self.config.get('deploy', 'engine_ppath'),
                    "LD_LIBRARY_PATH": self.config.get('deploy', 'engine_lpath')
                }
                jobpool = {}
                bbs_kernels = []
                with job_server(self.logger, jobpool, self.error) as (jobhost, jobport):
                    self.logger.debug("Job server at %s:%d" % (jobhost, jobport))
                    for job_id, details in enumerate(to_process):
                        host, file, vds = details
                        jobpool[job_id] = ComputeJob(
                            host, command,
                            arguments=[
                                self.inputs['kernel_exec'],
                                self.inputs['initscript'],
                                file,
                                self.inputs['key'],
                                self.inputs['db_name'],
                                self.inputs['db_user'],
                                self.inputs['db_host']
                            ]
                        )
                        bbs_kernels.append(
                            threading.Thread(
                                target=self._run_bbs_kernel,
                                args=(host, command, env, job_id,
                                    jobhost, str(jobport)
                                )
                            )
                        )
                    self.logger.info("Starting %d threads" % len(bbs_kernels))
                    [thread.start() for thread in bbs_kernels]
                    self.logger.debug("Waiting for all kernels to complete")
                    [thread.join() for thread in bbs_kernels]


                #         When GlobalControl finishes, our work here is done
                # ----------------------------------------------------------
                self.logger.info("Waiting for GlobalControl thread")
                bbs_control.join()
            finally:
                os.unlink(bbs_parset)
                shutil.rmtree(vds_dir)
                if self.killswitch.isSet():
                    #  If killswitch is set, then one of our processes failed so
                    #                                   the whole run is invalid
                    # ----------------------------------------------------------
                    return 1

        return 0

    def _run_bbs_kernel(self, host, command, env, *arguments):
        """
        Run command with arguments on the specified host using ssh. Return its
        return code.

        The resultant process is monitored for failure; see
        _monitor_process() for details.
        """
        try:
            bbs_kernel_process = run_remote_command(
                self.config,
                self.logger,
                host,
                command,
                env,
                arguments=arguments
            )
        except Exception, e:
            self.logger.exception("BBS Kernel failed to start")
            self.killswitch.set()
            return 1
        result = self._monitor_process(bbs_kernel_process, "BBS Kernel on %s" % host)
        sout, serr = bbs_kernel_process.communicate()
        serr = serr.replace("Connection to %s closed.\r\n" % host, "")
        log_process_output("SSH session (BBS kernel)", sout, serr, self.logger)
        return result

    def _run_bbs_control(self, bbs_parset, run_flag):
        """
        Run BBS Global Control and wait for it to finish. Return its return
        code.
        """
        env = utilities.read_initscript(self.logger, self.inputs['initscript'])
        self.logger.info("Running BBS GlobalControl")
        working_dir = tempfile.mkdtemp()
        with CatchLog4CPlus(
            working_dir,
            self.logger.name + ".GlobalControl",
            os.path.basename(self.inputs['control_exec'])
        ):
            with utilities.log_time(self.logger):
                try:
                    bbs_control_process = utilities.spawn_process(
                        [
                            self.inputs['control_exec'],
                            bbs_parset,
                            "0"
                        ],
                        self.logger,
                        cwd=working_dir,
                        env=env
                    )
                    # _monitor_process() needs a convenient kill() method.
                    bbs_control_process.kill = lambda : os.kill(bbs_control_process.pid, signal.SIGKILL)
                except OSError, e:
                    self.logger.error("Failed to spawn BBS Control (%s)" % str(e))
                    self.killswitch.set()
                    return 1
                finally:
                    run_flag.set()

            returncode = self._monitor_process(
                bbs_control_process, "BBS Control"
            )
            sout, serr = bbs_control_process.communicate()
        shutil.rmtree(working_dir)
        log_process_output(
            self.inputs['control_exec'], sout, serr, self.logger
        )
        return returncode

    def _monitor_process(self, process, name="Monitored process"):
        """
        Monitor a process for successful exit. If it fails, set the kill
        switch, so everything else gets killed too. If the kill switch is set,
        then kill this process off.

        Name is an optional parameter used only for identification in logs.
        """
        while True:
            try:
                returncode = process.poll()
                if returncode == None:                   # Process still running
                    time.sleep(1)
                elif returncode != 0:                           # Process broke!
                    self.logger.warn(
                        "%s returned code %d; aborting run" % (name, returncode)
                    )
                    self.killswitch.set()
                    break
                else:                                   # Process exited cleanly
                    self.logger.info("%s clean shutdown" % (name))
                    break
                if self.killswitch.isSet():        # Other process failed; abort
                    self.logger.warn("Killing %s" % (name))
                    process.kill()
                    returncode = process.wait()
                    break
            except:
                # An exception here is likely a ctrl-c or similar. Whatever it
                # is, we bail out.
                self.killswitch.set()
        return returncode

if __name__ == '__main__':
    sys.exit(bbs().main())
