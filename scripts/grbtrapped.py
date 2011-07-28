#!/usr/bin/python

import sys, os, time
from itertools import count
import logging
import tkp.database.dataset as d
import tkp.database.utils as dbu
from tkp.sourcefinder import image, accessors
from tkp.utility import containers

import monetdb.sql as db
from monetdb.sql import Error as Error

host = sys.argv[1] # number of sources per image
loadlsm = sys.argv[2] # Y/N to load lsm

db_type = "MonetDB"
db_host = host
db_port = 50000
db_dbase = "grb"
db_user = "grb"
db_passwd = "grb"

conn = db.connect(hostname=db_host,database=db_dbase,username=db_user,password=db_passwd)

starttime = time.time()

# where the images are:
#basedir = '/home/scheers/maps/lofar/'
basedir = '/home/scheers/maps/grb030329/pbcor'
imagesdir = basedir + '/fits'

print "\nResults will be stored in", db_type, "dbname:", db_dbase

logtime = time.strftime("%Y%m%d-%H%M")
logfile = basedir + '/log/' + db_type + '_' + db_dbase + '_' + logtime + '.log'
log = open(logfile, 'w')
#log.write('-')

query = 0
#query_time = []
sql_st = []

try:
    iter_start = time.time()
    cursor = conn.cursor()

    if loadlsm == 'Y':
        query = -2
        sql_st.append("""\
        CALL LoadLSM(158, 165, 24, 18.5, 'NVSS', 'VLSS', 'WENSS')
        """)
        #query_start = time.time()
        cursor.execute(sql_st[-1])
        #query_time.append((time.time() - query_start))
        #print "\tQuery ", query, ": ", str(round(query_time[-1] * 1000, 2)), "ms"
        conn.commit()
        print "LSM Loaded"
    else:
        print "LSM NOT Loaded"

    description = 'TRAPPED:  WSRT multifrequency GRB030329'
    dataset = d.DataSet(description)
    print "Dataset Id:", dataset.id

    i = 0
    files = os.listdir(imagesdir)
    files.sort()
    for file in files:
        #if (file.endswith('.fits') ):
        if (file.startswith('GRBPBCOR_WSRT_1400') ):
            if i < 2:
                print "\ni: ", i, ", file: ", file
                my_fitsfile = accessors.FitsFile(imagesdir + file, beam=(2e-2,2e-2,0))
                my_image = image.ImageData(my_fitsfile, conn = conn, dataset = dataset)
                #print "im.obstime:",my_image.obstime
                imid = my_image.id[0]
                print "Image Id:", imid
                results = my_image.extract(det=7, anl=4)
                print results
                t_start = time.time()
                dbu.insert_extracted_sources(conn, imid, results)
                #dbu.associate_extracted_sources(conn, imid, deRuiter_r)
                #dbu.variability_detection(conn, dataset.id, 0.2, 3.0)
                t_proc = time.time() - t_start
                print "image processing: t =", str(t_proc), "s"
                log.write(str(i) + ";" + str(t_proc) + "\n") 
                my_image.clearcache()
            i += 1

    conn.close()
    log.close()
except db.Error, e:
    logging.warn("Failed on query nr %s reason: %s " % (query, e))
    log.write("Failed on query nr %s reason: %s " % (query, e))
    log.close()
    logging.debug("Failed query nr: %s, reason: %s" % (query, e))

