#!/usr/bin/python

import tkp_lib.database as db
import tkp_lib.dbdiagnostics as diagn

conn = db.connection()

catid = 3 # NVSS
dsid = 1
dsid_min = 2
dsid_max = 9

files = diagn.plotWenssNvssFig4(dsid,dsid_min,dsid_max,catid,conn)
print files

"""
files = diagn.plotWenssNvssFig3(dsid,dsid_min,dsid_max,catid,conn)
print files

files = diagn.plotWenssNvssFig5(dsid,dsid_min,dsid_max,catid,conn)
print files

files = diagn.plotWenssNvssFig6(dsid,catid,conn)
print files

files = diagn.plotWenssNvssSpIdxFig7(dsid,catid,conn)
print files

files = diagn.scatterWenssNvssSourceFieldplusBackGround(dsid,dsid_min,dsid_max,catid,conn)
print files

files = diagn.scatterSourceAssocIndexX2C(dsid, catid, conn)
print files

files = diagn.scatterSourceAssocIndexX2CBackGround(dsid_min, dsid_max,catid, conn)
print files
"""

