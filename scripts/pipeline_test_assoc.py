#!/usr/bin/python

import os, time
from itertools import count
import tkp_lib.database as db
import tkp_lib.dataset as d
import tkp_lib.settings as s
#import tkp_lib.dbplots as dbplots
from tkp_lib import image, accessors, containers

starttime = time.time()

basedir = '/home/bscheers/maps/wenss/'
imagesdir = basedir + 'fits/'

print "\nResults will be stored in", s.database_type, "dbname:", s.database_dbase

logtime = time.strftime("%Y-%m-%d-%H:%M:%S")
logfile = basedir + 'log/' + s.database_type + '_' + s.database_dbase + '_' + logtime + '.log'
log = open(logfile, 'w')

print "\nLogs stored in file: ", logfile

description = 'Testing Source Association; WENSS det=var'
dataset = d.DataSet(description)
print "Dataset Id:", dataset.id
#dataset = d.DataSet(description, images)


#"""
log.write('dataset ' + description + '\n')
row = 'image; ' + 'nsources; ' + 'imgelapsed; ' + 'dbelapsed; ' + 'subtotal; \n'
log.write(row)
row = '------------------------------------------------------ \n'
log.write(row)

conn = db.connection()
#print conn

i = 0
files = os.listdir(imagesdir)
files.sort()
for file in files:
    if (file == 'WN30218H'):
    #if (file == 'WN30218H' or file == 'WN30224H' or file == 'WN30230H'):
        for j in range(1):
            #print "\ntimes i: ", i, ", file: ", file
            print "\ntimes j: ", j, ", file: ", file
            #dataset.append(imagesdir + file)
            imgstarttime = time.time()
            my_fitsfile = accessors.FitsFile(imagesdir + file)
            my_image = image.ImageData(my_fitsfile, dataset = dataset)
            imid = my_image.id[0]
            print "Image Id:", imid
            my_image.wcs.coordsys  = 'fk4' 
            my_image.wcs.outputsys = 'fk5'
            if (j == 0 or j == 3):
                results = my_image.sextract(det=110)
            else:
                results = my_image.sextract(det=100)
            imgendtime = time.time()
            nsources = len(results)
            imgelapsed = imgendtime - imgstarttime
            print "Image processing time %6.3f seconds" % (imgelapsed)
            dbstarttime = time.time()
            results.savetoDB(conn)
            #results.associnDB(my_image.id[0], conn)
            dbendtime = time.time()
            dbelapsed = dbendtime - dbstarttime
            print "DB insertion time %6.3f seconds" % (dbelapsed)
            subtotelapsed = dbelapsed + imgelapsed
            print "Subtotal proc time for this image: %6.3f seconds" % (subtotelapsed)
            row = str(imid) + ';' + str(nsources) + ';' + str(imgelapsed) + ';' + str(dbelapsed) + ';' + str(subtotelapsed) + '\n'
            log.write(row)
            my_image.clearcache()
        i = i + 1

endtime = time.time()
elapsed = endtime - starttime

#my_plot=dbplots.plotHistAssocCatDist(dataset.id, conn)

log.close()
conn.close()

print "Total processing time for dataset: %.3f seconds" % (elapsed)
#"""


