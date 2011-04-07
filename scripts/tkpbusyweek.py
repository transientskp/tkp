#!/usr/bin/python

import os, time
import sys
from itertools import count
import tkp_lib.database as db
import tkp_lib.dataset as d
import tkp_lib.settings as s
from tkp_lib import image, accessors, containers

answer=str(raw_input('Did you load the LSM table (y/n)? '))

if answer != 'y':
    sys.exit('\n\tLoad LSM first by CALL LoadLSM(ra_min0,ra_max,decl_min,decl_max,\'NVSS\',\'VLSS\',\'WENSS\');')

imagesdir = '/dir/where/my/images/are'

print "\nResults will be stored in", s.database_type, "dbname:", s.database_dbase

conn = db.connection()

description = 'A description of the dataset (and images)'
# This will create an entry in the datasets table
dataset = d.DataSet(description)
# This is the id under which the dataset is stored
dsid = dataset.id
print "Dataset Id:", dsid

files = os.listdir(imagesdir)
files.sort()
for file in files:
    # It can only process Fits files
    # And only those having some info the header
    my_fitsfile = accessors.FitsFile(imagesdir + file)
    my_image = image.ImageData(my_fitsfile, dataset = dataset)
    # This is the id under which the current image is stored,
    # with a reference id to the dataset id
    print "Image Id:", my_image.id[0]
    results = my_image.sextract(det=7,anl=4)
    # Store results in extractedsources table
    results.savetoDB(conn)
    # Check for associations in current dataset and
    # store results in assocxtrsources table
    results.assocXSrc2XSrc(my_image.id[0], conn)
    # Check for associations in (specified, via LoadLSM()) catalogs and
    # store results in assoccatsources table
    results.assocXSrc2Cat(my_image.id[0], conn)
    my_image.clearcache()

log.close()
conn.close()

