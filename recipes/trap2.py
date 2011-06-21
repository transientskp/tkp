#!/usr/bin/python

from __future__ import with_statement

import sys
import os
from contextlib import closing
from operator import itemgetter

from pyrap.quanta import quantity

from lofarpipe.support.control import control
from lofarpipe.support.utilities import log_time
from lofarpipe.support.parset import patched_parset
import tkp.database.database as tkpdb


SECONDS_IN_DAY = 86400.


class SIP(control):
    def pipeline_logic(self):
        # Read the datafiles; datafiles is a list of MS paths.
        from to_process2 import datafiles
        
        with log_time(self.logger):
            #storage_mapfile = self.run_task("datamapper_storage", datafiles)['mapfile'] # generate a mapfile mapping them to compute nodes
            #self.logger.info('storage mapfile = %s' % storage_mapfile)
            #
            ## Produce a GVDS file describing the data on the storage nodes.
            #self.run_task('vdsmaker', storage_mapfile)
            #
            ## Read metadata (start, end times, pointing direction) from GVDS.
            #vdsinfo = self.run_task("vdsreader")
            #
            ## NDPPP reads the data from the storage nodes, according to the
            ## map. It returns a new map, describing the location of data on
            ## the compute nodes.
            #ndppp_results = self.run_task(
            #    "ndppp",
            #    storage_mapfile,
            #)            
            #compute_mapfile = ndppp_results['mapfile']
            #
            #ra = quantity(vdsinfo['pointing']['ra']).get_value('deg')
            #dec = quantity(vdsinfo['pointing']['dec']).get_value('deg')
            #central = self.run_task(
            #    "skymodel", ra=ra, dec=dec, search_size=2.5
            #    )
            #
            ## Patch the name of the central source into the BBS parset for
            ## subtraction.
            #with patched_parset(
            #    self.task_definitions.get("bbs", "parset"),
            #    {
            #    'Step.correct.Model.Sources': '[ "%s" ]' % (central["source_name"]),
            #    'Step.solve1.Model.Sources': '[ "%s" ]' % (central["source_name"]),
            #    'Step.solve2.Model.Sources': '[ "%s" ]' % (central["source_name"]),
            #    'Step.subtract.Model.Sources': '[ "%s" ]' % (central["source_name"])
            #    }
            #    ) as bbs_parset:
            #    self.logger.info("bbs patched parset = %s" % bbs_parset)
            #    # BBS modifies data in place, so the map produced by NDPPP
            #    # remains valid.
            #    self.run_task("bbs", compute_mapfile, parset=bbs_parset)
            #
            ## rerun DPPP on calibrated data
            #ndppp_results = self.run_task(
            #    "ndppp2",
            #    compute_mapfile,
            #)            
            #compute_mapfile = ndppp_results['mapfile']
            compute_mapfile = self.run_task("datamapper_storage", datafiles)['mapfile'] # generate a mapfile mapping them to compute nodes
            self.logger.info("compute mapfile = %s" % compute_mapfile)
            # Produce a GVDS file describing the data on the storage nodes.
            gvds_file = self.run_task('vdsmaker', compute_mapfile)['gvds']
            self.logger.info("GVDS file = %s" % gvds_file)
            
            dataset_id = None
            outputs = self.run_task("time_slicing", gvds_file=gvds_file)
            mapfiles = outputs['mapfiles']
            subdirs = ["%d" % int(starttime) for starttime, endtime in
                       outputs['timesteps']]
            for iteration, (mapfile, subdir) in enumerate(zip(mapfiles,
                                                            subdirs)):
                self.logger.info("Starting time slice iteration #%d" %
                                 (iteration+1,))
                outputs = {}
                results_dir = os.path.join(
                    self.config.get('DEFAULT', 'default_working_directory'),
                    self.inputs['job_name'],
                    subdir
                    )
                outputs = self.run_task('cimager_trap', mapfile,
                                        vds_dir=os.path.dirname(mapfile),
                                        results_dir=results_dir)

                outputs.update(
                    self.run_task('img2fits', images=outputs['images'],
                        results_dir=os.path.join(
                            self.config.get('layout', 'results_directory'),
                            subdir))
                    )

                outputs.update(
                    self.run_task("source_extraction",
                                  images=outputs['combined_fitsfile'],
                                  dataset_id=dataset_id)
                    )
                if dataset_id is None:
                    dataset_id = outputs['dataset_id']
                dblogin = dict([(key, self.config.get('database', key))
                                for key in ('dbname', 'user', 'password',
                                            'hostname')])
                #database = tkpdb.DataBase(**dblogin)
                with closing(tkpdb.DataBase(**dblogin)) as database:
                    outputs.update(
                        self.run_task("transient_search", [],
                                      dataset_id=dataset_id,
                                      database=database)
                        )

                    outputs.update(
                        self.run_task("feature_extraction", [],
                                      transients=outputs['transients'],
                                      # transient_ids=outputs['transient_ids'],
                                      dblogin=dblogin,  # for the compute nodes
                                      database=database)
                        )

                    # run the manual classification on the transient objects
                    outputs.update(
                        self.run_task("classification", [],
                                      transients=outputs['transients'],
                                      database=database)
                        )

                self.logger.info("outputs = %s " % str(outputs))
                self.run_task("prettyprint", [], transients=outputs['transients'])


if __name__ == '__main__':
    sys.exit(SIP().main())
