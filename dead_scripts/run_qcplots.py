import os
import tkp.database.database as database
import tkp.database.qcplots as qc
from tkp.config import config

db_host = config['database']['host']
db_user = config['database']['user']
db_passwd = config['database']['password']
db_dbase = config['database']['name']
db_port = config['database']['port']
db_autocommit = config['database']['autocommit']

basedir = config['test']['datapath']
regdir = basedir + '/regions'
plotdir = basedir + '/plots'

db = database.DataBase(host=db_host, name=db_dbase, user=db_user, password=db_passwd, port=db_port, autocommit=db_autocommit)
conn=db.connection

f = qc.rms_distance_from_fieldcentre(conn, 1)
print f

f = qc.hist_sources_per_image(conn, 1)
print f

f = qc.scat_pos_counterparts(conn, 1)
print f

f = qc.scat_pos_all_counterparts(conn, 1)
print f

f = qc.hist_all_counterparts_dist(conn, 1)
print f

f = qc.hist_all_counterparts_assoc_r(conn, 1)
print f

