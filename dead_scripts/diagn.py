#!/usr/bin/python

import tkp_lib.database as db
import tkp_lib.dbdiagnostics as diagn
import tkp_lib.dbplots as plt
import tkp_lib.dbregion as reg

conn = db.connection()

catid = 3 # NVSS
dsid = 13

files = diagn.scatterSigmaOverMuX2X(dsid,conn)
print files

files = diagn.plotLightCurveMaxSigmaOverMu(dsid,conn)
print files

"""
files = plt.plotHistAssocXtrDist(dsid,conn)
print files

files = diagn.plotLightCurveLevelSigmaOverMu(conn, dsid, level=0.1)
print files

files = diagn.contourX2XDistLRRho(conn,dsid)
print files

files = diagn.histNumberOfAssociations(dsid,conn)
print files

files = diagn.plotSourcesPerImage(dsid,conn)
print files

files = diagn.contourX2CDistLRRho(conn, dsid, catid)
print files

"""

"""
outpath = '/home/bscheers/simsa/posflux/regions100/'
imageid=[1487,1490]
for i in range(len(imageid)):
    reg.createRegionByImage(imageid[i],conn,outpath, 'red')


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

