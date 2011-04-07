#!/usr/bin/python

import tkp_lib.database as db
import tkp_lib.dbdiagnostics as diagn
import tkp_lib.dbplots as dbplots

conn = db.connection()

catid = 3 # NVSS
dsid = 45

#xtrsrcid = [2143197,2143203,2143209,2143245]
xtrsrcid = [2143261]

for i in range(len(xtrsrcid)):
    files = dbplots.plotGRB030329LightCurveSecByXSource(xtrsrcid[i], dsid, conn)
    print files

