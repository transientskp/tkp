#!/usr/bin/python

import sys, os, time
import tkp.database.database as database
import tkp.database.gsmutils as gsm

db_host = "togano"
db_dbase = "aug2011sp2"
db_user = "aug2011sp2"
db_passwd = "aug2011sp2"
db_port = 60200
db_autocommit = True

db = database.DataBase(host=db_host, name=db_dbase, user=db_user, password=db_passwd, port=db_port, autocommit=db_autocommit)

#ra_c = 289.89258333333333
#decl_c = 0.0017444444444444445

ra_c = 287.80216666666666 
decl_c = 9.096861111111112

#ra_c = 286.87425
#decl_c = 7.1466111111111115

#ra_c = 70.0
#decl_c = 33.0
fov_radius = 5.0
assoc_theta = 0.025

gsm.expected_flux_in_fov(db.connection, ra_c, decl_c, fov_radius, assoc_theta, 'bbs.skymodel.test', storespectraplots=False)

db.close()

