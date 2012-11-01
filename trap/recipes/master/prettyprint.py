import trap.prettyprint
from lofarpipe.support.baserecipe import BaseRecipe

class prettyprint(BaseRecipe):
    inputs = {}
    outputs = {}

    def go(self):
        super(prettyprint, self).go()
        transients = self.inputs['args']
        trap.prettyprint.prettyprint(transients)

if __name__ == '__main__':
    import sys
    sys.exit(prettyprint().main())
