import trap.ingredients as ingred
from trap.ingredients.common import TrapNode, node_run
import trap.recipes

class monitoringlist(TrapNode):
    def trapstep(self, image_id):
        #self.outputs['image_id'] = trap.ingredients.monitoringlist.update_monitoringlist(image_id)
        self.outputs['forced_fits'] = ingred.monitoringlist.forced_fits(null_detections, image)

node_run(__name__, monitoringlist)
