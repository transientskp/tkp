###################################################################################
#      List the datafiles for processing by the imaging pipeline                  #
###################################################################################

import glob
datafiles = sorted(glob.glob("/data2/lofar_test_data/sip_test_data/L44201/*"))

#If you want to run on a subset of the files, just slice the sorted list:
datafiles = datafiles[:4]

#Just for show:
print "***** DATAFILES: ********"
for f in datafiles:
    print f
print "*************************"
