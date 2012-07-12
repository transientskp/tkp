#!/usr/bin/python

import sys, os, time
from itertools import count
import logging
import tkp.database.database as database
import tkp.database.dataset as ds
import tkp.database.dbregion as reg
import tkp.database.utils as dbu
import monetdb.sql
from tkp.sourcefinder import image
from tkp.config import config
from tkp.utility import accessors, containers

db_enabled = config['database']['enabled']
db_host = config['database']['host']
db_user = config['database']['user']
db_passwd = config['database']['password']
db_dbase = config['database']['name']
db_port = config['database']['port']
db_autocommit = config['database']['autocommit']

#print db_enabled 
#print db_host 
#print db_user 
#print db_passwd 
#print db_dbase 
#print db_port 
#print db_autocommit 

basedir = config['test']['datapath']
imagesdir = basedir + '/fits'
regionfilesdir = '/regions'

try:
    db = database.DataBase(host=db_host, name=db_dbase, user=db_user, password=db_passwd, port=db_port, autocommit=db_autocommit)
    print db.__repr__()
    
    iter_start = time.time()
    
    description = 'TRAP: LOFAR LSC_3C295'
    dataset = ds.DataSet(data={'description': description}, database=db)
    print "dataset.id:", dataset.id

    #sys.exit()
    i = 0
    files = os.listdir(imagesdir)
    files.sort()
    for file in files:
        my_fitsfile = accessors.FitsFile(imagesdir + '/' + file)
        my_image = accessors.sourcefinder_image_from_accessor(my_fitsfile)
        #print "type(my_image):",type(my_image)
        print "\ni: ", i, "\nfile: ", file
        dbimg = accessors.dbimage_from_accessor(dataset, my_fitsfile)
        print "dbimg.id: ", dbimg.id
        
        extracted_sources = my_image.extract()
        print("found %s sources in %s" % (len(extracted_sources), file))
        tuple_sources = [extracted_source.serialize() for extracted_source in extracted_sources]
        #print "tuple_sources",tuple_sources
        
        dbu.insert_extracted_sources(db.connection, dbimg.id, tuple_sources)
        dbu.associate_extracted_sources(db.connection, dbimg.id)
        dbu.associate_with_catalogedsources(db.connection, dbimg.id)
        print "xtrsrc: ", reg.extractedsourcesInImage(db.connection, dbimg.id, regionfilesdir)
        print "assoccatsrc: ", reg.assoccatsourcesInImage(db.connection, dbimg.id, regionfilesdir)
        #print dbu.detect_variable_sources(db.connection, dataset.id, 0.1, 4)
        my_image.clearcache()
        i += 1

    db.close()
except db.Error, e:
    print "Failed for reason: %s " % (e,)
    raise

