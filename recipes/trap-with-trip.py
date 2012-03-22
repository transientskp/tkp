#!/usr/bin/python

from __future__ import with_statement

import sys
import os
import datetime
from itertools import repeat

from pyrap.quanta import quantity

from lofarpipe.support.control import control
from lofarpipe.support.utilities import log_time
from lofarpipe.support.parset import patched_parset
from tkp.database.database import DataBase
from tkp.database.dataset import DataSet


SECONDS_IN_DAY = 86400.


class SIP(control):
    def pipeline_logic(self):
        # Read the datafiles; datafiles is a list of MS paths.
        from ms_to_process import datafiles
        
        with log_time(self.logger):
            storage_mapfile = self.run_task("datamapper_storage", datafiles)['mapfile'] # generate a mapfile mapping them to compute nodes
            self.logger.info('storage mapfile = %s' % storage_mapfile)
            
            # Produce a GVDS file describing the data on the storage nodes.
            gvds_file = self.run_task('vdsmaker', storage_mapfile)['gvds']
            
            # Read metadata (start, end times, pointing direction) from GVDS.
            vdsinfo = self.run_task("vdsreader")
            
            # NDPPP reads the data from the storage nodes, according to the
            # map. It returns a new map, describing the location of data on
            # the compute nodes.
            ndppp_results = self.run_task(
                "ndppp",
                storage_mapfile,
            )

            # Remove baselines which have been fully-flagged in any
            # individual subband.
            compute_mapfile = self.run_task(
                "flag_baseline",
                ndppp_results['mapfile'],
                baselines=ndppp_results['fullyflagged']
                )['mapfile']
                                    

            ra = quantity(vdsinfo['pointing']['ra']).get_value('deg')
            dec = quantity(vdsinfo['pointing']['dec']).get_value('deg')
            central = self.run_task(
                "skymodel", ra=ra, dec=dec, search_size=2.5
                )

            parmdb_mapfile = self.run_task("parmdb", compute_mapfile)['mapfile']
            sourcedb_mapfile = self.run_task("sourcedb", compute_mapfile)['mapfile']
#            
#            # Patch the name of the central source into the BBS parset for
#            # subtraction.
            with patched_parset(
                self.task_definitions.get("bbs", "parset"),
                {
                ## 'Step.correct.Model.Sources': '[ "%s" ]' % (central["source_name"]),
                ## 'Step.solve1.Model.Sources': '[ "%s" ]' % (central["source_name"]),
                ## 'Step.solve2.Model.Sources': '[ "%s" ]' % (central["source_name"]),
                ## 'Step.subtract.Model.Sources': '[ "%s" ]' % (central["source_name"])
                }
                ) as bbs_parset:
                self.logger.info("bbs patched parset = %s" % bbs_parset)
                # BBS modifies data in place, so the map produced by NDPPP
                # remains valid.
                bbs_mapfile = self.run_task(
                    "bbs", compute_mapfile,
                    parset=bbs_parset,
                    instrument_mapfile=parmdb_mapfile,
                    sky_mapfile=sourcedb_mapfile)['mapfile']

            # Now, run DPPP three times on the output of BBS. We'll run
            # this twice: once on CORRECTED_DATA, and once on
            # SUBTRACTED_DATA.
            with patched_parset(
                os.path.join(
                self.config.get("layout", "parset_directory"),
                "ndppp.postbbs.parset"
                ),
                {
                # "clip1.amplmax": str(5 * central["source_flux"])
                },
                output_dir=self.config.get("layout", "parset_directory")
                ) as corrected_ndppp_parset:
                for i in repeat(None, 2):
                    self.run_task(
                        "ndppp",
                        compute_mapfile,
                        parset=corrected_ndppp_parset,
                        suffix=""
                        )
            # Produce a GVDS file describing the data on the storage nodes.
            gvds_file = self.run_task('vdsmaker', compute_mapfile)['gvds']
            self.logger.info("GVDS file = %s" % gvds_file)
            
            # Create the dataset in the database
            database = DataBase()
            dataset = DataSet(data={'dsinname': self.inputs['job_name']},
                              database=database)
            dsid = dataset.id
            outputs = self.run_task("time_slicing", gvds_file=gvds_file)
            mapfiles = outputs['mapfiles']
            subdirs = ["%d" % int(starttime) for starttime, endtime in
                       outputs['timesteps']]
            self.logger.info("directories with sliced MSs = %s", str(subdirs))
            for iteration, (mapfile, subdir) in enumerate(zip(mapfiles,
                                                            subdirs)):
                self.logger.info("Starting time slice iteration #%d" %
                                 (iteration+1,))
                outputs = {}
                results_dir = os.path.join(
                    self.config.get('DEFAULT', 'working_directory'),
                    self.inputs['job_name'],
                    subdir
                    )
                outputs = self.run_task('awimager', mapfile)
            
                outputs.update(
                    self.run_task('img2fits', outputs['images'],
                                  results_dir=os.path.join(
                    self.config.get('layout', 'results_directory'),
                    subdir))
                    )
                
                outputs.update(self.run_task("source_extraction",
                                             [outputs['combined_fitsfile']],
                                             dataset_id=dataset.id))

                outputs.update(
                    self.run_task("monitoringlist", outputs['image_ids']))

                outputs.update(
                    self.run_task("transient_search", [dataset.id],
                                  image_ids=outputs['image_ids']))

                outputs.update(
                    self.run_task("feature_extraction", outputs['transients']))
                
                outputs.update(
                    self.run_task("classification", outputs['transients']))
                
                self.run_task("prettyprint", outputs['transients'])

            dataset.process_ts = datetime.datetime.utcnow()
            database.close()

            
if __name__ == '__main__':
    sys.exit(SIP().main())
