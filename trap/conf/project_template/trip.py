"""
This is a cut-down pipeline definition for tutorial purposes.

'return 0' stops the script at any given line
"""
from __future__ import with_statement
from contextlib import closing
from itertools import repeat
import sys
import os

from pyrap.quanta import quantity

from lofarpipe.support.control import control
from lofarpipe.support.utilities import log_time
from lofarpipe.support.parset import patched_parset
from lofarpipe.support.lofaringredient import ListField

class sip(control):
    outputs = {
        'images': ListField()
    }

    def pipeline_logic(self):       
        sys.path.insert(0,"") 
        from datafiles_to_process import datafiles # datafiles is a list of MS paths.
        with log_time(self.logger):
            # Build a map of compute node <-> data location on storage nodes.
            storage_mapfile = self.run_task(
                "datamapper_storage", datafiles)['mapfile']
            self.logger.info('storage mapfile = %s' % storage_mapfile)

            # Produce a GVDS file describing the data on the storage nodes.
            self.run_task('vdsmaker', storage_mapfile)

            # Read metadata (start, end times, pointing direction) from GVDS.
            vdsinfo = self.run_task("vdsreader")

            # NDPPP reads the data from the storage nodes, according to the
            # map. It returns a new map, describing the location of data on
            # the compute nodes.
            ndppp_results = self.run_task("ndppp",
                                          storage_mapfile,
                                          )

            # Remove baselines which have been fully-flagged in any individual
            # subband.
            compute_mapfile = self.run_task(
                                            "flag_baseline",
                                            ndppp_results['mapfile'],
                                            baselines=ndppp_results['fullyflagged']
                                        )['mapfile']

            #compute_mapfile = ndppp_results['mapfile']
            #self.logger.info("compute map file = %s", compute_mapfile)
            parmdb_mapfile = self.run_task("parmdb", compute_mapfile)['mapfile']
            sourcedb_mapfile = self.run_task("sourcedb", compute_mapfile)['mapfile']

            with patched_parset(
                self.task_definitions.get("bbs", "parset"),
                {}
            ) as bbs_parset:
                # BBS modifies data in place, so the map produced by NDPPP
                # remains valid.
                self.run_task("bbs", 
                            compute_mapfile, 
                            parset=bbs_parset, 
                            instrument_mapfile=parmdb_mapfile, 
                            sky_mapfile=sourcedb_mapfile)['mapfile']

#	    return 0
            # Now, run DPPP three times on the output of BBS. We'll run
            # this twice: once on CORRECTED_DATA, and once on
            # SUBTRACTED_DATA. Clip anything at more than 5 times the flux of
            # the central source.
            with patched_parset(
                os.path.join(
                    self.config.get("layout", "parset_directory"),
                    "ndppp.1.postbbs.parset"
                ),
                {
 #                   "clip1.amplmax": str(5 * central["source_flux"])
                },
                output_dir=self.config.get("layout", "parset_directory")
            ) as corrected_ndppp_parset:
                for i in repeat(None, 3):
                    self.run_task(
                        "ndppp",
                        compute_mapfile,
                        parset=corrected_ndppp_parset,
                        suffix=""
                    )

# Image CORRECTED_DATA with casapy
#            print dir(compute_mapfile)
#            print compute_mapfile
#            return 0
            self.run_task("force_mount", compute_mapfile, mount_type="ALT-AZ")
            self.run_task("casapy_clean", compute_mapfile, arguments={
                      "niter": 500, "threshold": '0.0mJy', 
                      "imsize": [1024, 1024], 
                      "cell": ['40.0arcsec'], 
                      "weighting": 'briggs', 
                      "robust": 0.0, 
                      "psfmode": 'clark', 
                      "gridmode": 'widefield', 
                      "wprojplanes": 128, 
                      "calready": False, 
                      "restoringbeam": [] })

if __name__ == '__main__':
    sys.exit(sip().main())
