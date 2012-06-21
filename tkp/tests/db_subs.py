import os
from tkp.config import config as tkp_conf
import datetime

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

def example_extractedsource_tuple():
    return ExtractedSourceTuple(ra=123.123, dec=10.5,
                                  ra_err=0.1, dec_err=0.1,
                                  peak = 15e-3, peak_err = 5e-4,
                                  flux = 15e-3, flux_err = 5e-4,
                                  sigma = 15,
                                  beam_maj = 100, beam_min = 100,
                                  beam_angle = 45
                                  )