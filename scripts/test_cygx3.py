#!/usr/bin/python

import os
import time
#import MonetSQLdb as mydb
import tkp_lib.database as db
import tkp_lib.dataset as d

starttime = time.clock()

cygx3dir = '/home/bscheers/cygx3_images/'
imagesdir = cygx3dir

starttime = time.clock()

conn = db.connection()

seq_nr = 0
dbtime = 0
for file in os.listdir(imagesdir):
  #if (file == 'WN30218H' or file == 'WN30224H'):
    seq_nr += 1

    print "File: ", file
    imagesfile = imagesdir + file
    print "Image file: ", imagesfile

    interstarttime = time.clock()
    fitsfile = d.FitsFile(imagesfile)
    image = d.ImageData(fitsfile, seq_nr = seq_nr)
    results = image.sextract(method='python')
    interendtime = time.clock()
    print "Image processing time %.3f seconds" % (interendtime - interstarttime)
    results.savetoDB(conn)
    interenddbtime = time.clock()
    dbtime = dbtime + (interenddbtime - interendtime)
    print "DB insertion time %.3f seconds" % (interenddbtime - interendtime)

endtime = time.clock()

print "Total DB processing time %.3f seconds" % (dbtime)
print "Total processing time %.3f seconds" % (endtime - starttime)

