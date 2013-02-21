#                                                         LOFAR IMAGING PIPELINE
#
#                        Generate a mapfile for processing data on storage nodes
#                                                            John Swinbank, 2010
#                                                      swinbank@transientskp.org
# ------------------------------------------------------------------------------

import os.path
from collections import defaultdict

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.parset import Parset
from lofarpipe.support.utilities import create_directory
import lofarpipe.support.lofaringredient as ingredient

class storagemapper(BaseRecipe):
    """
    Parses a list of filenames and generates a mapfile suitable for processing
    on storage nodes.

    **Arguments**

    None.
    """
    inputs = {
        'mapfile': ingredient.StringField(
            '--mapfile',
            help="Full path (including filename) of mapfile to produce (clobbered if exists)"
        )
    }

    outputs = {
        'mapfile': ingredient.FileField(
            help="Full path (including filename) of generated mapfile"
        )
    }

    def go(self):
        self.logger.info("Starting storagemapper run")
        super(storagemapper, self).go()

        #                          We read the storage node name out of the path
        #     and append the local filename (ie, on the storage node) to the map
        # ----------------------------------------------------------------------
        data = defaultdict(list)
        for filename in self.inputs['args']:
            host = filename.split(os.path.sep)[3]
            data[host].append(filename.split(host)[-1])

        #                                 Dump the generated mapping to a parset
        # ----------------------------------------------------------------------
        parset = Parset()
        for host, filenames in data.iteritems():
            parset.addStringVector(host, filenames)

        create_directory(os.path.dirname(self.inputs['mapfile']))
        parset.writeFile(self.inputs['mapfile'])
        self.outputs['mapfile'] = self.inputs['mapfile']

        return 0

if __name__ == '__main__':
    sys.exit(storagemapper().main())
