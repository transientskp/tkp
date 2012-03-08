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

from scipy.stats import chisqprob
import numpy

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support import lofaringredient
from lofar.parameterset import parameterset

from tkp.config import config
import tkp.database.database
import tkp.database.dataset
import tkp.database.utils as dbu
from tkp.classification.transient import Transient
from tkp.classification.transient import Position
from tkp.classification.transient import DateTime


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
        'parset': lofaringredient.FileField(
            '-p', '--parset',
            dest='parset',
            help="Transient search configuration parset"
        ),
#        'detection_level': lofaringredient.FloatField(
#            '--detection-level',
#            help='Detection level (level * sigma > mu)',
#            default=3.0
#        ),
#        'closeness_level': lofaringredient.FloatField(
#            '--closeness-level',
#            help=('Closeness level for associated sources '
#                  '(ignore associations with level > closeness level)'),
#            default=3.0
#        ),
        'dataset_id': lofaringredient.IntField(
            '--dataset-id',
            help='Dataset ID (as stored in the database)'
        ),
        'image_ids': lofaringredient.ListField(
            '--image-ids',
            default=None,
            help='List of current images'
        ),
        }
    
    outputs = {
        'transient_ids': IntList(),
        'siglevels': FloatList(),
        'transients': lofaringredient.ListField(),
        }

    def go(self):
        # parset default values:
        super(transient_search, self).go()
        self.logger.info("Finding transient sources in the database")
        parset = parameterset(self.inputs['parset'])
        dataset_id = self.inputs['dataset_id']
        self.database = tkp.database.database.DataBase()
        self.dataset = tkp.database.dataset.DataSet(
            id=dataset_id, database=self.database)
        limits = {'eta': parset.getFloat(
            'probability.eta_lim', config['transient_search']['eta_lim']),
                  'V': parset.getFloat(
            'probability.V_lim', config['transient_search']['V_lim'])}
        results = self.dataset.detect_variables(
            eta_lim=limits['eta'], V_lim=limits['V'])
        transients = []
        if len(results) > 0:
            self.logger.info("Found %d variable sources", len(results))
            detection_threshold = parset.getFloat(
                'probability.threshold',
                config['transient_search']['probability'])
            # need (want) sorting by sigma
            # This is not pretty, but it works:
            tmpresults = dict((key,  [result[key] for result in results])
                           for key in ('srcid', 'npoints', 'v_nu', 'eta_nu'))
            srcids = numpy.array(tmpresults['srcid'])
            weightedpeaks, dof = (numpy.array(tmpresults['v_nu']),
                                  numpy.array(tmpresults['npoints'])-1)
            probability = 1 - chisqprob(tmpresults['eta_nu'] * dof, dof)
            selection = probability > detection_threshold
            transient_ids = numpy.array(srcids)[selection]
            selected_results = numpy.array(results)[selection]
            siglevels = probability[selection]
            minpoints = parset.getInt('probability.minpoints',
                                      config['transient_search']['minpoints'])
            for siglevel, result in zip(siglevels, selected_results):
                if result['npoints'] < minpoints:
                    continue
                position = Position(ra=result['ra'], dec=result['dec'],
                                    error=(result['ra_err'], result['dec_err']))
                transient = Transient(srcid=result['srcid'], position=position)
                transient.siglevel = siglevel
                transient.eta = result['eta_nu']
                transient.V = result['v_nu']
                transient.dataset = result['dataset']
                transient.monitored = dbu.is_monitored(
                    self.database.connection, transient.srcid)
                dbu.insert_transient(self.database.connection, transient,
                                     dataset_id, images=self.inputs['image_ids'])
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
