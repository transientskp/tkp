from __future__ import with_statement
import sys
import itertools
import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from tkp.database import DataBase, quality
from tkp.database.utils import general as dbgen
import trap.ingredients as ingred


class image_detections(BaseRecipe, RemoteCommandRecipeMixIn):
    """Store an image and its detections into the database"""

    #inputs = {
    #    'parset': ingredient.FileField(
    #        '-p', '--parset',
    #        dest='parset',
    #        help="persistence configuration parset"
    #    ),
    #}
    outputs = {
        'image_id': ingredient.IntField()
    }

    def go(self):
        super(image_detections, self).go()
        im_dets = self.inputs['args'][0]
        dataset_id = self.inputs['args'][1]
        image_qualified = im_dets['image_qualified']
        image = image_qualified['image']
        good_image = image_qualified['good_image']
        xtrsrcs = im_dets['extractedsources']

        # Maybe do it simple and straightforward...
        # First get freqband
        #   if it doesn't exist, create it
        # Then store image
        image_id = ingred.persistence.store_image(image, dataset_id)
        if not good_image:
            reason = image_qualified['reason']
            comment = image_qualified['comment']
            quality.reject(image_id, reason, comment)
        else:
            # Add blindly extracted sources
            dbgen.insert_extracted_sources(image_id, xtrsrcs, 'blind')

        self.outputs['image_id'] = image_id

        if self.error.isSet():
            self.logger.warn("Failed image_detections process detected")
            return 1
        else:
            return 0

if __name__ == '__main__':
    sys.exit(image_detections().main())
