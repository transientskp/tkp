__author__ = 'gijs'
import os
import glob
from tkp.conf.job_template import __path__ as job_template_dir
job_template_dir = job_template_dir[0]
default_parset_paths = { os.path.basename(f): f
                        for f in glob.glob(os.path.join(job_template_dir, 'parsets', '*.parset')) }
