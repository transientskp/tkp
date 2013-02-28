from tkp import steps
from tkp.distribute.cuisine.common import node_run, TrapNode


class null_detections(TrapNode):
    def trapstep(self, image_id, image_path, image_nd, parset_file):
        self.outputs['ff_nd'] = steps.source_extraction.forced_fits(image_path, image_nd, parset_file)
        self.outputs['image_id'] = image_id

node_run(__name__, null_detections)

