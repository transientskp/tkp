#! /usr/bin/env python


import sys
import os
import getpass
import socket
import ConfigParser
import shutil
import logging


#logging.basicConfig(level=logging.INFO,
#                    format="%(message)s",
#                    stream=sys.stdout)


class ConfigError(Exception):
    pass


def ask(question, default='y', options=(('y', ('yes', 'y')), ('n', ('no', 'n'))),
        unique_shorten=True, case_insensitive=True, repeats=-1):
    options_string = "/".join([option[1][0] for option in options])
    for option in options:
        if option[0] == default:
            default_answer = option[1][0]
    if default is not None:
        question = "%s (%s)? " % (question.rstrip('?'),
                                  options_string.replace(default_answer,
                                                         default_answer.upper()))
    else:
        question = question.rstrip('?') + "? "
    while repeats:
        result = ''
        answer = raw_input(question).strip()
        if not options:
            result = answer
        elif answer == '':
            result = default
        else:
            if case_insensitive:
                answer = answer.lower()
            if unique_shorten:
                tmpoptions = options
                remaining_options = []
                for option, option_texts in tmpoptions:
                    done = False
                    for text in option_texts:
                        if text.startswith(answer):
                            remaining_options.append((option, option_texts))
                            done = True
                            break
                if len(remaining_options) > 1:
                    # Too many valid answers
                    tmpoptions = tuple(remaining_options)
                elif not remaining_options:   # no valid answer
                    pass
                else:
                    result = remaining_options[0][0]
            else:
                for option, option_texts in options:
                    for text in option_texts:
                        if answer == text:
                            result = option
                            break
                    if result:
                        break
        if not result:
            if repeats == 1:
                raise ValueError("No valid answer")
            print "Please choose from: %s" % options_string
            if repeats < 0:
                continue
            repeats -= 1
        else:
            break
    return result


def ask_and_create_directory(dir, message=None, logger=None):
    if logger is None:
        logger = logging.getLogger('trapinit')
    #if message:
    #    logger.info(message)
    if message:
        message = "%s (%s)? " % (message.rstrip('?'), dir)
        path = raw_input(message).strip()
        if path == '':
            path = dir
    else:
        path = dir
    if not os.path.exists(path):
        logger.warning("Directory %s does not exist.", path)
        if ask("Create directory") == 'y':
            try:
                os.makedirs(path)
            except OSerror as exc:
                logger.error("Failed to create directory %s: %s",
                              path, str(exc))
                raise ConfigError(
                    "failed to create directory %s: %s" % (path, str(exc)))
    return path


class Setup(object):
    """
    Main class that takes care of all the separate steps.

    The __init__() method scans the environment, after which the run()
    method will take care of the user interaction to set up the rest.

    """

    def __init__(self, *args, **kwargs):
        """Scan the environment for a default setup"""

        self.logger = logging.getLogger('trapinit')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)
        self.logger.info("Determining default setup")
        self.logger.info("")
        self.files_created = {}
        self.config = self.setup_config()
        super(Setup, self).__init__(*args, **kwargs)

    def setup_config(self):
        """Determine the host, and from that deduce some default options"""
    
        config = {}
        user = getpass.getuser()
        name = socket.gethostname()
        homedir = os.path.expanduser('~')
        config['hostname'] = name
        config['user'] = user
        config['default-dirs'] = {'home': homedir}
        if name in ('heastro1', 'heastro2'):
            tkp_base = '/opt/tkp/dev/tkp'
            lofim_base = '/opt/LofIm/lofar'
            config['database'] = {
                'host': 'heastro1',
                'name': 'tkpdev',
                'user': 'tkpdev',
                'password': 'tkpdev',
                }
            config['default-dirs'].update({
                'tkp': {'base': tkp_base,
                        'lib': os.path.join(tkp_base, 'lib'),
                        'python': os.path.join(tkp_base, 'lib/python'),
                        'bin': os.path.join(tkp_base, 'bin')},
                'trap': {'recipes': os.path.join(tkp_base, 'recipes')},
                'database': {'base': os.path.join(tkp_base, 'database')},
                'lofim': {'base': lofim_base,
                        'lib': os.path.join(lofim_base, 'lib/python'),
                        'python': os.path.join(lofim_base, 'lib/python2.6/dist-packages'),
                        'bin': os.path.join(lofim_base, 'bin')},
                'monetdb': {'python': '/opt/monetdb/lib/python2.6/site-packages'},
                'sip': {'recipes': '/opt/pipeline/recipes',
                        'python':
                        '/opt/pipeline/framework/lib/python2.6/site-packages'},
                'work': '/zfs/heastro-plex/scratch/%s/trap' % user,
                'archive': '/zfs/heastro-plex/archive',
                'pipeline-runtime': os.path.join(homedir, 'pipeline-runtime'),
                'jobs': os.path.join(homedir, 'pipeline-runtime', 'jobs'),
                })
            config['cdesc'] = 'heastro.clusterdesc'
            config['sipcfg'] = 'sip.cfg'
            config['postgres'] = {'host': '146.50.10.202'}
        return config
                        
    def create_minimal_tkp_configfile(self, path):
        """Write a minimal .tkp.cfg file"""
        
        with open(path, 'w') as outfile:
            outfile.write("""\
[database]
enabled = True
host = %s
name = %s
user = %s
password = %s
""" % (self.config['database']['host'],
       self.config['database']['hostname'],       
       self.config['database']['user'],
       self.config['database']['password']))
            self.files_created['tkpconfig'] = path

    def check_tkp_configfile(self):
        homedir = self.config['default-dirs']['home']
        path = os.path.join(homedir, '.tkp.cfg')
        try:
            open(path)
        except IOError as exc:
            self.logger.warning("Can't read the TKP config file at %s", path)
            if ask("Create a minimal TKP config file") == 'y':
                # Could use the config creation method in tkp.config,
                # but that may create a config file that could confuse the
                # user, since it's abundant in its options
                create_minimal_tkp_configfile(path, self.config)
        tkpconfig = ConfigParser.SafeConfigParser()
        tkpconfig.read(os.path.expanduser('~/.tkp.cfg'))
        if not tkpconfig.has_section('database'):
            self.logger.info("[database] section missing in %s. "
                        "Please add and then rerun this script", path)
            raise ConfigError("database section missing")
        for option in ('enabled', 'host', 'name', 'user', 'password'):
            if not tkpconfig.has_option('database', option):
                self.logger.info("[database] section is missing option %s in %s. "
                            "Please add and then rerun this script", option, path)
                raise ConfigError("missing database option")
        if not tkpconfig.getboolean('database', 'enabled'):
            self.logger.error("Database is not enabled in %s. "
                         "Please enable the database and then rerun this script", path)
            raise ConfigError("database not enabled")

    def verify_tkp_modules(self):
        self.logger.info("Checking modules")
        for module in ('tkp', 'tkp.database', 'tkp.database.database',
                       'tkp.database.dataset', 'tkp.database.utils',
                       'tkp.sourcefinder', 'tkp.sourcefinder.extract',
                       'tkp.sourcefinder.image', 'tkp.sourcefinder.gaussian',
                       'tkp.sourcefinder.stats', 'tkp.sourcefinder.utils',
                       'tkp.utility', 'tkp.utility.accessors',
                       'tkp.utility.containers', 'tkp.utility.coordinates',
                       'tkp.utility.fits', 'tkp.utility.memoize',
                       'tkp.utility.sigmaclip', 'tkp.utility.uncertain'):
            try:
                __import__(module)
            except ImportError:
                self.logger.error("TKP module %s could not be loaded."
                             "Please check and try again", module)
                raise

    def verify_database(self):
        try:
            import monetdb
        except ImportError as exc:
            self.logger.error("MonetDB Python can't be imported: %s\n", str(exc))
            raise
        from tkp.database.database import DataBase
        try:
            database = DataBase()
        except Exception as exc:
            self.logger.error("Error connecting to the database: %s\n", str(exc))
            raise ConfigError("error connecting to the database: %s\n" % str(exc))
    
    
    
    def show_config(self):
        dirs = self.config['default-dirs']
        self.logger.info("")
        self.logger.info("The following setup has been detected on the system:")
        self.logger.info("TKP / TRAP main directory:        %s", dirs['tkp']['base'])
        self.logger.info("Database (MonetDB) python module: %s", dirs['monetdb']['python'])
        self.logger.info("Pipeline framework:               %s", dirs['sip']['python'])
        self.logger.info("LofIm main directory:             %s", dirs['lofim']['base'])
        self.logger.info("Working (scratch) data directory: %s", dirs['work'])
    
    
    def check_tkp_installation(self):
        try:
            self.check_tkp_configfile()
        except ConfigError:
            return 1
        dirs = self.config['default-dirs']
        sys.path.append(dirs['tkp']['python'])
        sys.path.append(dirs['monetdb']['python'])
        #sys.path.append(dirs['lofim']['python'])
        #sys.path.append(dirs['sip']['python'])
        try:
            self.verify_tkp_modules()
        except ImportError:
            return 2
    
    
    def check_database(self):
        try:
            self.verify_database()
        except ImportError, ConfigError:
            return 3
    
    
    def create_dirs(self):
        dirs = self.config['default-dirs']
        try:
            dirs['pipeline-runtime'] = ask_and_create_directory(
                dirs['pipeline-runtime'], "Enter the pipeline runtime directory")
            dirs['jobs'] = os.path.join(dirs['pipeline-runtime'], 'jobs')
            ask_and_create_directory(dirs['jobs'])
            dirs['work'] = ask_and_create_directory(
                dirs['work'], "Enter the working scratch directory")
        except ConfigError as exc:
            return 4
        self.config['default-dirs'] = dirs
        return 0
    
    
    def create_clusterdescription(self, path, host):
        if host == 'heastro':
            with open(path, 'w') as outfile:
                outfile.write("""\
    ClusterName = heastro
    
    Compute.Nodes = [ heastro1,heastro2 ]
    Compute.LocalDisks = [ /zfs/heastro-plex ]
    """)
        self.files_created['clusterdesc'] = path
        
    def check_clusterdescription(self):
        if not os.path.exists(self.config['cdesc']):
            self.logger.warning("No cluster description file detected")
            if ask("Would you like to have a default one created") == 'y':
                if self.config['hostname'].startswith('heastro'):
                    self.create_clusterdescription(self.config['cdesc'], 'heastro')
                self.logger.info("Created default cluster description file %s",
                             self.config['cdesc'])
    
    
    def create_sipcfg(self, path, host):
        dirs = self.config['default-dirs']
        if host == 'heastro':
            with open(path, 'w') as outfile:
                outfile.write("""\
[DEFAULT]
runtime_directory = %s
recipe_directories = [%s, %s]
lofarroot = /opt/LofIm/lofar
lofarroot = %s
default_working_directory = /zfs/heastro-plex/scratch/evert/trap
default_working_directory = %s
task_files = [%%(cwd)s/tasks.cfg]

[layout]
job_directory = %%(runtime_directory)s/jobs/%%(job_name)s
log_directory = %%(job_directory)s/logs/%%(start_time)s
vds_directory = %%(job_directory)s/vds
parset_directory = %%(job_directory)s/parsets
results_directory = %%(job_directory)s/results/%%(start_time)s

[cluster]
clusterdesc = %s

[deploy]
engine_ppath = %s:%s:%s:%s
engine_lpath = %s:%s:/usr/local/lib

[logging]
log_file = %%(runtime_directory)s/jobs/%%(job_name)s/logs/%%(start_time)s/pipeline.log
format = %%(asctime)s %%(levelname)-7s %%(name)s: %%(message)s
datefmt = %%Y-%%m-%%d %%H:%%M:%%S
""" % (dirs['pipeline-runtime'], dirs['trap']['recipes'], dirs['sip']['recipes'],
       dirs['lofim']['base'], dirs['work'], self.config['cdesc'],
       dirs['tkp']['python'], dirs['lofim']['python'], dirs['monetdb']['python'],
       dirs['sip']['python'], dirs['tkp']['lib'], dirs['lofim']['lib']))
        self.files_created['trap.cfg'] = path

    def check_sipcfg(self):
        if not os.path.exists(self.config['sipcfg']):
            self.logger.warning("No SIP configuration file detected")
            if ask("Would you like to have a default one created") == 'y':
                if self.config['hostname'].startswith('heastro'):
                    self.create_sipcfg(self.config['sipcfg'], 'heastro')
                self.logger.info("Created default SIP configuration file %s",
                             self.config['sipcfg'])
    
    
    def create_job_layout(self):
        dirs = self.config['default-dirs']
        jobdir = os.path.join(dirs['jobs'], self.config['dsname'])
        if os.path.exists(jobdir):
            self.logger.warning("Directory %s already exists. Skipping.", jobdir)
            return -1
        try:
            os.makedirs(jobdir)
        except OSError:
            pass
        for subdir in ('control', 'parsets', 'vds', 'logs', 'results'):
            try:
                os.makedirs(os.path.join(jobdir, subdir))
            except OSError:
                pass
        return 0
                        
    
    def setup_control_dir(self):
        dirs = self.config['default-dirs']
        controldir = os.path.join(dirs['jobs'], self.config['dsname'], 'control')
        shutil.copy(os.path.join(dirs['trap']['recipes'], 'trap-with-trip.py'),
                    controldir)
        # runtrap.sh file
        with open(os.path.join(controldir, 'runtrap.sh'), 'w') as outfile:
            outfile.write("""\
#! /bin/sh

# Uncomment the following four lines if you want to remove old stuff
# Only do this automatically when testing
#rm -r %s/*
#rm -r %s/*
#rm -r %s/*
#rm %s

CONTROLDIR=%s
# Note! The next command spans 3 lines
PYTHONPATH=%s:%s:%s:%s \\
LD_LIBRARY_PATH=%s:%s \\
python ${CONTROLDIR}/trap-with-trip.py -d --task-file=${CONTROLDIR}/tasks.cfg -j %s -c %s $1
""" % (os.path.join(dirs['work'], self.config['dsname']), 
       os.path.join(controldir, 'vds'),
       os.path.join(controldir, 'results'),
       os.path.join(dirs['jobs'], self.config['dsname'], 'statefile'),
       controldir,
       dirs['tkp']['python'], dirs['lofim']['python'],
       dirs['monetdb']['python'], dirs['sip']['python'],
       dirs['tkp']['lib'], dirs['lofim']['lib'],
       self.config['dsname'], self.config['sipcfg']))
        self.files_created['runtrap.sh'] = os.path.join(controldir, 'runtrap.sh')
        # tasks.cfg file
        with open(os.path.join(controldir, 'tasks.cfg'), 'w') as outfile:
            outfile.write("""\
[datamapper_storage]
recipe = datamapper_heastro
mapfile = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/storage_mapfile

[datamapper_compute]
recipe = datamapper_heastro
mapfile = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/compute_mapfile

[ndppp]
recipe = new_dppp
executable = %%(lofarroot)s/bin/NDPPP
initscript = %%(lofarroot)s/lofarinit.sh
working_directory = %%(default_working_directory)s
dry_run = False
mapfile = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/compute_mapfile
parset = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/ndppp.1.parset
nproc = 1

# This ndppp gets ran after the calibration
[ndppp2]
recipe = new_dppp
executable = %%(lofarroot)s/bin/NDPPP
initscript = %%(lofarroot)s/lofarinit.sh
working_directory = %%(default_working_directory)s
dry_run = False
mapfile = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/compute_mapfile
parset = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/ndppp.2.parset
nproc = 1


[bbs]
recipe = bbs
initscript = %%(lofarroot)s/lofarinit.sh
control_exec = %%(lofarroot)s/bin/GlobalControl
kernel_exec = %%(lofarroot)s/bin/KernelControl
parset = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/bbs.parset
key = bbs_%%(job_name)s
db_host = %s
db_name = %s
db_user = postgres
makevds = %%(lofarroot)s/bin/makevds
combinevds = %%(lofarroot)s/bin/combinevds
makesourcedb = %%(lofarroot)s/bin/makesourcedb
parmdbm = %%(lofarroot)s/bin/parmdbm
skymodel = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/bbs.skymodel
nproc = 1

[vdsreader]
recipe = vdsreader
gvds = %%(runtime_directory)s/jobs/%%(job_name)s/vds/%%(job_name)s.gvds

[parmdb]
recipe = parmdb
executable = %%(lofarroot)s/bin/parmdbm

[sourcedb]
recipe = sourcedb
executable = %%(lofarroot)s/bin/makesourcedb
skymodel = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/bbs.skymodel

[skymodel]
recipe = skymodel
min_flux = 1.
skymodel_file = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/bbs.skymodel
search_size = 2.

[time_slicing]
recipe = time_slicing
interval = 12:00:00
gvds_file = %%(runtime_directory)s/jobs/%%(job_name)s/vds/cimager.gvds
mapfiledir = %%(runtime_directory)s/jobs/%%(job_name)s/vds/

[vdsmaker]
recipe = new_vdsmaker
directory = %%(runtime_directory)s/jobs/%%(job_name)s/vds
gvds = %%(runtime_directory)s/jobs/%%(job_name)s/vds/%%(job_name)s.gvds
makevds = %%(lofarroot)s/bin/makevds
combinevds = %%(lofarroot)s/bin/combinevds
unlink = False

[cimager_trap]
recipe = cimager_trap
imager_exec = /opt/LofIm/lofar/bin/cimager
#imager_exec = /opt/LofIm/askapsoft/bin/cimager.sh
convert_exec = /opt/LofIm/lofar/bin/convertimagerparset
parset = %%(runtime_directory)s/jobs/%%(job_name)s/parsets/mwimager.parset
parset_type = mwimager
makevds = /opt/LofIm/lofar/bin/makevds
combinevds = /opt/LofIm/lofar/bin/combinevds
#results_dir = %%(runtime_directory)s/jobs/%%(job_name)s/results/

[img2fits]
recipe = img2fits

[source_extraction]
recipe = source_extraction
detection_level = 10.
radius = 3.

[transient_search]
recipe = transient_search
detection_level = 1e6
closeness_level = 3

[feature_extraction]
recipe = feature_extraction

[classification]
recipe = classification
schema = classification
weight_cutoff = 0.1

[prettyprint]
recipe = prettyprint
""" % (self.config['postgres']['host'],
       self.config['user']))
        self.files_created['tasks.cfg'] = os.path.join(controldir, 'tasks.cfg')

        

    def create_default_parsets(self):
        dirs = self.config['default-dirs']
        parsetdir = os.path.join(dirs['jobs'], self.config['dsname'], 'parsets')
        with open(os.path.join(parsetdir, 'ndppp.1.parset'), 'w') as outfile:
            outfile.write("""\
# Adjusted for 16 channel data
uselogger = True
msin.startchan = 0
msin.nchan = 1
msin.datacolumn = DATA     # is the default
msout.datacolumn = DATA    # is the default
steps = [preflag, flag1, flag2, count]   # if defined as [] the MS will be copied and NaN/infinite will be  flagged
preflag.type=preflagger    # This step will flag the autocorrelations. Note that they are not flagged by default by NDPPP
preflag.corrtype=auto
flag1.type=madflagger
flag1.threshold=4
flag1.freqwindow=1
flag1.timewindow=5
flag1.correlations=[0,3]   # only flag on XX and YY
avg1.type = squash
avg1.freqstep = 16        # it compresses the data by a factor of 16 in frequency
avg1.timestep = 1          # is the default
flag2.type=madflagger
flag2.threshold=3
flag2.timewindow=51
avg2.type = squash
avg2.timestep = 1          #it compresses the data by a factor of 5 in time
count.type = counter
count.showfullyflagged = True
""")
        self.files_created['ndppp.1.parset'] = os.path.join(parsetdir, 'ndppp.1.parset')
        with open(os.path.join(parsetdir, 'ndppp.2.parset'), 'w') as outfile:
            outfile.write("""\
# Flag after calibration
uselogger = True
msin.startchan = 0
msin.nchan = 1
msin.datacolumn = CORRECTED_DATA
msout.datacolumn = DATA
steps = [flag1, count]   # if defined as [] the MS will be copied and NaN/infinite will be  flagged
flag1.type=madflagger
flag1.threshold=100
flag1.freqwindow=1
flag1.timewindow=5
flag1.correlations=[0,3]   # only flag on XX and YY
flag2.type=madflagger
flag2.threshold=3
flag2.timewindow=51
count.type = counter
count.showfullyflagged = True
""")

        self.files_created['ndppp.2.parset'] = os.path.join(parsetdir, 'ndppp.2.parset')
        with open(os.path.join(parsetdir, 'bbs.parset'), 'w') as outfile:
            outfile.write("""\
Strategy.InputColumn = DATA
Strategy.ChunkSize = 0
Strategy.Steps = [solve, correct]
Step.solve.Operation = SOLVE
Step.solve.Model.Gain.Enable = T
Step.solve.Model.Bandpass.Enable = F
Step.solve.Model.DirectionalGain.Enable = F
Step.solve.Model.Beam.Enable = F
Step.solve.Model.Ionosphere.Enable = F
Step.solve.Model.Cache.Enable = T
Step.solve.Solve.Parms = ["Gain:0:0:*","Gain:1:1:*"]
Step.solve.Solve.ExclParms = []
Step.solve.Solve.CellSize.Freq = 0
Step.solve.Solve.CellSize.Time = 5
Step.solve.Solve.CellChunkSize = 20
Step.solve.Solve.Options.MaxIter = 20
Step.solve.Solve.Options.EpsValue = 1e-9
Step.solve.Solve.Options.EpsDerivative = 1e-9
Step.solve.Solve.Options.ColFactor = 1e-9
Step.solve.Solve.Options.LMFactor = 1.0
Step.solve.Solve.Options.BalancedEqs = F
Step.solve.Solve.Options.UseSVD = T
Step.correct.Operation = CORRECT
Step.correct.Model.Gain.Enable = T
Step.correct.Output.Column = CORRECTED_DATA
Step.subtract.Operation = SUBTRACT
Step.subtract.Output.Column = SUBTRACTED_DATA
Step.subtract.Model.Sources = []
Step.subtract.Model.Gain.Enable = F
Step.subtract.Model.Beam.Enable = F
""")
        self.files_created['bbs.parset'] = os.path.join(parsetdir, 'bbs.parset')
        with open(os.path.join(parsetdir, 'mwimager.parset'), 'w') as outfile:
            outfile.write("""\
Images.stokes = [I]
Images.shape = [512, 512]
Images.cellSize = [20, 20]
Images.directionType = J2000
Solver.type = Dirty
Solver.algorithm = MultiScale
Solver.niter = 1.
Solver.gain = 1.0
Solver.verbose = True
Solver.scales = [0, 3]
Gridder.type = WProject
Gridder.wmax = 50000
Gridder.nwplanes = 51
Gridder.oversample = 1
Gridder.maxsupport = 256
Gridder.limitsupport = 0
Gridder.cutoff = 0.001
Gridder.nfacets = 1
datacolumn = DATA
minUV = 1.0
ncycles = 0
restore = True
restore_beam = [0.01, 0.01, 0]
""")
        self.files_created['mwimager.parset'] = os.path.join(parsetdir, 'mwimager.parset')

    def find_subbands(self):
        if self.config['hostname'].startswith('heastro'):
            archivedir = os.path.join(self.config['default-dirs']['archive'],
                                      self.config['dsname'])
            try:
                datafiles = sorted(os.listdir(archivedir))
            except OSError:
                self.logger.warning("Could not find data files; "
                               "creating an empty data file list")
                datafiles = []
        # we could dump it with str(datafiles), but let's do it nicely
        filename = os.path.join(self.config['default-dirs']['jobs'],
                               self.config['dsname'], 'control', 'ms_to_process.py')
        with open(filename, 'w') as outfile:
            outfile.write("datafiles = [\n")
            outfile.write(",\n".join(["    '%s'" % os.path.join(archivedir, datafile)
                                      for datafile in datafiles]))
            outfile.write("\n]\n")
            self.files_created['ms_to_process'] = filename

    def show_files_created(self):
        self.logger.info("")
        self.logger.info("The following files have been created.")
        self.logger.info("You may want to review and edit them:")
        for filename in self.files_created.values():
            self.logger.info("  %s", filename)
            
    def run(self):
        result = self.check_tkp_installation()
        if result:
            return result
        result = self.check_database()
        if result:
            return result
        self.show_config()
        self.logger.info("")
        result = self.create_dirs()
        if result:
            return result
        self.config['cdesc'] = os.path.join(self.config['default-dirs']['pipeline-runtime'], self.config['cdesc'])
        self.config['sipcfg'] = os.path.join(self.config['default-dirs']['pipeline-runtime'], self.config['sipcfg'])
        self.check_clusterdescription()
        self.check_sipcfg()
        if ask("Create a job directory structure for a new dataset") == 'y':
            self.config['dsname'] = ask("Dataset name", default=None, options=[])
            if self.create_job_layout() == 0:
                self.setup_control_dir()
                if ask("Create default parsets") == 'y':
                    self.create_default_parsets()
                if ask("Try to find subbands based on dataset name") == 'y':
                    self.find_subbands()
        if self.files_created:
            self.show_files_created()
        return 0


def main():
    setup = Setup()
    return setup.run()


if __name__ == '__main__':
    sys.exit(main())
