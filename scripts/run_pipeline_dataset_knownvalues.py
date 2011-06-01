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

knownValues = (('centrera', 350.85),
    ('centredec', 58.815),
    ('centrerapix', 1025.0),
    ('centredecpix', 1025.0),
    ('raincr', -0.052083333333329998),
    ('decincr', 0.052083333333329998),
    ('xdim', 2048),
    ('ydim', 2048),
    ('pixmax', 0.499993652105),
    ('pixmin', -0.0278977472335),
)


my_filename = imagesdir + "WN30143H"
my_dataset = dataset.DataSet("my dataset")
my_fitsfile = accessors.FitsFile(my_filename)
my_image = image.ImageData(my_fitsfile, dataset = my_dataset)

for attr, value in knownValues:
    print "attr = ", attr, "; value = ", value
    #result = getattr(self.my_im, attr)
    #self.assertAlmostEqual(result, value)



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
        results = my_image.extract(det=10)
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


