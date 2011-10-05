from __future__ import with_statement
from __future__ import division


__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010, University of Amsterdam'
__version__ = '0.1'
__last_modification__ = '2010-08-24'



import sys
import os

import monetdb.sql.connections
from scipy.stats import chisqprob
import numpy

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support import lofaringredient

import tkp.database.database
import tkp.database.dataset
from tkp.classification.manual.transient import Transient
from tkp.classification.manual.utils import Position
from tkp.classification.manual.utils import DateTime


SQL = dict(
    position="""\
SELECT
     ra, decl, ra_err, decl_err
FROM
    extractedsources x1
WHERE
    x1.xtrsrcid = %s
""",
    dataset="""\
SELECT
    ds.dsinname
FROM
    extractedsources x, images im, datasets ds
WHERE
    x.xtrsrcid = %s
  AND x.image_id = im.imageid
  AND im.ds_id = ds.dsid
""",
    siglevel="""\
SELECT
   xtrsrc_id
  ,datapoints
  ,sqrt(datapoints*(avg_I_peak_sq - avg_I_peak*avg_I_peak)/(datapoints-1)) /avg_I_peak as V
  ,(datapoints/(datapoints-1)) * (avg_weighted_I_peak_sq - avg_weighted_I_peak*avg_weighted_I_peak/avg_weight_peak) as eta
FROM runningcatalog
WHERE
    ds_id = %s
  AND
    datapoints > 1
ORDER BY eta DESC
""",
    insert="""\
INSERT INTO transients
  (xtrsrc_id, status)
  SELECT
    b.xtrsrc_id, 1
  FROM
    runningcatalog b
  WHERE
    b.xtrsrc_id = %s
   AND
    b.xtrsrc_id NOT IN
    (
      SELECT
        xtrsrc_id
      FROM
        transients
    )
""",
    update="""\
UPDATE 
    transients
SET
    siglevel = %s
WHERE
    xtrsrc_id = %s
"""
)


class IntList(lofaringredient.ListField):
    """Input that defines a list of ints"""
    def is_valid(self, value):
        if (super(IntList, self).is_valid(value) and
            all(map(lambda v: isinstance(v, int), value))):
            return True
        return False


class FloatList(lofaringredient.ListField):
    """Input that specifies a list of floats"""
    def is_valid(self, value):
        if (super(FloatList, self).is_valid(value) and
            all(map(lambda v: isinstance(v, float), value))):
            return True
        return False


class transient_search(BaseRecipe):
    """
    Search for transients in the database, for a specific dataset
    """
    
    inputs = {
        'detection_level': lofaringredient.FloatField(
            '--detection-level',
            help='Detection level (level * sigma > mu)',
            default=3.0
        ),
        'closeness_level': lofaringredient.FloatField(
            '--closeness-level',
            help=('Closeness level for associated sources '
                  '(ignore associations with level > closeness level)'),
            default=3.0
        ),
        'dataset_id': lofaringredient.IntField(
            '--dataset-id',
            help='Dataset ID (as stored in the database)'
        )
        }
    
    outputs = {
        'transient_ids': IntList(),
        'siglevels': FloatList(),
        'transients': lofaringredient.ListField(),
        }

    def create_transient(self, srcid, siglevel):
        """Construct a very basic transient object"""

        self.database.cursor.execute(SQL['position'], (srcid,))
        results = self.database.cursor.fetchall()
        results = map(float, results[0])
        # calculate an average error for now
        error = numpy.sqrt(results[2]*results[2] + results[3]*results[3])
        transient = Transient(srcid=srcid, position=Position(
            ra=results[0], dec=results[1], error=(results[2], results[3])))
        transient.siglevel = siglevel
        self.database.cursor.execute(SQL['dataset'], (srcid,))
        transient.dataset = self.database.cursor.fetchone()[0]
        return transient

    def go(self):
        super(transient_search, self).go()
        self.logger.info("Selecting transient sources from the database")
        try:
            detection_level = float(self.inputs['detection_level'])
        except KeyError:
            detection_level = DETECTION_LEVEL
        try:
            closeness_level = float(self.inputs['closeness_level'])
        except KeyError:
            closeness_level = CLOSENESS_LEVEL
        dataset_id = self.inputs['dataset_id']
        self.database = tkp.database.database.DataBase()
        self.dataset = tkp.database.dataset.DataSet(
            id=dataset_id, database=self.database)
        results = self.dataset.detect_variables()
        transients = []
        if len(results) > 0:
            # need (want) sorting by sigma
            # This is not pretty, but it works:
            results = dict((key,  [result[key] for result in results])
                           for key in ('srcid', 'npoints', 'v_nu', 'eta_nu'))
            srcids = numpy.array(results['srcid'])
            weightedpeaks, N = numpy.array(results['v_nu']), numpy.array(results['npoints'])-1
            siglevel = chisqprob(results['eta_nu'] * N, N)
            selection = siglevel < 1/detection_level
            transient_ids = numpy.array(srcids)[selection]
            siglevels = siglevel[selection]
            for transient_id, siglevel in zip(transient_ids, siglevels):
                transient = self.create_transient(int(transient_id),
                                                  float(siglevel))
                #self.database.cursor.execute(SQL['insert'], (transient.srcid,))
                #self.database.commit()
                #self.database.cursor.execute(SQL['update'], (
                #    transient.srcid, transient.siglevel))
                #self.database.commit()
                transients.append(transient)
        else:
            transient_ids = numpy.array([], dtype=numpy.int)
            siglevels = numpy.array([], dtype=numpy.float)
        self.outputs['transient_ids'] = map(int, transient_ids)
        self.outputs['siglevels'] = siglevels
        self.outputs['transients'] = transients
        return 0


if __name__ == '__main__':
    sys.exit(transient_search().main())
