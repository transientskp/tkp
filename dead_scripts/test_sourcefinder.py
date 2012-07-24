#!/usr/bin/python

import sys, os, time
from itertools import count
import logging
from tkp.sourcefinder import image
from tkp.config import config
from tkp.utility import accessors, containers

basedir = config['test']['datapath']
imagesdir = basedir + '/fits'
regionfilesdir = basedir + '/regions'

iter_start = time.time()

i = 0
files = os.listdir(imagesdir)
files.sort()
for file in files:
    my_fitsfile = accessors.FitsFile(imagesdir + '/' + file)
    my_image = accessors.sourcefinder_image_from_accessor(my_fitsfile)
    results = my_image.extract()
    print results
    my_image.clearcache()
    i += 1

