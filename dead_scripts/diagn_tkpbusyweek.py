#!/usr/bin/python

import tkp_lib.database as db
import tkp_lib.dbdiagnostics as diagn
import tkp_lib.dbplots as plt
import tkp_lib.dbregion as reg

conn = db.connection()

catid = 3 # NVSS
dsid = 1

files = diagn.plotLightCurveMaxVar_v1(dsid,conn)
print files

files = diagn.plotLightCurveLevelVar_v1(conn, dsid, level=0.1)
print files

files = diagn.scatterVar_v1_v2_X2X(dsid,conn)
print files

files = diagn.contourX2XDistLRRho(conn,dsid)
print files

outpath = '/home/bscheers/simsa/posflux/regions100/'
imageid=[1487,1490]
for i in range(len(imageid)):
    file = reg.createRegionByImage(imageid[i],conn,outpath, 'red')
    print file

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

