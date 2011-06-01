#!/usr/bin/python

import os
import time
#import MySQLdb as mydb
#import MonetSQLdb as mydb
import tkp_lib.database as db
import tkp_lib.dataset as d

starttime = time.clock()

basedir = '/home/bscheers/maps/wenss/'
#basedir = '/home/bscheers/genimages/random_sources3/'
#basedir = '/home/bscheers/selected_genimages/'
#basedir = '/home/bscheers/maps/cygx3_images/'


imagesdir = basedir + 'fits/'

logfile = basedir + 'log/proctimes2.log'
log = open(logfile, 'w')

files = os.listdir(imagesdir)
files.sort()

starttime = time.time()

conn = db.connection()
print conn

seq_nr = 0
for file in files:
  #if (file == 'WN30143H' or file == 'WN30218H' or file == 'WN30224H'):
  #if (file == 'WN30218H' or file == 'WN30224H'):
  if (file == 'WN55074H'):
  #if (file == 'WN30224H'):
  #if (file == 'random_sources0916.fits'):
    seq_nr += 1

    print "File: ", file
    imagefile = imagesdir + file
    print "Image File: ", imagefile

    imgstarttime = time.time()
    fitsfile = d.FitsFile(imagefile)
    image = d.ImageData(fitsfile, seq_nr = seq_nr)
    image.wcs.coordsys  = 'fk4' 
    image.wcs.outputsys = 'fk5'
    results = image.extract(sigma=4.5, method='python')
    #results = image.extract(method='python')
    imgendtime = time.time()
    imgelapsed = imgendtime - imgstarttime
    print "Image processing time %6.3f seconds" % (imgelapsed)
    dbstarttime = time.time()
    results.savetoDB(conn)
    dbendtime = time.time()
    dbelapsed = dbendtime - dbstarttime
    print "DB insertion time %6.3f seconds" % (dbelapsed)
    subtotelapsed = dbelapsed + imgelapsed
    print "Subtotal proc time %6.3f seconds" % (subtotelapsed)
    row = str(seq_nr) + ';' + str(subtotelapsed) + ';' + str(dbelapsed) + ';' + str(imgelapsed) + '\n'
    log.write(row)

endtime = time.time()
elapsed = endtime - starttime

log.close()
conn.close()

print "Total processing time %.3f seconds" % (elapsed)

