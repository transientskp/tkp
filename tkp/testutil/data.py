import os
import tkp.config

DATAPATH = tkp.config.config['test']['datapath']

# A arbitrary fits file which can be used for playing around
fits_file = os.path.join(DATAPATH,
    'quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band6.corr.fits')

# A arbitrary casa table which can be used for playing around
casa_table = os.path.join(DATAPATH,
'casatable/L55614_020TO029_skymodellsc_wmax6000_noise_mult10_cell40_npix512_wplanes215.img.restored.corr')
