#!/usr/bin/python

import os
import time
import tkp_lib.database as db
import tkp_lib.dataset as d
import tkp_lib.settings as s

starttime = time.time()

basedir = '/home/bscheers/maps/cs1/'

imagesdir = basedir + 'fits/'

logtime = time.strftime("%Y-%m-%d-%H:%M:%S")
logfile = basedir + 'log/proctimes' + logtime + '.log'
log = open(logfile, 'w')

files = os.listdir(imagesdir)
files.sort()
images = []
for file in files:
    print "File: ", file
    images.append(imagesdir + file)
    descr = 'Proc. CS1 maps, MySQL at det=10'

dataset = d.DataSet(descr, images)
print dataset

#s.database_type = "MonetDB"
#s.database_host = "acamar.science.uva.nl"



conn = db.connection()
print conn

i = 0
for img in dataset:
    imgstarttime = time.time()
    results = img.extract(det=10)
    imgendtime = time.time()
    imgelapsed = imgendtime - imgstarttime
    print "Image: ", img.filename, " processing time %6.3f seconds" % (imgelapsed)
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

