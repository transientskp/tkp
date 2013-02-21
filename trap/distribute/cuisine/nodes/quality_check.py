from trap.distribute.cuisine.common import TrapNode, node_run
import trap.ingredients.quality
import trap.distribute.cuisine

class quality_check(TrapNode):
    def trapstep(self, image_id, image_path, parset_file):
            self.outputs['rejected'] = trap.ingredients.quality.reject_check(image_path, parset_file)
            self.outputs['image_id'] = image_id

node_run(__name__, quality_check)
