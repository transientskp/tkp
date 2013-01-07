import os
import tkp.config

DATAPATH = tkp.config.config['test']['datapath']

# A arbitrary fits file which can be used for playing around
fits_file = os.path.join(DATAPATH,
    'quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band6.corr.fits')