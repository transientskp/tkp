from __future__ import with_statement
import sys
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.clusterdesc import ClusterDesc, get_compute_nodes
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
import tkp.config
import trap.persistence

class persistence(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Store an image into the database
    """

    inputs = {
        'dataset_id': ingredient.IntField(
            '--dataset-id',
            help='Specify a previous dataset id to append the results to.',
            default=-1
        ),
        'description': ingredient.StringField(
            '--description',
            help="Description of the dataset",
            default="TRAP pipeline dataset"
        ),
        'store_images': ingredient.BoolField(
            '--store-images',
            help="Store images in MongoDB database",
            default=False
        ),
        'mongo_host': ingredient.StringField(
            '--mongo-host',
            help="MongoDB hostname",
            default="pc-swinbank.science.uva.nl"
        ),
        'mongo_port': ingredient.IntField(
            '--mongo-port',
            help="MongoDB port number",
            default=27017
        ),
        'mongo_db': ingredient.StringField(
            '--mongo-db',
            help="MongoDB database",
            default="tkp"
        )
    }
    outputs = {
        'dataset_id': ingredient.IntField()
    }

    def go(self):
        super(persistence, self).go()
        images = self.inputs['args']
        self.outputs['dataset_id'] = trap.persistence.store(images, self.inputs['description'], self.inputs['dataset_id'])
        return 0

if __name__ == '__main__':
    sys.exit(persistence().main())
