from tkp.distribute.cuisine.common import TrapNode, node_run
import tkp.steps.persistence


class persistence(TrapNode):
    def trapstep(self, image,  parset_file):
        self.outputs['metadatas'] = tkp.steps.persistence.node_steps([image], parset_file)

node_run(__name__, persistence)
