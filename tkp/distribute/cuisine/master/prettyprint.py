from lofarpipe.support.baserecipe import BaseRecipe

import tkp.steps.prettyprint


class prettyprint(BaseRecipe):
    inputs = {}
    outputs = {}

    def go(self):
        super(prettyprint, self).go()
        transients = self.inputs['args']
        tkp.steps.prettyprint.prettyprint(transients)

if __name__ == '__main__':
    import sys
    sys.exit(prettyprint().main())
