import trap.ingredients as ingred
import trap.recipes

class monitoringlist(trap.recipes.TrapNode):
    def trapstep(self, image_id):
        #self.outputs['image_id'] = trap.ingredients.monitoringlist.update_monitoringlist(image_id)
        self.outputs['forced_fits'] = ingred.monitoringlist.forced_fits(null_detections, image)

trap.recipes.node_run(__name__, monitoringlist)
