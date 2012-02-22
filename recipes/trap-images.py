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

from tkp.database.database import DataBase
from tkp.database.dataset import DataSet


class SIP(control):
    def pipeline_logic(self):
        from images_to_process import images

        # Create the dataset
        database = DataBase()
        dataset = DataSet(data={'dsinname': self.inputs['job_name']},
                          database=database)
        self.logger.info("dataset id = %d", dataset.id)
        with log_time(self.logger):
             for image in images:
                 self.logger.info("Processing image %s", str(image))
                 outputs = self.run_task("source_extraction",
                                         images=[image],
                                         dataset_id=dataset.id)
                 outputs.update(
                     self.run_task("monitoringlist",
                                   image_ids=outputs['image_ids'],
                                   dataset_id=dataset.id))
                 outputs.update(
                     self.run_task("transient_search", [],
                                   dataset_id=dataset.id))
                 outputs.update(
                     self.run_task("feature_extraction", [],
                                   transients=outputs['transients']))
                 
                 # run the manual classification on the transient objects
                 outputs.update(
                     self.run_task("classification", [],
                                   transients=outputs['transients']))
                 
                 self.run_task("prettyprint", [], transients=outputs['transients'])

        dataset.process_ts = datetime.datetime.utcnow()
        database.close()


if __name__ == '__main__':
    sys.exit(SIP().main())
