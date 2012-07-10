#!/usr/bin/python

import sys, os, time
from itertools import count
import logging
import tkp.database.database as database
import tkp.database.dataset as ds
import tkp.database.dbregion as reg
import tkp.database.utils as dbu
from tkp.sourcefinder import image
from tkp.config import config
from tkp.utility import accessors, containers

#loadlsm = sys.argv[1] # Y/N to load lsm

#db_host = "togano"
#db_dbase = "bell"
#db_dbase = "user1+pw1@*/lightcurve1,user2+pw2@*/lightcurve2,user3+pw3@*/lightcurve3,user4+pw4@*/lightcurve4,user5+pw5@*/lightcurve5"
#-lsql+mf -duser1+pw1@*/lightcurve1,user2+pw2@*/lightcurve2,user3+pw3@*/lightcurve3,user4+pw4@*/lightcurve4,user5+pw5@*/lightcurve5
#db_autocommit = True

db_host = config['database']['host']
db_user = config['database']['user']
db_passwd = config['database']['password']
db_dbase = config['database']['name']
db_port = config['database']['port']
db_autocommit = config['database']['autocommit']

basedir = config['test']['datapath']
imagesdir = basedir + '/fits'
regionfilesdir = basedir + '/regions'

db = database.DataBase(host=db_host, name=db_dbase, user=db_user, password=db_passwd, port=db_port, autocommit=db_autocommit)

#logtime = time.strftime("%Y%m%d-%H%M")
#logfile = basedir + '/log/MonetDB_' + db_dbase + '_' + logtime + '.log'
#log = open(logfile, 'w')

try:
    iter_start = time.time()

    #if loadlsm == 'Y':
    #    dbu.load_LSM(db.connection, 47.0, 59.0, 50.0, 58.0)

    description = 'TRAPPED: GRB030329 multifrequency images'
    dataset = ds.DataSet(data={'inname': description}, database=db)
    print "dataset.id:", dataset.id

    i = 0
    files = os.listdir(imagesdir)
    files.sort()
    for file in files:
        my_fitsfile = accessors.FitsFile(imagesdir + '/' + file)
        my_image = accessors.sourcefinder_image_from_accessor(my_fitsfile)
        #print "type(my_image):",type(my_image)
        dbimg = accessors.dbimage_from_accessor(dataset, my_fitsfile)
        print "\ni: ", i, "\nfile: ", file, "; dbimg.id: ", dbimg.id
        results = my_image.extract()
        print results
        dbu.insert_extracted_sources(db.connection, dbimg.id, results)
        dbu.associate_extracted_sources(db.connection, dbimg.id)
        dbu.associate_with_catalogedsources(db.connection, dbimg.id)
        print "xtrsrc: ", reg.extractedsourcesInImage(db.connection, dbimg.id, regionfilesdir)
        print "assoccatsrc: ", reg.assoccatsourcesInImage(db.connection, dbimg.id, regionfilesdir)
        #print "catsrc: ", reg.catsourcesInRegion(db.connection, dbimg.id, 47.0, 59.0, 50.0, 58.0, regionfilesdir,flux_lim=0.09)
        #if i>2: #dbu.variability_detection(conn, dataset.id)
        my_image.clearcache()
        i += 1

    db.close()
    #log.close()
except db.Error, e:
    print "Failed for reason: %s " % (e,)
    raise
    #log.write("Failed on query nr %s reason: %s " % (query, e))
    #log.close()
    #logging.debug("Failed query nr: %s, reason: %s" % (query, e))

