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
fits_file = os.path.join(DATAPATH, "sourcefinder/NCP_sample_image_1.fits")

job_template_dir = os.path.join(tkp.__path__[0], 'config/job_template')
default_job_config = os.path.join(job_template_dir, 'job_params.cfg')
default_header_inject_config = os.path.join(job_template_dir, 'inject.cfg')

project_template_dir = os.path.join(tkp.__path__[0], 'config/project_template')
default_pipeline_config = os.path.join(project_template_dir, 'pipeline.cfg')
