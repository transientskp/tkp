import trap.ingredients as ingred
from trap.ingredients.common import node_run, TrapNode


class null_detections(TrapNode):
    def trapstep(self, image_id, image_path, image_nd):
        self.outputs['ff_nd'] = ingred.source_extraction.forced_fits(image_path, image_nd)
        self.outputs['image_id'] = image_id

node_run(__name__, null_detections)

