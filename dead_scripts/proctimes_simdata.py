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
import pylab

starttime = time.time()

home = os.getenv('HOME')
basedir = home + '/simsa/posflux/'

mysqllogfile = basedir + 'tkplog/' + 'MySQL_pipeline_develop_20100207-2116.log'
monetdblogfile = basedir + 'tkplog/' + 'MonetDB_pipeline_develop_20100212-2335.log'
#monetdbimplogfile = basedir + 'tkplog/' + 'MonetDB_pipeline_sim_20100401-1534.log'
monetdbimplogfile = basedir + 'tkplog/' + 'MonetDB_pipeline_sim_20100402-1131.log'

log = open(mysqllogfile, 'r')
mysql_img = []
mysql_assoc = []
row = 0
for line in log:
    row += 1
    if row > 3 :
        rw = line.split(';')
        #print rw[0],rw[1],rw[4]
        if row == 4:
            min_img = int(rw[0]) - 1
        mysql_img.append(int(rw[0]) - min_img)
        mysql_assoc.append(rw[4])
log.close()

log = open(monetdblogfile, 'r')
monetdb_img = []
monetdb_assoc = []
row = 0
for line in log:
    row += 1
    if row > 3 :
        rw = line.split(';')
        #print rw[0],rw[1],rw[4]
        if row == 4:
            min_img = int(rw[0]) - 1
        monetdb_img.append(int(rw[0]) - min_img)
        monetdb_assoc.append(rw[4])
log.close()

log = open(monetdbimplogfile, 'r')
monetdbimp_img = []
monetdbimp_assoc = []
row = 0
for line in log:
    row += 1
    if row > 3 :
        rw = line.split(';')
        #print rw[0],rw[1],rw[4]
        if row == 4:
            min_img = int(rw[0]) - 1
        monetdbimp_img.append(int(rw[0]) - min_img)
        monetdbimp_assoc.append(rw[4])
log.close()

plotfiles=[]
p = 0
fig = pylab.figure()
ax1 = fig.add_subplot(111)
ax1.set_xlabel('image')
ax1.set_ylabel('time [s]')

ax1.loglog(mysql_img, mysql_assoc, 'r-', label='MySQL')
ax1.loglog(monetdb_img, monetdb_assoc, 'b-', label='MonetDB fast')
ax1.loglog(monetdbimp_img, monetdbimp_assoc, 'g-', label='MonetDB faster')
pylab.legend(numpoints=1,loc='upper left')
ax1.grid(True)

plotfiles.append('DB_proctimes_simdata.eps')
pylab.savefig(plotfiles[p],dpi=600)

print plotfiles


"""
row = 'image_id; ' + \
      'nsources; ' + \
      'imgelapsed; ' + \
      'dbinsert; ' + \
      'dbassocxtr; ' + \
      'dbassoccat; ' + \
      'dbelapsed; ' + \
      'subtotal; \n'
"""



