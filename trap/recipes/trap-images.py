#!/usr/bin/python

"""
This main recipe accepts a list of images (through images_to_process.py).
Images should be prepared with the correct keywords.
"""

from __future__ import with_statement

import sys
import datetime
import json

from lofarpipe.support.control import control
from lofarpipe.support.utilities import log_time
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
        'monitor_coords': ingredient.StringField(
            '-m', '--monitor-coords',
            # Unfortunately the ingredient system cannot handle spaces in
            # parameter fields. I have tried enclosing with quotes, switching
            # to StringField, still no good.
            help='Specify a list of RA,DEC co-ordinate pairs to monitor\n'
            '(decimal degrees, no spaces), e.g.:\n'
            '--monitor-coords=[[137.01,14.02],[137.05,15.01]]',
            optional=True
        ),
      'monitor_list': ingredient.FileField(
            '-l', '--monitor-list',
            help='Specify a file containing a list of RA,DEC' 
                    'co-ordinates to monitor, e.g.\n'
            '--monitor-list=my_coords.txt\n'
            'File should contain a list of RA,DEC pairs (each in list form), e.g.\n'
            '[ [137.01,14.02], [137.05,15.01]] \n'
            ,
            optional=True
        ),
    }

    def pipeline_logic(self):
        from images_to_process import images

        log_time(self.logger)
        if not images:
            self.logger.warn("No images found, check parameter files.")
            return 1

        self.logger.info("creating dataset in database ...")
        self.outputs.update(self.run_task(
            "persistence",
            images,
            description=self.inputs['job_name'], dataset_id=self.inputs['dataset_id']
        ))

        dataset = DataSet(id=self.outputs['dataset_id'], database=DataBase())
        dataset.update_images()

        self.outputs.update(self.run_task(
            "quality_check",
            [i.id for i in dataset.images],
        ))

        self.outputs.update(self.run_task(
            "source_extraction",
            self.outputs['good_image_ids'],
            #nproc = self.config.get('DEFAULT', 'default_nproc')
            nproc=1 # Issue #3357
        ))

        self.outputs.update(self.run_task(
            "monitoringlist", [dataset.id],
            nproc=1 # Issue #3357
        ))

        self.outputs.update(self.run_task(
            "transient_search", [dataset.id],
            image_ids=self.outputs['good_image_ids']
        ))

        self.outputs.update(self.run_task(
            "feature_extraction",
            self.outputs['transients']
        ))

        self.outputs.update(self.run_task(
            "classification",
            self.outputs['transients']
        ))

        self.run_task("prettyprint", self.outputs['transients'])

        dataset.process_ts = datetime.datetime.utcnow()


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
        monitor_coords=[]
        if 'monitor_coords' in self.inputs:
            try:
                monitor_coords.extend(json.loads(self.inputs['monitor_coords']))
            except ValueError:
                self.logger.error("Could not parse monitor-coords from command line")
                sys.exit(1)
                
        if 'monitor_list' in self.inputs:
            try:
                mon_list = json.load(open(self.inputs['monitor_list']))
                monitor_coords.extend(mon_list)
            except ValueError:
                self.logger.error("Could not parse monitor-coords from file: "
                                  +self.inputs['monitor_list'])
                sys.exit(1)
                
        if len(monitor_coords):
            self.logger.info( "You specified monitoring at coords:")
            for i in monitor_coords:
                self.logger.info( "RA, %f ; Dec, %f " % (i[0],i[1]))
        for c in monitor_coords:
            dataset.add_manual_entry_to_monitoringlist(c[0],c[1])

if __name__ == '__main__':
    sys.exit(TrapImages().main())
