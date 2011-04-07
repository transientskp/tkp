#!/usr/bin/python

import os, time
from itertools import count
import tkp_lib.database as db
import tkp_lib.dataset as dataset
import tkp_lib.settings as s
from tkp_lib import image, accessors, containers

starttime = time.time()

basedir = '/home/bscheers/maps/wenss/'
imagesdir = basedir + 'fits/'

logtime = time.strftime("%Y-%m-%d-%H:%M:%S")
logfile = basedir + 'log/proctimes' + logtime + '.log'
log = open(logfile, 'w')
print "logfile: ", logfile

my_images = (imagesdir + "WN30143H",
    imagesdir + "WN30218H",
    imagesdir + "WN30224H"
)

print "nr of images = ", len(my_images)

my_dataset = dataset.DataSet("my dataset", my_images)

#description = 'Testing pipeline_develop database; WENSS det=10'
#dataset = d.DataSet(description)
#dataset = d.DataSet(description, images)

arr = []
for nr, im in zip(count(), my_dataset):
    print "nr = ", nr, "; dsname = ", my_dataset.name, "; my_dataset._id = ", my_dataset._id, "; im._id[0] = ", im._id[0]
    arr.append([my_dataset._id, im._id[0]])
    print "(nr, im.id - arr[0][1]) = (", nr, im._id[0]-arr[0][1], ")"

print "arr = ", arr
print "first im id = ", arr[0][1]

"""
log.write(description + '\n')
row = 'image; ' + 'nsources; ' + 'imgelapsed; ' + 'dbelapsed; ' + 'subtotal; \n'
log.write(row)
w = '------------------------------------------------------ \n'
log.write(row)
#print "dataset id: ", dataset.id

conn = db.connection()
#print conn

i = 0
files = os.listdir(imagesdir)
files.sort()
for file in files:
    if (file == 'WN30143H' or file == 'WN30218H' or file == 'WN30224H'):
    #if (file == 'WN30143H'):
        print "i: ", i, ", file: ", file
        #dataset.append(imagesdir + file)
        imgstarttime = time.time()
        my_fitsfile = accessors.FitsFile(imagesdir + file)
        my_image = image.ImageData(my_fitsfile, dataset = dataset)
        my_image.wcs.coordsys  = 'fk4' 
        my_image.wcs.outputsys = 'fk5'
        results = my_image.sextract(det=10)
        imgendtime = time.time()
        nsources = len(results)
        imgelapsed = imgendtime - imgstarttime
        print "Image processing time %6.3f seconds" % (imgelapsed)
        dbstarttime = time.time()
        results.savetoDB(conn)
        dbendtime = time.time()
        dbelapsed = dbendtime - dbstarttime
        print "DB insertion time %6.3f seconds" % (dbelapsed)
        subtotelapsed = dbelapsed + imgelapsed
        print "Subtotal proc time for this image: %6.3f seconds" % (subtotelapsed)
        row = str(i) + ';' + str(nsources) + ';' + str(imgelapsed) + ';' + str(dbelapsed) + ';' + str(subtotelapsed) + '\n'
        log.write(row)
        my_image.clearcache()
        i = i + 1

endtime = time.time()
elapsed = endtime - starttime

log.close()
conn.close()

print "Total processing time for dataset: %.3f seconds" % (elapsed)
"""


