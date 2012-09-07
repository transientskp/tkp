###################################################################################
#      List the images for processing by the transient detection pipeline         #
###################################################################################
import os
import glob
datafiles = sorted( glob.glob(os.path.expanduser("~/test/ami/120422/images/*.fits")) )

#Just for show:
print "***** datafiles: ********"
for f in datafiles:
    print f
print "*************************"
