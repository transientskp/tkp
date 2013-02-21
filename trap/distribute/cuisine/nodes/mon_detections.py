from trap.distribute.cuisine.common import TrapNode, node_run
import trap.ingredients as ingred

class mon_detections(TrapNode):
    def trapstep(self, image_id, image_path, image_nd):
        self.outputs['ff_mon'] = ingred.source_extraction.forced_fits(image_path, image_nd)
        self.outputs['image_id'] = image_id

node_run(__name__, mon_detections)

