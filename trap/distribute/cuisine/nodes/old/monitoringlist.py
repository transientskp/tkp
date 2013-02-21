from trap import steps
from trap.distribute.cuisine.common import TrapNode, node_run


class monitoringlist(TrapNode):
    def trapstep(self, image_id):
        #self.outputs['image_id'] = trap.ingredients.monitoringlist.update_monitoringlist(image_id)
        self.outputs['forced_fits'] = steps.monitoringlist.forced_fits(null_detections, image)

node_run(__name__, monitoringlist)
