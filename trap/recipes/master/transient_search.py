from __future__ import with_statement
from __future__ import division
import sys
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support import lofaringredient
from lofarpipe.support.utilities import log_time
import trap.ingredients as ingred

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
        super(transient_search, self).go()
        with log_time(self.logger):
            ingred.transient_search.logger = self.logger
            self.outputs.update(ingred.transient_search.search_transients(
                                          image_ids=self.inputs['image_ids'],
                                          dataset_id=self.inputs['args'][0],
                                          parset=self.inputs['parset']))
        return 0


if __name__ == '__main__':
    sys.exit(transient_search().main())
