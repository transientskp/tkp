#!/usr/bin/python

import sys, os, time
from itertools import count
import tkp_lib.database as db
import tkp_lib.dataset as d
import tkp_lib.settings as s
import tkp_lib.dbregion as rg
from tkp_lib import image, accessors, containers


answer=str(raw_input('Did you load the LSM table (y/n)? '))

if answer != 'y':
    sys.exit('\n\tLoad LSM first by CALL LoadLSM(158,165,18,25,\'NVSS\',\'VLSS\',\'\');')

starttime = time.time()

basedir = '/home/scheers/maps/grb030329/pbcor/'
#basedir = '/scratch/bscheers/maps/grb030329/pbcor/'

imagesdir = basedir + 'fits/'

print "\nResults will be stored in", s.database_type, "dbname:", s.database_dbase

logtime = time.strftime("%Y%m%d-%H%M")
logfile = basedir + 'log/' + s.database_type + '_' + s.database_dbase + '_' + logtime + '.log'
log = open(logfile, 'w')

#description = 'GRBPBCOR WSRT nw assoc excl.2300_1207_1007'
description = 'GRBPBCOR WSRT assocs det10-anl4 excl71 fit'
#description = 'GRBPBCOR GMRT & WSRT det5-anl4'
dataset = d.DataSet(description)
print "Dataset Id:", dataset.id

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
#files.sort()
for file in files:
    #if (
        #file == 'GRB030329_WSRT_20031225_1400.fits' 
        #file == 'GRB030329_WSRT_330_20040125.fits' 
        #or file == 'GRB030329_WSRT_330_20040502.fits' 
        #or file == 'GRB030329_WSRT_330_20050326.fits' 
        #or file == 'GRB030329_WSRT_20040129_1400.fits' 
        #or file == 'GRB030329_WSRT_20040327_1400.fits'
        #or file == 'GRB030329_WSRT_20040401_1400.fits'
        #or file == 'GRB030329_WSRT_20040519_1400.fits'
        #or file == 'GRB030329_WSRT_20041111_1400.fits'
        #or file == 'GRB030329_WSRT_20050409_1400.fits'
        #or file == 'GRB030329_WSRT_200512COMBI_1400.fits'
        #):
    if (file.startswith('GRBPBCOR_WSRT_') ):
    #if (file.startswith('GRB030329_WSRT_')):
        print "\ni: ", i, ", file: ", file
        imgstarttime = time.time()
        my_fitsfile = accessors.FitsFile(imagesdir + file)
        my_image = image.ImageData(my_fitsfile, dataset = dataset)
        print "im.obstime:",my_image.obstime
        imid = my_image.id[0]
        print "Image Id:", imid
        results = my_image.sextract(det=10,anl=4)
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

log.close()
conn.close()

print "Total processing time for dataset: %.3f seconds" % (elapsed)
print "\nLog file: ", logfile

