#!/usr/bin/python

import sys, os, time
from itertools import count
import logging
import tkp.database.database as database
import tkp.database.dataset as ds
import tkp.database.utils as dbu
from tkp.sourcefinder import image
from tkp.utility import accessors, containers

loadlsm = sys.argv[1] # Y/N to load lsm

db_dbase = "bell"
db_user = "bell"
db_passwd = "bell"

basedir = '/home/bscheers/maps/bell'
imagesdir = basedir + '/fits'

db = database.DataBase(name=db_dbase, port="60200", user=db_user, password=db_passwd)

#logtime = time.strftime("%Y%m%d-%H%M")
#logfile = basedir + '/log/MonetDB_' + db_dbase + '_' + logtime + '.log'
#log = open(logfile, 'w')

try:
    iter_start = time.time()

    if loadlsm == 'Y':
        query = """\
        CALL LoadLSM(158, 165, 18, 25, 'NVSS', 'VLSS', 'WENSS')
        """
        db.cursor.execute(query)
        db.commit()
        print "LSM Loaded"
    else:
        print "LSM NOT Loaded"

    description = 'TRAPPED: WSRT multifrequency GRB030329'
    dataset = ds.DataSet(description, database=db)
    print dataset

    i = 0
    files = os.listdir(imagesdir)
    files.sort()
    for file in files:
        print "\ni: ", i, ", file: ", file
        #my_fitsfile = accessors.FitsFile(imagesdir + '/' + file, beam=(2e-2,2e-2,0))
        my_fitsfile = accessors.FitsFile(imagesdir + '/' + file)
        my_image = accessors.sourcefinder_image_from_accessor(my_fitsfile)
        dbimg = accessors.dbimage_from_accessor(dataset, my_fitsfile)
        print "dbimg: ", dbimg
        print "dbimg._imageid: ", dbimg._imageid
        #results = my_image.extract(det=7, anl=4)
        results = my_image.extract(det=10.0)
        print results
        dbu.insert_extracted_sources(db.connection, dbimg._imageid, results)
        #dbu.associate_extracted_sources(db.connection, dbimg._imageid, deRuiter_r=18.5/3600.)
        dbu.associate_extracted_sources(db.connection, dbimg._imageid, deRuiter_r=18.5)
        #if i>2: #dbu.variability_detection(conn, dataset.id)
        my_image.clearcache()
        i += 1

    db.close()
    #log.close()
except db.Error, e:
    logging.warn("Failed on query nr %s reason: %s " % (query, e))
    #log.write("Failed on query nr %s reason: %s " % (query, e))
    #log.close()
    logging.debug("Failed query nr: %s, reason: %s" % (query, e))

