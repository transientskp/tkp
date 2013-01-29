import trap.ingredients as ingred
from trap.ingredients.common import TrapNode, node_run
import trap.recipes

class user_detections(TrapNode):
    def trapstep(self, image_id, image_path, image_nd):
        self.outputs['ff_ud'] = ingred.source_extraction.forced_fits(image_path, image_nd)
        self.outputs['image_id'] = image_id

node_run(__name__, user_detections)

