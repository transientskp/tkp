import os
import warnings
import glob
import tkp


HERE = os.path.dirname(__file__)
DEFAULT = os.path.abspath(os.path.join(HERE, '../../tests/data'))
DATAPATH = os.environ.get('TKP_TESTPATH', DEFAULT)

if not os.access(DATAPATH, os.X_OK):
    warnings.warn("can't access " + DATAPATH)

# A arbitrary fits file which can be used for playing around
fits_file = os.path.join(DATAPATH,
    'quality/noise/bad/home-pcarrol-msss-3C196a-analysis-band6.corr.fits')

# A arbitrary casa table which can be used for playing around
casa_table = os.path.join(DATAPATH,
'casatable/L55614_020TO029_skymodellsc_wmax6000_noise_mult10_cell40_npix512_wplanes215.img.restored.corr')

job_template_dir = os.path.join(tkp.__path__[0], 'config/job_template')
default_job_config = os.path.join(job_template_dir, 'job_params.cfg')
default_header_inject_config = os.path.join(job_template_dir, 'inject.cfg')

project_template_dir = os.path.join(tkp.__path__[0], 'config/project_template')
default_pipeline_config = os.path.join(project_template_dir, 'pipeline.cfg')
