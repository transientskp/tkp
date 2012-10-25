
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
import lofarpipe.support.lofaringredient as ingredient

class quality_check(BaseRecipe, RemoteCommandRecipeMixIn):
    inputs = {
        'dataset_id': ingredient.IntField(
            '--dataset-id',
            help='Dataset to which images belong',
            default=None
        ),
    }
    outputs = {
        'image_ids': ingredient.ListField()
    }