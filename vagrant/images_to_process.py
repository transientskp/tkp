path = "/vagrant/vagrant/data/*"

import os
import glob
images = sorted( glob.glob( os.path.expanduser(path)))
images = [i for i in images if not i.endswith('README')]

print "******** IMAGES: ********"
for f in images:
    print f
print "*************************"
