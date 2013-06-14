import os
import glob
import tkp
job_template_dir = os.path.join(tkp.__path__[0], 'conf/job_template')
default_parset_paths = dict([(os.path.basename(f), f) for f in
                            glob.glob(os.path.join(job_template_dir,
                                                   'parsets',
                                                   '*.parset'))])
