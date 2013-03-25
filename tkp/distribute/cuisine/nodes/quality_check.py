from tkp.distribute.cuisine.common import TrapNode, node_run
import tkp.steps.quality


class quality_check(TrapNode):
    def trapstep(self, image_id, image_path, parset_file):
            self.outputs['rejected'] = tkp.steps.quality.reject_check(image_path, parset_file)
            self.outputs['image_id'] = image_id

node_run(__name__, quality_check)
