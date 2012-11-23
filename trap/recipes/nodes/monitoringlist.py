import trap.ingredients.monitoringlist
import trap.recipes

class monitoringlist(trap.recipes.TrapNode):
    def trapstep(self, image_id):
        self.outputs['image_id'] = trap.ingredients.monitoringlist.update_monitoringlist(image_id)

trap.recipes.node_run(__name__, monitoringlist)
