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
regionfilesdir = basedir + '/regions'
BOX_IN_BEAMPIX = 10

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
        
        # source_extraction
        dbu.insert_extracted_sources(db.connection, dbimg.id, tuple_sources)
        print "xtrsrc: ", reg.extractedsourcesInImage(db.connection, dbimg.id, regionfilesdir)
        dbu.associate_extracted_sources(db.connection, dbimg.id)
        print "runcat: ", reg.runcatInDataset(db.connection, dataset.id, regionfilesdir)
        dbu.associate_with_catalogedsources(db.connection, dbimg.id)
        #print "assoccatsrc: ", reg.assoccatsourcesInImage(db.connection, dbimg.id, regionfilesdir)
        
        # monitoringlist
        fitsimage = accessors.FITSImage(imagesdir + '/' + file)
        db_image = ds.Image(id=dbimg.id, database=db)
        sources = db_image.monitoringsources()
        # Run the source finder on these sources
        if len(sources):
            print "Measuring %d undetected monitoring sources: %s" % (len(sources), str(sources))
            data_image = accessors.sourcefinder_image_from_accessor(fitsimage)
            results = data_image.fit_fixed_positions(
                [(source[0], source[1]) for source in sources],
                boxsize=BOX_IN_BEAMPIX*max(data_image.beam[0], data_image.beam[1]))
            # Filter out the bad ones, and combines with xtrsrc_ids
            results = [(source[2], source[3], result.serialize()) for source, result in
                zip(sources, results) if result is not None]
            db_image.insert_monitoring_sources(results)
        
        # transient_search
        from scipy.stats import chisqprob
        import numpy
        #from lofarpipe.support.baserecipe import BaseRecipe
        #from lofarpipe.support import lofaringredient
        #from lofar.parameterset import parameterset
        #from tkp.config import config
        #import tkp.database.database
        #import tkp.database.dataset
        #import tkp.database.utils as dbu
        from tkp.classification.transient import Transient
        from tkp.classification.transient import Position
        from tkp.classification.transient import DateTime
    
        print "Finding transient sources in the database"
        #parset = parameterset(self.inputs['parset'])
        #dataset_id = self.inputs['args'][0]
        #self.database = tkp.database.database.DataBase()
        #self.dataset = tkp.database.dataset.DataSet(
        #    id=dataset_id, database=self.database)
        #limits = {'eta': parset.getFloat(
        #    'probability.eta_lim', config['transient_search']['eta_lim']),
        #          'V': parset.getFloat(
        #    'probability.V_lim', config['transient_search']['V_lim'])}
        varsources = dbu.detect_variable_sources(db.connection, dataset.id, V_lim=0.1, eta_lim=5.0)
        transients = []
        if len(varsources) > 0:
            print "Found", len(varsources), "variable sources"
            #detection_threshold = parset.getFloat(
            #    'probability.threshold',
            #    config['transient_search']['probability'])
            detection_threshold = 0.99
            # need (want) sorting by sigma
            # This is not pretty, but it works:
            tmpvarsources = dict((key,  [varsource[key] for varsource in varsources])
                           for key in ('srcid', 'npoints', 'v_nu', 'eta_nu'))
            srcids = numpy.array(tmpvarsources['srcid'])
            weightedpeaks, dof = (numpy.array(tmpvarsources['v_nu']),
                                  numpy.array(tmpvarsources['npoints'])-1)
            probability = 1 - chisqprob(tmpvarsources['eta_nu'] * dof, dof)
            selection = probability > detection_threshold
            transient_ids = numpy.array(srcids)[selection]
            selected_varsources = numpy.array(varsources)[selection]
            siglevels = probability[selection]
            #minpoints = parset.getInt('probability.minpoints',
            #                          config['transient_search']['minpoints'])
            minpoints = 2
            for siglevel, varsource in zip(siglevels, selected_varsources):
                if varsource['npoints'] < minpoints:
                    continue
                position = Position(ra=varsource['ra'], dec=varsource['dec'],
                                    error=(varsource['ra_err'], varsource['dec_err']))
                transient = Transient(srcid=varsource['srcid'], position=position)
                transient.siglevel = siglevel
                transient.eta = varsource['eta_nu']
                transient.V = varsource['v_nu']
                transient.dataset = varsource['dataset']
                transient.monitored = dbu.is_monitored(db.connection, transient.srcid)
                print "transient.srcid =", transient.srcid
                dbu.insert_transient(db.connection, transient, dataset.id, 
                    #images=self.inputs['image_ids'])
                    images=[dbimg.id])
                transients.append(transient)
        else:
            transient_ids = numpy.array([], dtype=numpy.int)
            siglevels = numpy.array([], dtype=numpy.float)
        #self.outputs['transient_ids'] = map(int, transient_ids)
        #self.outputs['siglevels'] = siglevels
        #self.outputs['transients'] = transients

        
        
        #print dbu.detect_variable_sources(db.connection, dataset.id, 0.1, 4)
        my_image.clearcache()
        i += 1

    db.close()
except db.Error, e:
    print "Failed for reason: %s " % (e,)
    raise


