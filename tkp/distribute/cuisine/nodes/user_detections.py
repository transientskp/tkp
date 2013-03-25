from tkp import steps
from tkp.distribute.cuisine.common import TrapNode, node_run


class user_detections(TrapNode):
    def trapstep(self, image_id, image_path, image_nd):
        self.outputs['ff_ud'] = steps.source_extraction.forced_fits(image_path, image_nd)
        self.outputs['image_id'] = image_id

node_run(__name__, user_detections)

