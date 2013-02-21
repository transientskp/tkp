#                                                         LOFAR IMAGING PIPELINE
#
#                                                          Demixing: node script
#                                                             Marcel Loose, 2011
#                                                                loose@astron.nl
# ------------------------------------------------------------------------------
from __future__ import with_statement
import os
import shutil
import sys
import logging
import tempfile
import numpy as numpy
import pyrap.tables as pt

from lofarpipe.support.lofarnode import LOFARnodeTCP
from lofarpipe.support.pipelinelogging import log_time
from lofarpipe.support.pipelinelogging import CatchLog4CPlus
from lofarpipe.support.utilities import read_initscript, catch_segfaults

# Add demix directory to sys.path before importing demix modules.
from trap.distribute.cuisine.nodes.old import shiftphasecenter as spc, demixing

sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), "demix"))
import smoothdemix as smdx
import subtract_from_averaged as sfa
from trap.distribute.cuisine.nodes.old.find_a_team import getAteamList

class demixing(LOFARnodeTCP):
    """
    Wrapper class to Bas vdTol's demixing scripts

    Problems/complaints: neal.jackson@manchester.ac.uk
    Further modified by R van Weeren, rvweeren@strw.leidenuniv.nl
    Further modified by G van Diepen, diepen@astron.nl

    Args:
        infile            MS to be demixed
        remove            list of stuff to remove eg ['CygA','CasA'];
                          if empty, use find_a_team.getAteamList()
        target            name of target  (default 'target')
        half_window = 20  integer window size of median filter,
                          20 is a good choice
        threshold = 2.5   solutions above/below threshold*rms are smoothed,
                          2.5 is a good choice

    *** NOTE: assumes that the MS to be demixed contains '_uv' in its name!!!
    *** NOTE: you need to "use LofIm" before starting
    *** NOTE: do not run two demixing sessions in the same directory in
              parallel!!
    """


    def _execute(self, cmd):
        try:
            temp_dir = tempfile.mkdtemp()
            with CatchLog4CPlus(temp_dir,
                                self.logger.name,
                                os.path.basename(cmd[0])
            ) as logger:
                catch_segfaults(cmd, temp_dir, self.environment, self.logger)
        except Exception, e:
            self.logger.error(str(e))
            return False
        finally:
            shutil.rmtree(temp_dir)
        return True


    def run(self, infile, working_dir, initscript, remove, target,
            clusterdesc, timestep, freqstep, half_window, threshold,
            demixdir, skymodel):

        with log_time(self.logger):
            if os.path.exists(infile):
                self.logger.info("Started processing %s" % infile)
            else:
                self.logger.error("Dataset %s does not exist" % infile)
                return 1

            self.logger.debug("infile = %s", infile)
            self.logger.debug("working_dir = %s", working_dir)
            self.logger.debug("initscript = %s", initscript)
            self.logger.debug("remove = %s", remove)
            self.logger.debug("target = %s", target)
            self.logger.debug("clusterdesc = %s", clusterdesc)
            self.logger.debug("timestep = %d", timestep)
            self.logger.debug("freqstep = %d", freqstep)
            self.logger.debug("half_window = %d", half_window)
            self.logger.debug("threshold = %f", threshold)
            self.logger.debug("demixdir = %s", demixdir)
            self.logger.debug("skymodel = %s", skymodel)

            # Initialise environment
            self.environment = read_initscript(self.logger, initscript)

            # Create working directory, if it does not yet exist.
            if not os.path.exists(working_dir):
                os.makedirs(working_dir)

            # The output file names are based on the input filename, however
            # they must be created in ``working_dir``.
            filename = os.path.split(infile)[1]
            outfile = os.path.join(working_dir, filename)
            key = os.path.join(working_dir, 'key_' + filename)
            mixingtable = os.path.join(working_dir, 'mixing_' + filename)
            basename = outfile.replace('_uv.MS', '') + '_'

            #  If needed, run NDPPP to preflag input file out to demix.MS
            t = pt.table(infile)
            shp = t.getcell("DATA", 0).shape
            t = 0
            mstarget = outfile.replace('uv',target)
            if os.system ('rm -f -r ' + mstarget) != 0:
                return 1
            if (shp[0] == 64  or  shp[0] == 128  or  shp[0] == 256):
                f=open(basename + 'NDPPP_dmx.parset','w')
                f.write('msin = %s\n' % infile)
                f.write('msin.autoweight = True\n')
                f.write('msin.startchan = nchan/32\n')
                f.write('msin.nchan = 30*nchan/32\n')
                f.write('msout = %s\n' % mstarget)
                f.write('steps=[preflag]\n')
                f.write('preflag.type=preflagger\n')
                f.write('preflag.corrtype=auto\n')
                f.close()
                self.logger.info("Starting NDPPP demix ...")
                if not self._execute(['NDPPP', basename + 'NDPPP_dmx.parset']):
                    return 1
            else:
                self.logger.info(
                    "Copying MS-file: %s --> %s" % (infile, mstarget)
                )
                if os.system ('cp -r ' + infile + ' ' + mstarget) != 0:
                    return 1

            # Use heuristics to get list of A-team sources if it wasn't given
            if not remove:
                self.logger.debug("Get list of A-team sources to remove")
                remove = getAteamList(
                             infile,
                             verbose=self.logger.isEnabledFor(logging.DEBUG))
                self.logger.debug("getAteamList returned: %s" % remove)

            self.logger.info("Removing target(s) %s from %s" %
                             (', '.join(remove), mstarget))
            spc.shiftphasecenter (mstarget, remove, freqstep, timestep)

            # for each source to remove, and the target, do a freq/timesquash
            # NDPPP
            removeplustarget = numpy.append (remove, target)
            avgoutnames = []

            for rem in removeplustarget:
                if os.system ('rm -f ' + basename + 'dmx_avg.parset') != 0:
                    return 1
                f=open(basename + 'dmx_avg.parset','w')
                msin = outfile.replace('uv',rem)
                f.write('msin = %s\n' % msin)
                msout = msin.replace ('.MS','_avg.MS')
                f.write('msout = %s\n' % msout)
                f.write('steps=[avg]\n')
                f.write('avg.type = averager\n')
                f.write('avg.timestep = %d\n' % timestep)
                f.write('avg.freqstep = %d\n' % freqstep)
                f.close()
                self.logger.debug("Squashing %s to %s" % (msin, msout))
                if os.system ('rm -f -r '+msout) != 0:
                    return 1

                if not self._execute(['NDPPP', basename + 'dmx_avg.parset']):
                    return 1

                # Form avg output names.
                msin = outfile.replace('uv',rem)
                msout = msin.replace ('.MS','_avg.MS')
                avgoutnames.append (msout)
                msdem = msin.replace ('.MS','_avg_dem.MS')
                if os.system ('rm -f -r '+msdem) != 0:
                    return 1

            self.logger.info("Starting the demixing algorithm")
            dmx.demixing (mstarget, mixingtable, avgoutnames,
                          freqstep, timestep, 4)
            self.logger.info("Finished the demixing algorithm")

            #
            #  run BBS on the demixed measurement sets
            #
            self.logger.info("Starting BBS run on demixed measurement sets")
            for i in remove:
                self.logger.info("Processing %s ..." % i)
                msin = outfile.replace('uv', i)
                msout = msin.replace ('.MS','_avg_dem.MS')

                vds_file = basename + i +'.vds'
                gds_file = basename + i +'.gds'

                self.logger.info("Creating vds & gds files...")
                if os.system ('rm -f '+ vds_file + gds_file) != 0:
                    return 1
                if not self._execute(['makevds', clusterdesc, msout, vds_file]):
                    return 1
                if not self._execute(['combinevds', gds_file, vds_file]):
                    return 1

                self.logger.info("Starting first calibration run")
                command=['calibrate',
                         '-f',
                         '--key', key,
                         '--cluster-desc', clusterdesc,
                         '--db', 'ldb001',
                         '--db-user', 'postgres',
                          gds_file,
                          os.path.join(demixdir, 'bbs_'+i+'.parset'),
                          skymodel,
                          working_dir]
                if not self._execute(command):
                    return 1

                self.logger.info("Generating smoothed instrument model")
                input_parmdb = os.path.join(msout, 'instrument')
                output_parmdb= os.path.join(msout, 'instrument_smoothed')
                # smoothparmdb indirectly creates a subprocess, so we must
                # make sure that the correct environment is set-up here.
                env = os.environ
                os.environ = self.environment
                smdx.smoothparmdb(input_parmdb, output_parmdb,
                                  half_window, threshold)
                os.environ = env

                self.logger.info("Starting second calibration run, "
                                 "using smoothed instrument model")
                command=['calibrate',
                         '--clean',
                         '--skip-sky-db',
                         '--skip-instrument-db',
                         '--instrument-name', 'instrument_smoothed',
                         '--key', key,
                         '--cluster-desc', clusterdesc,
                         '--db', 'ldb001',
                         '--db-user', 'postgres',
                         gds_file,
                         os.path.join(demixdir, 'bbs_'+i+'_smoothcal.parset'),
                         skymodel,
                         working_dir]
                if not self._execute(command):
                    return 1

            # Form the list of input files and subtract.
            self.logger.info("Subtracting removed sources from the data ...")
            demfiles = [outfile.replace('uv',rem+'_avg_dem') for rem in remove]
            sfa.subtract_from_averaged (mstarget.replace('.MS','_avg.MS'),
                                        mixingtable,
                                        demfiles,
                                        mstarget.replace('.MS','_sub.MS'))
        # We're done.
        return 0


    #   If invoked directly, parse command line arguments for logger information
    #                        and pass the rest to the run() method defined above
    # --------------------------------------------------------------------------
if __name__ == "__main__":
    jobid, jobhost, jobport = sys.argv[1:4]
    sys.exit(demixing(jobid, jobhost, jobport).run_with_stored_arguments())
