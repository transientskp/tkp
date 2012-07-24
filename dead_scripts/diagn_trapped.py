#!/usr/bin/python

import sys, os, time
from itertools import count
import logging
import tkp.database.dbregion as reg

import monetdb.sql as db
from monetdb.sql import Error as Error

db_type = "MonetDB"
db_host = "ldb001"
db_port = 50000
db_dbase = "trapd"
db_user = "trap"
db_passwd = "bang"

conn = db.connect(hostname=db_host,database=db_dbase,username=db_user,password=db_passwd)

outpath = '/home/scheers/maps/lofar/regions/'
imageid=[13]
for i in range(len(imageid)):
    reg.createRegionByImage(imageid[i], conn, outpath, 'blue')


"""
outputdir = '.'
xtrsrcids=[22046,22053]
for i in range(len(xtrsrcids)):
    files = plt.plotLightCurveSecByXSource(xtrsrcids[i],conn)
    print files
    files = plt.plotAssocCloudByXSource(xtrsrcids[i],conn,outputdir)
    print files

outputdir = '.'
xtrsrcids=[8474,8506]
for i in range(len(xtrsrcids)):
    files = plt.plotLightCurveSecByXSource(xtrsrcids[i],conn)
    print files
    files = plt.plotAssocCloudByXSource(xtrsrcids[i],conn,outputdir)
    print files
"""

