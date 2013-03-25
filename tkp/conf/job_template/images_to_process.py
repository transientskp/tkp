###################################################################################
#      List the images for processing by the transient detection pipeline         #
###################################################################################
import os
import glob
images = sorted( glob.glob(os.path.expanduser("/home/gijs/Data/small_multifreq/*.fits")) )

#Just for show:
print "***** IMAGES: ********"
for f in images:
    print f
print "*************************"
