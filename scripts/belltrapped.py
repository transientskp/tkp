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

db_host = "togano"
db_dbase = "bell"
#db_dbase = "node1db+node1db@*/lightcurve1,node2db+node2db@*/lightcurve2,node3db+node3db@*/lightcurve3"
db_user = "bell"
db_passwd = "bell"
db_port = 60200
db_autocommit = True

#basedir = '/home/bscheers/maps/bell'
basedir = '/export/scratch1/bscheers/maps/bell'
imagesdir = basedir + '/fits'

db = database.DataBase(host=db_host, name=db_dbase, user=db_user, password=db_passwd, port=db_port, autocommit=db_autocommit)
#db = database.DataBase(host=db_host, name=db_dbase, port=db_port, autocommit=db_autocommit)

#logtime = time.strftime("%Y%m%d-%H%M")
#logfile = basedir + '/log/MonetDB_' + db_dbase + '_' + logtime + '.log'
#log = open(logfile, 'w')

try:
    iter_start = time.time()

    #if loadlsm == 'Y':
    #    query = """\
    #    CALL LoadLSM(47, 59, 50, 58, 'NVSS', 'VLSS', 'WENSS')
    #    """
    #    db.cursor.execute(query)
    #    #db.commit()
    #    print "LSM Loaded"
    #else:
    #    print "LSM NOT Loaded"
    if loadlsm == 'Y':
        dbu.load_LSM(db.connection, 47.0, 59.0, 50.0, 58.0)

    description = 'TRAPPED: LOFAR image reduced by MBell'
    dataset = ds.DataSet(data={'dsinname': 'toedeloe'}, database=db)
    print "dataset.id:", dataset.id

    i = 0
    files = os.listdir(imagesdir)
    files.sort()
    for file in files:
        print "\ni: ", i, ", file: ", file
        my_fitsfile = accessors.FitsFile(imagesdir + '/' + file)
        my_image = accessors.sourcefinder_image_from_accessor(my_fitsfile)
        dbimg = accessors.dbimage_from_accessor(dataset, my_fitsfile)
        print "dbimg: ", dbimg
        print "dbimg._imageid: ", dbimg.id
        #results = my_image.extract(det=7, anl=4)
        results = my_image.extract(det=10.0)
        print results
        dbu.insert_extracted_sources(db.connection, dbimg.id, results)
        #dbu.associate_extracted_sources(db.connection, dbimg.id, deRuiter_r=18.5/3600.)
        dbu.associate_extracted_sources(db.connection, dataset.id, dbimg.id, deRuiter_r=0.0112)
        #dbu.associate_across_frequencies(db.connection, dataset.id, dbimg.id, deRuiter_r=0.0112)
        #dbu.associate_with_catalogedsources(db.connection, dbimg.id)
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

