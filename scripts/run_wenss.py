#!/usr/bin/python

import os
import time
import tkp_lib.database as db
import tkp_lib.dataset as d
import tkp_lib.settings as s

starttime = time.time()

basedir = '/home/bscheers/maps/wenss/'
#basedir = '/home/bscheers/genimages/random_sources3/'
#basedir = '/home/bscheers/selected_genimages/'
#basedir = '/home/bscheers/maps/cygx3_images/'
#basedir = '/home/bscheers/maps/cygx3_few_images/'
#basedir = '/home/bscheers/maps/gcrt/'
#basedir = '/home/bscheers/maps/gcrt_few/'

imagesdir = basedir + 'fits/'

logtime = time.strftime("%Y-%m-%d-%H:%M:%S")
logfile = basedir + 'log/proctimes' + logtime + '.log'
log = open(logfile, 'w')

files = os.listdir(imagesdir)
files.sort()
images = []
for file in files:
    #if (file == 'WP85324H' or file == 'WP90000H'):
    #    print "File: ", file, " for later testing, not now"
    #else:
    #    images.append(imagesdir + file)
    if (file[0:4] == 'WN55'):
        images.append(imagesdir + file)
        descr = 'Proc. WENSS maps decl = ' + file[2:4] + ', MySQL at det=7'

dataset = d.DataSet(descr, images)
print dataset

#s.database_type = "MonetDB"
#s.database_host = "acamar.science.uva.nl"



conn = db.connection()
print conn

i = 0
for img in dataset:
    imgstarttime = time.time()
    img.wcs.coordsys  = 'fk4' 
    img.wcs.outputsys = 'fk5'
    results = img.sextract(det=7)
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
    row = str(i) + ';' + str(subtotelapsed) + ';' + str(dbelapsed) + ';' + str(imgelapsed) + '\n'
    log.write(row)
    img.clearcache()
    i = i + 1

endtime = time.time()
elapsed = endtime - starttime

log.close()
conn.close()

print "Total processing time %.3f seconds" % (elapsed)

