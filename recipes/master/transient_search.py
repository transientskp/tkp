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

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support import lofaringredient
from lofar.parameterset import parameterset

from tkp.config import config
import tkp.database.database
import tkp.database.dataset
import tkp.database.utils as dbu



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
        'image_ids': lofaringredient.ListField(
            '--image-ids',
            default=[],
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
        dataset_id = self.inputs['args'][0]
        self.database = tkp.database.database.DataBase()
        self.dataset = tkp.database.dataset.DataSet(
            id=dataset_id, database=self.database)
        eta_lim = parset.getFloat(
            'probability.eta_lim', config['transient_search']['eta_lim'])
        V_lim= parset.getFloat(
            'probability.V_lim', config['transient_search']['V_lim'])
        prob_threshold = parset.getFloat(
                                'probability.threshold',
                                config['transient_search']['probability'])
        minpoints = parset.getInt('probability.minpoints',
                                  config['transient_search']['minpoints'])
        
        transient_ids, siglevels, transients = dbu.transient_search(
                    conn = self.database.connection, 
                     dataset = self.dataset, 
                     eta_lim = eta_lim, 
                     V_lim = V_lim,
                     probability_threshold = prob_threshold, 
                     minpoints = minpoints,
                     image_ids=self.inputs['image_ids'],
                     logger=None)

        self.outputs['transient_ids'] = map(int, transient_ids)
        self.outputs['siglevels'] = siglevels
        self.outputs['transients'] = transients
        
        return 0


if __name__ == '__main__':
    sys.exit(transient_search().main())
