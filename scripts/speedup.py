#!/usr/bin/python

import os, time
import sys
from itertools import count
import tkp_lib.database as db
import tkp_lib.dataset as d
import tkp_lib.settings as s
import tkp_lib.dbregion as rg
import tkp_lib.dbdiagnostics as diagn
from tkp_lib import image, accessors, containers

starttime = time.time()

n_of_maps = sys.argv[1]
repos = os.getenv("REPOS")
basedir = repos + '/pipe/database/simdata/'
imagesdir = basedir + 'maps' + n_of_maps + '/'

print "\nResults will be stored in", s.database_type, "dbname:", s.database_dbase

logtime = time.strftime("%Y%m%d-%H%M")
logfile = basedir + 'tkplog/' + s.database_type + '_' + s.database_dbase + '_' + logtime + '.log'
log = open(logfile, 'w')

#description = 'Simulated data of n_of_maps = ' + n_of_maps
description = 'test det.serialize()'
dataset = d.DataSet(description)
dsid = dataset.id
print "Dataset Id:", dsid

log.write('dataset ' + description + '\n')
row = 'image_id; ' + \
      'nsources; ' + \
      'imgelapsed; ' + \
      'dbinsert; ' + \
      'dbassocxtr; ' + \
      'dbassoccat; ' + \
      'dbelapsed; ' + \
      'subtotal; \n'
log.write(row)
row = '------------------------------------------------------ \n'
log.write(row)

conn = db.connection()

i = 0
files = os.listdir(imagesdir)
files.sort()
for file in files:
    if (file.startswith('SOURCESINSERTED1.')):
        print "\ni: ", i, ", file: ", file
        imgstarttime = time.time()
        my_fitsfile = accessors.FitsFile(imagesdir + file)
        my_image = image.ImageData(my_fitsfile, dataset = dataset)
        print "im.obstime:",my_image.obstime
        imid = my_image.id[0]
        print "Image Id:", imid
        #results = my_image.sextract(det=10,anl=6)
        results = my_image.sextract(det=90,anl=6)
        #print "results:",results
        imgendtime = time.time()
        nsources = len(results)
        imgelapsed = imgendtime - imgstarttime
        print "Image processing time %6.3f seconds" % (imgelapsed)
        dbstarttime = time.time()
        
        results.savetoDB(conn)
        dbinter1time = time.time()
        dbinsert = dbinter1time - dbstarttime
        #results.associnDB(my_image.id[0], conn)
        
        results.assocXSrc2XSrc(my_image.id[0], conn)
        dbinter2time = time.time()
        dbassocxtr = dbinter2time - dbinter1time
        
        results.assocXSrc2Cat(my_image.id[0], conn)
        dbinter3time = time.time()
        dbassoccat = dbinter3time - dbinter2time
        dbelapsed = dbinter3time - dbstarttime
        print "DB INSERT time: %6.3f seconds" % (dbinsert)
        print "DB Assoc2Xtr time: %6.3f seconds" % (dbassocxtr)
        print "DB Assoc2Cat time: %6.3f seconds" % (dbassoccat)
        print "DB total time: %6.3f seconds" % (dbelapsed)
        subtotelapsed = dbelapsed + imgelapsed
        print "Subtotal proc time for this image: %6.3f seconds" % (subtotelapsed)
        row = str(imid) + ';' + \
              str(nsources) + ';' + \
              str(imgelapsed) + ';' + \
              str(dbinsert) + ';' + \
              str(dbassocxtr) + ';' + \
              str(dbassoccat) + ';' + \
              str(dbelapsed) + ';' + \
              str(subtotelapsed) + '\n'
        log.write(row)
        my_image.clearcache()
        i = i + 1

endtime = time.time()
elapsed = endtime - starttime

"""
print "#---- Diagnostics ----"
files = diagn.plotSourcesPerImage(dsid,conn)
print files

files = diagn.histNumberOfAssociations(dsid,conn)
print files

files = diagn.scatterSigmaOverMuX2X(dsid,conn)
print files

files = diagn.plotLightCurveMaxSigmaOverMu(dsid,conn)
print files
#---------------------
"""

log.close()
conn.close()

print "Total processing time for dataset: %.3f seconds" % (elapsed)
print "\nLog file: ", logfile


