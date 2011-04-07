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
basedir = home + '/tkp-code/pipe/database/pipeline_develop/MonetDB/scripts/simrsm/logs'

logfiles = []
#logfiles.append(basedir + '/insert.assoc.pc-swinbank.10.sources.per.image.10000.images.log')
#logfiles.append(basedir + '/insert.assoc.100.sources.per.image.10000.images.20100718-2309.log')
name = 'insert.assoc.ldb001.100.sources.per.image.1000.images.20100721-1228'
logfiles.append(basedir + '/' + name + '.log')
#logfiles.append(basedir + '/insert.assoc.10.sources.per.image.100000.images.log')

plotfiles=[]
p = 0
fig = pylab.figure()
ax1 = fig.add_subplot(111)
ax1.set_xlabel(r'image [100 sources/image]',size='large')
ax1.set_ylabel(r'$t$ [s]',size='large')

for i in range(len(logfiles)):
    log = open(logfiles[i], 'r')
    img = []
    insert = []
    addsource = []
    det = []
    row = 0
    for line in log:
        row += 1
        #if row > 5 and row < 3614:
        if row > 5:
            rw = line.split(',')
            #print rw[0],rw[1],rw[4]
            img.append(int(rw[0]))
            insert.append(float(rw[2]))
            addsource.append(float(rw[3]))
            det.append(float(rw[4]))
    log.close()

#ax1.loglog(img, insert, 'b-', label='' + str(i) + 'insert')
#ax1.loglog(img, assoc, 'r-', label='' + str(i) + 'assoc')
#ax1.plot(img, insert, 'b-', linewidth=2,label='insert')
#ax1.plot(img, assoc, 'r-', linewidth=2,label='assoc')
ax1.loglog(img, insert, 'b-', linewidth=2,label='insert')
ax1.loglog(img, addsource, 'g-', linewidth=2,label='addsrc')
ax1.loglog(img, det, 'r-', linewidth=2,label='det')

#ax1.loglog(monetdb_img, monetdb_assoc, 'b-', label='MonetDB fast')
#ax1.loglog(monetdbimp_img, monetdbimp_assoc, 'g-', label='MonetDB faster')
pylab.legend(numpoints=1,loc='upper left')
ax1.grid(True)

plotfiles.append(name + '.eps')
pylab.savefig(plotfiles[p],dpi=600)

print plotfiles
