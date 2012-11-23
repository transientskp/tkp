#!/usr/bin/python

import sys, os, time
import numpy
from itertools import count
import logging
import tkp.database.database as database
from tkp.database import ExtractedSource
import tkp.database.orm as ds
import tkp.database.dbregion as reg
import tkp.database.utils.general as dbg
import tkp.database.utils.associations as dbu
import tkp.database.utils.monitoringlist as mon
import tkp.database.utils.transients as dbt
from tkp.classification.features import lightcurve as lcmod
from tkp.classification.features import catalogs as catmod
import tkp.classification.transient as tr
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
    
    description = 'TRAP: LOFAR LBA Multifreq Bands'
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
        dbg.insert_extracted_sources(db.connection, dbimg.id, tuple_sources)
        print "xtrsrc: ", reg.extractedsourcesInImage(db.connection, dbimg.id, regionfilesdir)
        dbu.associate_extracted_sources(db.connection, dbimg.id)
        print "runcat: ", reg.runcatInDataset(db.connection, dataset.id, regionfilesdir)
        dbu.associate_with_catalogedsources(db.connection, dbimg.id)
        #print "assoccatsrc: ", reg.assoccatsourcesInImage(db.connection, dbimg.id, regionfilesdir)
        
        # monitoringlist
        #fitsimage = accessors.FITSImage(imagesdir + '/' + file)
        #db_image = ds.Image(id=dbimg.id, database=db)
        #sources = dbimg.monitoringsources()
        # Run the source finder on these sources
        #if len(sources):
        #    print "Measuring %d undetected monitoring sources: %s" % (len(sources), str(sources))
        #    #data_image = accessors.sourcefinder_image_from_accessor(fitsimage)
        #    results = my_image.fit_fixed_positions(
        #        [(source[0], source[1]) for source in sources],
        #        boxsize=BOX_IN_BEAMPIX*max(my_image.beam[0], my_image.beam[1]))
        #    # Filter out the bad ones, and combines with xtrsrc_ids
        #    results = [(source[2], source[3], result.serialize()) for source, result in
        #        zip(sources, results) if result is not None]
        #    mon.insert_monitored_sources(db.connection, results, dbimg.id)
        
        # monitoringlist
        dataset.update_images()
        image_ids = [img.id for img in dataset.images]
        ids_filenames = dbg.get_imagefiles_for_ids(db.connection, image_ids)
        det_thresh = config['source_extraction']['detection_threshold']
        dataset.mark_transient_candidates(single_epoch_threshold = det_thresh,
                                          combined_threshold = det_thresh)
        sources = dbimg.monitoringsources()
        if len(sources):
            print "Measuring %d undetected monitoring sources." % (len(sources),)
            #data_image = sourcefinder_image_from_accessor(fitsimage)
            results = my_image.fit_fixed_positions(
                [(source[0], source[1]) for source in sources],
                boxsize=BOX_IN_BEAMPIX*max(my_image.beam[0], my_image.beam[1]))
            # Filter out the bad ones, and combines with xtrsrc_ids
            results = [(source[2], source[3], result.serialize()) for source, result in zip(sources, results) if result is not None]
            dbimg.insert_monitored_sources(results)
        
        # transient_search
        transient_ids, siglevels, transients = dbt.transient_search(
                                conn = db.connection,
                                dataset = dataset,
                                eta_lim = config['transient_search']['eta_lim'],
                                V_lim = config['transient_search']['V_lim'],
                                probability_threshold = config['transient_search']['probability'],
                                minpoints = config['transient_search']['minpoints'],
                                image_ids=[dbimg.id,])
        # feature_extraction
        for transient in transients:
            source = ExtractedSource(id=transient.runcatid, database=db)
            lightcurve = lcmod.LightCurve(*zip(*source.lightcurve()))
            lightcurve.calc_background()
            lightcurve.calc_stats()
            lightcurve.calc_duration()
            lightcurve.calc_fluxincrease()
            lightcurve.calc_risefall()
            if lightcurve.duration['total']:
                variability = (lightcurve.duration['active'] /
                               lightcurve.duration['total'])
            else:
                variability = numpy.NaN
            features = {
                'duration': lightcurve.duration['total'],
                'variability': variability,
                'wmean': lightcurve.stats['wmean'],
                'median': lightcurve.stats['median'],
                'wstddev': lightcurve.stats['wstddev'],
                'wskew': lightcurve.stats['wskew'],
                'wkurtosis': lightcurve.stats['wkurtosis'],
                'max': lightcurve.stats['max'],
                'peakflux': lightcurve.fluxincrease['peak'],
                'relpeakflux': lightcurve.fluxincrease['increase']['relative'],
                'risefallratio': lightcurve.risefall['ratio'],
                }
            transient.duration = lightcurve.duration['total']
            transient.timezero = lightcurve.duration['start']
            transient.variability = variability
            transient.features = features
            transient.catalogs = catmod.match_catalogs(transient)

        ## transient_search
        #from scipy.stats import chisqprob
        #import numpy
        ##from lofarpipe.support.baserecipe import BaseRecipe
        ##from lofarpipe.support import lofaringredient
        ##from lofar.parameterset import parameterset
        ##from tkp.config import config
        ##import tkp.database.database
        ##import tkp.database.dataset
        ##import tkp.database.utils as dbu
        #from tkp.classification.transient import Transient
        #from tkp.classification.transient import Position
        #from tkp.classification.transient import DateTime
    
        #print "Finding transient sources in the database"
        ##parset = parameterset(self.inputs['parset'])
        ##dataset_id = self.inputs['args'][0]
        ##self.database = tkp.database.database.DataBase()
        ##self.dataset = tkp.database.dataset.DataSet(
        ##    id=dataset_id, database=self.database)
        ##limits = {'eta': parset.getFloat(
        ##    'probability.eta_lim', config['transient_search']['eta_lim']),
        ##          'V': parset.getFloat(
        ##    'probability.V_lim', config['transient_search']['V_lim'])}
        #varsources = dbt.detect_variable_sources(db.connection, dataset.id, V_lim=0.1, eta_lim=5.0)
        #transients = []
        #if len(varsources) > 0:
        #    print "Found", len(varsources), "variable sources"
        #    #detection_threshold = parset.getFloat(
        #    #    'probability.threshold',
        #    #    config['transient_search']['probability'])
        #    detection_threshold = 0.99
        #    # need (want) sorting by sigma
        #    # This is not pretty, but it works:
        #    tmpvarsources = dict((key,  [varsource[key] for varsource in varsources])
        #                   for key in ('runcatid', 'npoints', 'v_nu', 'eta_nu'))
        #    srcids = numpy.array(tmpvarsources['runcatid'])
        #    weightedpeaks, dof = (numpy.array(tmpvarsources['v_nu']),
        #                          numpy.array(tmpvarsources['npoints'])-1)
        #    probability = 1 - chisqprob(tmpvarsources['eta_nu'] * dof, dof)
        #    selection = probability > detection_threshold
        #    transient_ids = numpy.array(srcids)[selection]
        #    selected_varsources = numpy.array(varsources)[selection]
        #    siglevels = probability[selection]
        #    #minpoints = parset.getInt('probability.minpoints',
        #    #                          config['transient_search']['minpoints'])
        #    minpoints = 2
        #    for siglevel, varsource in zip(siglevels, selected_varsources):
        #        if varsource['npoints'] < minpoints:
        #            continue
        #        position = Position(ra=varsource['ra'], dec=varsource['dec'],
        #                            error=(varsource['ra_err'], varsource['dec_err']))
        #        transient = Transient(runcatid=varsource['runcatid'], position=position)
        #        transient.siglevel = siglevel
        #        transient.eta = varsource['eta_nu']
        #        transient.V = varsource['v_nu']
        #        transient.dataset = varsource['dataset']
        #        transient.monitored = mon.is_monitored(db.connection, transient.runcatid)
        #        print "transient.srcid =", transient.runcatid
        #        dbt.insert_transient(db.connection, transient, dataset.id, 
        #            #images=self.inputs['image_ids'])
        #            image_ids=[dbimg.id])
        #        transients.append(transient)
        #        print "transients:",transients
        #        
        #        # feature_extraction
        #        source = ds.ExtractedSource(id=transient.runcatid, database=db)
        #        lightcurve = lcmod.LightCurve(*zip(*source.lightcurve()))
        #        lightcurve.calc_background()
        #        lightcurve.calc_stats()
        #        lightcurve.calc_duration()
        #        lightcurve.calc_fluxincrease()
        #        lightcurve.calc_risefall()
        #        if lightcurve.duration['total']:
        #            variability = (lightcurve.duration['active'] /
        #                           lightcurve.duration['total'])
        #        else:
        #            variability = numpy.NaN
        #        features = {
        #            'duration': lightcurve.duration['total'],
        #            'variability': variability,
        #            'wmean': lightcurve.stats['wmean'],
        #            'median': lightcurve.stats['median'],
        #            'wstddev': lightcurve.stats['wstddev'],
        #            'wskew': lightcurve.stats['wskew'],
        #            'wkurtosis': lightcurve.stats['wkurtosis'],
        #            'max': lightcurve.stats['max'],
        #            'peakflux': lightcurve.fluxincrease['peak'],
        #            'relpeakflux': lightcurve.fluxincrease['increase']['relative'],
        #            'risefallratio': lightcurve.risefall['ratio'],
        #            }
        #        transient.duration = lightcurve.duration['total']
        #        transient.timezero = lightcurve.duration['start']
        #        transient.variability = variability
        #        transient.features = features
        #        transient.catalogs = catmod.match_catalogs(transient)
        #        
        #        # classification
        #else:
        #    transient_ids = numpy.array([], dtype=numpy.int)
        #    siglevels = numpy.array([], dtype=numpy.float)
        ##self.outputs['transient_ids'] = map(int, transient_ids)
        ##self.outputs['siglevels'] = siglevels
        ##self.outputs['transients'] = transients

        ##print dbu.detect_variable_sources(db.connection, dataset.id, 0.1, 4)
        
        
        my_image.clearcache()
        i += 1

    db.close()
except db.Error, e:
    print "Failed for reason: %s " % (e,)
    raise


