#!/usr/bin/python

"""
This main recipe accepts a list of images (through images_to_process.py).
Images should be prepared with the correct keywords.
"""

from __future__ import with_statement

import sys
import os
from contextlib import closing
from operator import itemgetter
from itertools import repeat

from pyrap.quanta import quantity

from lofarpipe.support.control import control
from lofarpipe.support.utilities import log_time
from lofarpipe.support.parset import patched_parset
import tkp.database.database as tkpdb

class SIP(control):
    def pipeline_logic(self):
        from images_to_process import images
        dataset_id = None
        with log_time(self.logger):
             for image in images:
                    outputs = self.run_task("source_extraction",
                                            images=[image],
                                            dataset_id=dataset_id)
                    if dataset_id is None:
                        dataset_id = outputs['dataset_id']
                    dblogin = dict([(key, self.config.get('database', key))
                                for key in ('name', 'user', 'password',
                                            'host')])

                    with closing(tkpdb.DataBase(**dblogin)) as database:
                        self.logger.info("%s", str(database))

                        outputs.update(
                            self.run_task("transient_search", [],
                                          dataset_id=dataset_id,
                                          database=database)
                            )
                    outputs.update(
                        self.run_task("feature_extraction", [],
                                      transients=outputs['transients'],
                                      dblogin=dblogin,  # for the compute nodes
                                      database=database)
                        )

                    # run the manual classification on the transient objects
                    outputs.update(
                        self.run_task("classification", [],
                                      transients=outputs['transients'],
                                      database=database)
                        )

                    self.run_task("prettyprint", [], transients=outputs['transients'])

if __name__ == '__main__':
    sys.exit(SIP().main())
