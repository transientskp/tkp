#!/usr/bin/python

import tkp_lib.database as db
import tkp_lib.dbplots as plt
import tkp_lib.dbregion as reg

conn = db.connection()

plt.plotHistSpIndices(conn)

"""
dirname = '/home/bscheers/maps/grb030329/regions/'
reg.createRegionByImage(10,conn,dirname,'yellow')
reg.createRegionByImage(11,conn,dirname,'red')

outputdir = '/home/bscheers/tkp-code/pipe/scripts/testing/'
plt.plotLightCurveByXSource(231, conn)
plt.plotAssocCloudByXSource(231, conn,outputdir)

xtrsrcid = [1,8,9,11,12,14,18,19,20,21,23,24,29,34,35,36,39,43,44,45,48,50,52,53]
print "len(xtrsrcid) = ",len(xtrsrcid)
for i in range(len(xtrsrcid)):
    print i, xtrsrcid[i]
    plt.plotLightCurveByXSource(xtrsrcid[i], conn)
    plt.plotAssocCloudByXSource(xtrsrcid[i], conn,outputdir)

plt.plotLightCurveByXSource(45, conn)
#dirname = '/home/bscheers/maps/grb030329/regions/'
#reg.createRegionByImage(2,conn,dirname,'green')
#this works:
plt.plotLightCurveByXSource(1, conn)
plt.plotLightCurveByXSource(2, conn)
plt.plotLightCurveByXSource(3, conn)
plt.plotLightCurveByXSource(4, conn)

plt.plotAssocCloudByXSource(1, conn)
plt.plotAssocCloudByXSource(2, conn)
plt.plotAssocCloudByXSource(3, conn)
plt.plotAssocCloudByXSource(4, conn)

reg.createRegionByImage(6,dirname,'red',conn)
reg.createRegionByImage(7,dirname,'blue',conn)
reg.createRegionByImage(8,dirname,'green',conn)

#reg.createRegionByImage(17,dirname,'cyan',conn)
"""
"""
#plt.plotHistAssocCatDist(1,conn)
#plt.plotBarLR(2,3,conn)
#plt.plotBarLR(2,3,conn)
#plt.plotBarBGLR(3,10,3,conn)
plt.plotBarSrcBGLR(2,3,10,3,conn)
#plt.plotBarRho(2,3,conn)
#plt.plotBarDist(1,3,conn)
"""


