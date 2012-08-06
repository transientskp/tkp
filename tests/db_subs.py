import os
from tkp.config import config as tkp_conf
import datetime
import logging
from collections import namedtuple

ExtractedSourceTuple=namedtuple("ExtractedSourceTuple",
                                ['ra', 'dec' ,
                                'ra_err' ,'dec_err' ,
                                'peak' ,'peak_err',
                                'flux', 'flux_err',
                                 'sigma',
                                 'beam_maj', 'beam_min',
                                 'beam_angle'
                                ]) 

def use_test_database_by_default():
    test_db_name = tkp_conf['test']['test_database_name']
    tkp_conf['database']['name'] = test_db_name
    tkp_conf['database']['user'] = test_db_name
    tkp_conf['database']['password'] = test_db_name
    
def delete_test_database(database):
    """
    Use with caution!

    NB. Not the same as a freshly initialised database.
        All the sequence counters are offset.
    """
    import monetdb.sql
    if database.name.lower().find("test") != 0:
        raise ValueError("You tried to delete a database not prefixed with 'test'.\n"
                         "Not recommended!")
    try:
        cursor = database.connection.cursor()
        query = "DELETE from monitoringlist"
        cursor.execute(query)
        query = "DELETE from runningcatalog_flux"
        cursor.execute(query)
        query = "DELETE from assocxtrsource"
        cursor.execute(query)
        query = "DELETE from temprunningcatalog"
        cursor.execute(query)
        query = "DELETE from runningcatalog"
        cursor.execute(query)
        query = "DELETE from extractedsource"
        cursor.execute(query)
        query = "DELETE from image"
        cursor.execute(query)
        query = "DELETE from dataset"
        cursor.execute(query)
        query = "DELETE from transient"
        cursor.execute(query)
        if not tkp_conf['database']['autocommit']:
            database.connection.commit()
    except monetdb.sql.Error:
        logging.warn("Query failed when trying to blank database\n"
                     "Query: "+query)
        raise
    finally:
        cursor.close()
             
    
def example_dbimage_datasets(n_images):
    """Generate a list of image data dictionaries.
    
    These can be used to create known entries in the image table.
    """
    starttime = datetime.datetime(2012,1,1) #Happy new year
    time_spacing = datetime.timedelta(seconds = 600)
    
    init_im_params = {'tau_time':300,
                      'freq_eff':140e6,
                      'freq_bw':2e6,
                      'taustart_ts':starttime,
                      'url':"someurl"}
    
    im_params=[]
    for i in range(n_images):
        im_params.append(init_im_params.copy())
        init_im_params['taustart_ts']+=time_spacing
    
    return im_params

def example_extractedsource_tuple(ra=123.123, dec=10.5, 
                                  ra_err=5./3600, dec_err=6./3600, 
                                  peak = 15e-3, peak_err = 5e-4, 
                                  flux = 15e-3, flux_err = 5e-4,
                                  sigma = 15,
                                  beam_maj = 100, beam_min = 100, 
                                  beam_angle = 45):
    # NOTE: ra_err & dec_err are in degrees (they are converted to arcsec in the db)
    return ExtractedSourceTuple(ra=ra, dec=dec, ra_err=ra_err, dec_err=dec_err, 
                                peak = peak, peak_err = peak_err, 
                                flux = flux, flux_err = flux_err,
                                sigma = sigma,
                                beam_maj = beam_maj, beam_min = beam_min, 
                                beam_angle = beam_angle
                               )
    
def example_source_lists(n_images, include_non_detections):
    assert n_images >= 7
    FixedSource = example_extractedsource_tuple()            
    SlowTransient1 = FixedSource._replace(ra=123.888,
                                  peak = 5e-3, 
                                  flux = 5e-3,
                                  sigma = 4,
                                  )
    SlowTransient2 = SlowTransient1._replace(sigma = 3)    
    
    BrightFastTransient = FixedSource._replace(dec=15.666,
                                    peak = 30e-3,
                                    flux = 30e-3, 
                                    sigma = 15,
                                  )
    
    WeakFastTransient = FixedSource._replace(dec=15.777,
                                    peak = 10e-3,
                                    flux = 10e-3, 
                                    sigma = 5,
                                  )
    source_lists=[]
    for i in xrange(n_images):
        source_lists.append([FixedSource])
    
    source_lists[3].append(BrightFastTransient)
    source_lists[4].append(WeakFastTransient)        
    source_lists[5].append(SlowTransient1)
    source_lists[6].append(SlowTransient2)
    
    if include_non_detections:
        #nd_sigma = 0.0
        nd_sigma = 0.01 #Workaround for issue 3532
        # https://support.astron.nl/lofar_issuetracker/issues/3532
        for sl in source_lists[:5]+source_lists[7:]:
            sl.append(SlowTransient1._replace(peak=0,
                                               flux=0, 
                                               sigma=nd_sigma))
        for sl in source_lists[:3]+source_lists[4:]:
            sl.append(BrightFastTransient._replace(peak=0,
                                                   flux=0, 
                                                   sigma=nd_sigma))
        for sl in source_lists[:4]+source_lists[5:]:
            sl.append(WeakFastTransient._replace(peak=0,
                                                   flux=0, 
                                                   sigma=nd_sigma))
    
#    print "Source list lengths:"
#    print ", ".join([str(len(l)) for l in source_lists])
         
    return source_lists
    
    
    
    
