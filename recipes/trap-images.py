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

from lofarpipe.support.control import control
from lofarpipe.support.utilities import log_time
from lofarpipe.support.parset import patched_parset
import lofarpipe.support.lofaringredient as ingredient

from tkp.database.database import DataBase
from tkp.database.dataset import DataSet


class SIP(control):
    inputs = {
          'dataset_id': ingredient.IntField(
            '--dataset-id',
            help='Specify a previous dataset id to append the results to.',
            default=-1
            ),
      }
    
    def pipeline_logic(self):
        from images_to_process import images
        
        # Create the dataset
        database = DataBase()
        if self.inputs['dataset_id'] == -1:
            dataset = DataSet(data={'dsinname': self.inputs['job_name']},
                              database=database)
        else:
            dataset = DataSet(id = self.inputs['dataset_id'],
                              database=database)
            self.logger.info("Appending results to previous dataset")
            
        self.logger.info("dataset id = %d", dataset.id)
        with log_time(self.logger):
            for image in images:
                self.logger.info("Processing image %s", str(image))
                outputs = self.run_task("source_extraction", [image],
                                        dataset_id=dataset.id)
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
