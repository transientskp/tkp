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

db_dbase = "grb"
db_user = "grb"
db_passwd = "grb"

basedir = '/home/bscheers/maps/grb030329/pbcor'
imagesdir = basedir + '/fits'

db = database.DataBase(name=db_dbase, user=db_user, password=db_passwd)

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
        #if (file.endswith('.fits') ):
        if (file.startswith('GRBPBCOR_WSRT_1400') ):
            if i < 1:
                print "\ni: ", i, ", file: ", file
                #my_fitsfile = accessors.FitsFile(imagesdir + '/' + file, beam=(2e-2,2e-2,0))
                my_fitsfile = accessors.FitsFile(imagesdir + '/' + file)
                print "my_fitsfile.obstime:", my_fitsfile.obstime
                print "my_fitsfile.freqeff:", my_fitsfile.freqeff
                #my_image = image.ImageData(my_fitsfile.data, my_fitsfile.beam, my_fitsfile.wcs)
                #my_image = accessors.sourcefinder_image_from_accessor(my_fitsfile)
                #print "my_image: ", my_image
                #imid = my_image.id[0]
                #print "Image Id:", imid
                dbimg = accessors.dbimage_from_accessor(dataset, my_fitsfile)
                print "dbimg: ", dbimg
                print "dbimg._imageid: ", dbimg._imageid
                #results = my_image.extract(det=7, anl=4)
                #print results
                #t_start = time.time()
                #dbu.insert_extracted_sources(conn, imid, results)
                #dbu.associate_extracted_sources(conn, imid, deRuiter_r)
                #dbu.variability_detection(conn, dataset.id, 0.2, 3.0)
                #t_proc = time.time() - t_start
                #print "image processing: t =", str(t_proc), "s"
                #log.write(str(i) + ";" + str(t_proc) + "\n") 
                #my_image.clearcache()
            i += 1

    db.close()
    #log.close()
except db.Error, e:
    logging.warn("Failed on query nr %s reason: %s " % (query, e))
    #log.write("Failed on query nr %s reason: %s " % (query, e))
    #log.close()
    logging.debug("Failed query nr: %s, reason: %s" % (query, e))

