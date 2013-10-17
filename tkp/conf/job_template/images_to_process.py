###################################################################################
#      List the images for processing by the transient detection pipeline         #
###################################################################################

# This should provide a module-scope iterable named "images" which provides a
# full path to each image to be processed. For example:

images = [
    "/path/to/image1",
    "/path/to/image2",
    ...
]

# Optionally, whatever standard tools are required may be used to generate the
# list:
#
#  import os
#  import glob
#  images = sorted(
#      glob.glob(
#          os.path.expanduser("/home/example/data/*.fits")
#      )
#  )

#Just for show:
print "******** IMAGES: ********"
for f in images:
    print f
print "*************************"
