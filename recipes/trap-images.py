#!/usr/bin/python

"""
This main recipe accepts a list of images (through images_to_process.py).
Images should be prepared with the correct keywords.
"""

from __future__ import with_statement

import sys
import os
import datetime

from pyrap.quanta import quantity

import lofarpipe.support
from lofarpipe.support.control import control
from lofarpipe.support.utilities import log_time
from lofarpipe.support.parset import patched_parset
import lofarpipe.support.lofaringredient as ingredient

from tkp.database import DataBase
from tkp.database import DataSet

class TrapImages(control):
    inputs = {
        'dataset_id': ingredient.IntField(
            '--dataset-id',
            help='Specify a previous dataset id to append the results to.',
            default=-1
        ),
        'monitor_coords': ingredient.ListField(
            '-m', '--monitor-coords',
            # Unfortunately the ingredient system cannot handle spaces in
            # parameter fields. I have tried enclosing with quotes, switching
            # to StringField, still no good.
            help='Specify a list of RA,DEC co-ordinates to monitor\n'
            '(decimal degrees, no spaces), e.g.:\n'
            '--monitor-coords=[137.01,14.02,137.05,15.01]',
            default=[]
        ),
    }

    def pipeline_logic(self):
        from images_to_process import images

        database = DataBase()
        dataset = self.initialise_dataset(database)
        self.add_manual_monitoringlist_entries(dataset)

        with log_time(self.logger):
            if images:
                self.logger.info("Processing images ...")
                for ctr, image in enumerate(images):
                    outputs = self.run_task(
                        "source_extraction", [image], dataset_id=dataset.id,
#                       nproc = self.config.get('DEFAULT', 'default_nproc')
                        nproc=1 # Issue #3357
                    )
                    if ctr > 1: # monitoring list fails on first image
                        outputs.update(
                                self.run_task("monitoringlist", [dataset.id],
                                nproc=1 # Issue #3357
                            )
                        )
                    outputs.update(
                            self.run_task(
                                "transient_search", [dataset.id],
                                image_ids=outputs['image_ids']
                            )
                    )
                    outputs.update(
                        self.run_task("feature_extraction", outputs['transients'])
                    )
                    outputs.update(
                        self.run_task("classification", outputs['transients'])
                    )
#                   self.run_task("prettyprint", outputs['transients'])
            else:
                self.logger.warn("No images found, check parameter files.")
        dataset.process_ts = datetime.datetime.utcnow()
        database.close()

    def initialise_dataset(self, database):
        """Either inits a fresh dataset, or grabs the dataset specified
            at command line"""
        if self.inputs['dataset_id'] == -1:
            dataset = DataSet(
                data={'description': self.inputs['job_name']},
                database=database
            )
        else:
            dataset = DataSet(
                id = self.inputs['dataset_id'], database=database
            )
            self.logger.info("Appending results to previously entered dataset")
        self.logger.info("dataset id = %d", dataset.id)
        return dataset

    def add_manual_monitoringlist_entries(self, dataset):
        """Parses co-ords from self.inputs, loads them into the monitoringlist"""
        mon_coords = self.parse_monitoringlist_coords()
        for c in mon_coords:
            dataset.add_manual_entry_to_monitoringlist(c[0],c[1])

    def parse_monitoringlist_coords(self):
        """Returns a list of coord 2-tuples, format is: [(RA,DEC)] """
        if len(self.inputs['monitor_coords']):
            raw_monitor_list =  self.inputs['monitor_coords']

            if len(raw_monitor_list)%2 != 0:
                raise ValueError(
                    "Odd number of monitor co-ordinates supplied: "
                    "please supply RA,DEC pairs *with commas but no spaces*."
                )
            ra_list = raw_monitor_list[0::2]
            dec_list = raw_monitor_list[1::2]
            monitor_coords = zip(ra_list, dec_list)

            print "You specified monitoring at coords:"
            for i in monitor_coords:
                print "RA,", i[0]," ; Dec, " , i[1]
            return monitor_coords
        return []

if __name__ == '__main__':
    sys.exit(TrapImages().main())
