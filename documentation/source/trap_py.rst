Example files
=============


trap.cfg
--------

Below is the pipeline configuration for the TRAP on heastro1::

    [DEFAULT]
    runtime_directory = /home/evert/work/trap
    recipe_directories = [/zfs/heastro-plex/scratch/evert/svn/tkp/code/pipe/recipes/, /opt/pipeline/recipes/]
    lofarroot = /opt/LofIm/lofar-2011-02-02
    default_working_directory = /zfs/heastro-plex/scratch/evert/trap
    task_files = [%(cwd)s/tasks.cfg]
    
    [layout]
    job_directory = %(runtime_directory)s/jobs/%(job_name)s
    log_directory = %(job_directory)s/logs/%(start_time)s
    vds_directory = %(job_directory)s/vds
    parset_directory = %(job_directory)s/parsets
    results_directory = %(job_directory)s/results/%(start_time)s
    
    [cluster]
    clusterdesc = /home/evert/work/cdesc/heastro1.cdesc
    task_furl = %(runtime_directory)s/task.furl
    multiengine_furl = %(runtime_directory)s/multiengine.furl
    
    [deploy]
    engine_ppath = /opt/tkp/tkp/lib/python2.6/site-packages:/opt/LofIm/lofar/lib/python2.6/dist-packages:/opt/monetdb/lib/python2.6/site-packages:/opt/pipeline/framework/lib/python2.6/site-packages
    engine_lpath = /opt/LofIm/lofar/lib:/usr/local/lib:/opt/tkp/tkp/lib
    
    [logging]
    log_file = %(runtime_directory)s/jobs/%(job_name)s/logs/%(start_time)s/pipeline.log
    format = %(asctime)s %(levelname)-7s %(name)s: %(message)s
    datefmt = %Y-%m-%d %H:%M:%S
    
    [database]
    # TKP database login details
    hostname = heastro1
    database = classification
    username = classification
    password = classification


trap.py
-------

This section shows the source code for trap.py (leaving out the import
statements), the main recipe that runs the TRAP. It is dotted with a
bit more comments than the actual file, to show where you can comment
out parts as to run only sections. The full script runs and end-to-end
pipeline, including time-slicing a dataset and matching between images
from those time slices.


::

    class SIP(control):
        def pipeline_logic(self):
            # Read the datafiles; datafiles is a list of MS paths.
            from to_process import datafiles
            
            with log_time(self.logger):
                # generate a mapfile, mapping the datafiles to compute nodes
                # with this and the previous step done, you can start anywhere in the TRAP
                storage_mapfile = self.run_task("datamapper_storage", datafiles)['mapfile']
                self.logger.info('storage mapfile = %s' % storage_mapfile)
    
                # Produce a GVDS file describing the data on the storage nodes.
                # The VDS file is used by to obtain the RA and Dec to createa sky model later.
                self.run_task('vdsmaker', storage_mapfile)
                
                # Read metadata (start, end times, pointing direction) from GVDS.
                vdsinfo = self.run_task("vdsreader")
                
                # NDPPP reads the data from the storage nodes, according to the
                # map. It returns a new map, describing the location of data on
                # the compute nodes.
                ndppp_results = self.run_task(
                    "ndppp",
                    storage_mapfile,
                )            
                # Use the new mapfile
                compute_mapfile = ndppp_results['mapfile']
                
                # Create a BBS skymodel file, using the catalogs in the database, 
 		# filling in the pointing information from the VDS files.
                ra = quantity(vdsinfo['pointing']['ra']).get_value('deg')
                dec = quantity(vdsinfo['pointing']['dec']).get_value('deg')
                central = self.run_task(
                    "skymodel", ra=ra, dec=dec, search_size=2.5
                    )
                
                # Patch the name of the central source into the BBS parset for
                # subtraction.
                with patched_parset(
                    self.task_definitions.get("bbs", "parset"),
                    {
                    'Step.correct.Model.Sources': '[ "%s" ]' % (central["source_name"]),
                    'Step.solve1.Model.Sources': '[ "%s" ]' % (central["source_name"]),
                    'Step.solve2.Model.Sources': '[ "%s" ]' % (central["source_name"]),
                    'Step.subtract.Model.Sources': '[ "%s" ]' % (central["source_name"])
                    }
                    ) as bbs_parset:
                    self.logger.info("bbs patched parset = %s" % bbs_parset)
                    # BBS modifies data in place, so the map produced by NDPPP
                    # remains valid.
                    self.run_task("bbs", compute_mapfile, parset=bbs_parset)
    
                # rerun DPPP on calibrated data
     		# the compute file hasn't changed (BBS doesn't create new files).
                ndppp_results = self.run_task(
                    "ndppp2",
                    compute_mapfile,
                )            
                # Get a new compute file for the newly flagged MS files
                compute_mapfile = ndppp_results['mapfile']
                self.logger.info("compute mapfile = %s" % compute_mapfile)

                # Produce a GVDS file describing the data on the storage nodes.
                gvds_file = self.run_task('vdsmaker', compute_mapfile)['gvds']
                self.logger.info("GVDS file = %s" % gvds_file)

		# slice the MS sets into time sections. views through
                # the MS are created in subdirectories in the node
                # working directories.
                outputs = self.run_task("time_slicing", gvds_file=gvds_file)
                mapfiles = outputs['mapfiles']
                subdirs = ["%d" % int(starttime) for starttime, endtime in
                           outputs['timesteps']]

 		# set the dataset_id to None, so a new dataset_id will be 
		# created in the database. Do this before the iteration starts
                dataset_id = None
                for iteration, (mapfile, subdir) in enumerate(zip(mapfiles,
                                                                subdirs)):
                    self.logger.info("Starting time slice iteration #%d" %
                                     (iteration+1,))
                    outputs = {}
		    # Set a results_dir that includes the time-sliced subdir name
                    results_dir = os.path.join(
                        self.config.get('DEFAULT', 'default_working_directory'),
                        self.inputs['job_name'],
                        subdir
                        )
		    # Run the cimager on the sliced data
                    outputs = self.run_task('cimager_trap', mapfile,
                                            vds_dir=os.path.dirname(mapfile),
                                            results_dir=results_dir)
                    # Convert the resulting CASA image to FITS, and combine images
                    outputs.update(
                        self.run_task('img2fits', images=outputs['images'],
                            results_dir=os.path.join(
                                self.config.get('layout', 'results_directory'),
                                subdir))
                        )
    
		    # Find sources in the combined image, and store them in the
		    # database
                    outputs.update(
                        self.run_task("source_extraction",
                                      images=outputs['combined_fitsfile'],
                                      dataset_id=dataset_id)
                        )
                    # Make sure we have the dataset ID throughout this loop
		    # for association purpoes
                    if dataset_id is None:
                        dataset_id = outputs['dataset_id']
		    # Set up the database loging credentials
                    dblogin = dict([(key, self.config.get('database', key))
                                    for key in ('database', 'username', 'password',
                                                'hostname')])
                    with closing(tkpdb.connection(**dblogin)) as dbconnection:
		        # Do a search for transients (inside the database)
                        outputs.update(
                            self.run_task("transient_search", [],
                                          dataset_id=dataset_id,
                                          dbconnection=dbconnection)
                            )
    			# Extract features from all found transients
                        outputs.update(
                            self.run_task("feature_extraction", [],
                                          transients=outputs['transients'],
                                          # transient_ids=outputs['transient_ids'],
                                          dblogin=dblogin,  # for the compute nodes
                                          dbconnection=dbconnection)
                            )
    
                        # run the manual classification on the transient objects
                        outputs.update(
                            self.run_task("classification", [],
                                          transients=outputs['transients'],
                                          dbconnection=dbconnection)
                            )
    
                    self.logger.info("outputs = %s " % str(outputs))
                    # Pretty print the found transients and classifications
                    self.run_task("prettyprint", [], transients=outputs['transients'])



tasks.cfg
---------

The tasks.cfg file gives the set up of the tasks run in the above trap.py; you can't use trap.py without a tasks file. 

::

    [datamapper_storage]
    recipe = datamapper_heastro
    mapfile = %(runtime_directory)s/jobs/%(job_name)s/parsets/storage_mapfile
    
    [datamapper_compute]
    recipe = datamapper_heastro
    mapfile = %(runtime_directory)s/jobs/%(job_name)s/parsets/compute_mapfile
    
    [ndppp]
    recipe = new_dppp
    executable = %(lofarroot)s/bin/NDPPP
    initscript = %(lofarroot)s/lofarinit.sh
    working_directory = %(default_working_directory)s
    dry_run = False
    mapfile = %(runtime_directory)s/jobs/%(job_name)s/parsets/compute_mapfile
    parset = %(runtime_directory)s/jobs/%(job_name)s/parsets/ndppp.1.parset
    nproc = 4
    
    # This ndppp gets ran after the calibration
    [ndppp2]
    recipe = new_dppp
    executable = %(lofarroot)s/bin/NDPPP
    initscript = %(lofarroot)s/lofarinit.sh
    working_directory = %(default_working_directory)s
    dry_run = False
    mapfile = %(runtime_directory)s/jobs/%(job_name)s/parsets/compute_mapfile
    parset = %(runtime_directory)s/jobs/%(job_name)s/parsets/ndppp.2.parset
    nproc = 4
    
    
    [bbs]
    recipe = bbs
    initscript = %(lofarroot)s/lofarinit.sh
    control_exec = %(lofarroot)s/bin/GlobalControl
    kernel_exec = %(lofarroot)s/bin/KernelControl
    parset = %(runtime_directory)s/jobs/%(job_name)s/parsets/bbs.parset
    key = bbs_%(job_name)s
    db_host = 146.50.10.202
    #db_host = localhost
    db_name = evert
    db_user = postgres
    makevds = %(lofarroot)s/bin/makevds
    combinevds = %(lofarroot)s/bin/combinevds
    makesourcedb = %(lofarroot)s/bin/makesourcedb
    parmdbm = %(lofarroot)s/bin/parmdbm
    skymodel = %(runtime_directory)s/jobs/%(job_name)s/parsets/bbs.skymodel
    nproc = 4
    
    [vdsreader]
    recipe = vdsreader
    gvds = %(runtime_directory)s/jobs/%(job_name)s/vds/%(job_name)s.gvds
    
    [parmdb]
    recipe = parmdb
    executable = %(lofarroot)s/bin/parmdbm
    
    [sourcedb]
    recipe = sourcedb
    executable = %(lofarroot)s/bin/makesourcedb
    skymodel = %(runtime_directory)s/jobs/%(job_name)s/parsets/bbs.skymodel
    
    [skymodel]
    recipe = skymodel
    min_flux = 1.
    skymodel_file = %(runtime_directory)s/jobs/%(job_name)s/parsets/bbs.skymodel
    search_size = 2.
    db_host = 146.50.10.202
    db_dbase = classification
    db_user = classification
    db_password = classification
    
    [time_slicing]
    recipe = time_slicing
    interval = 2:00:00
    gvds_file = %(runtime_directory)s/jobs/%(job_name)s/vds/cimager.gvds
    mapfiledir = %(runtime_directory)s/jobs/%(job_name)s/vds/
    
    [vdsmaker]
    recipe = new_vdsmaker
    directory = %(runtime_directory)s/jobs/%(job_name)s/vds
    gvds = %(runtime_directory)s/jobs/%(job_name)s/vds/%(job_name)s.gvds
    makevds = %(lofarroot)s/bin/makevds
    combinevds = %(lofarroot)s/bin/combinevds
    unlink = False
    
    [cimager_trap]
    recipe = cimager_trap
    imager_exec = /opt/LofIm/lofar/bin/cimager
    #imager_exec = /opt/LofIm/askapsoft/bin/cimager.sh
    convert_exec = /opt/LofIm/lofar/bin/convertimagerparset
    parset = %(runtime_directory)s/jobs/%(job_name)s/parsets/mwimager.parset
    parset_type = mwimager
    makevds = /opt/LofIm/lofar/bin/makevds
    combinevds = /opt/LofIm/lofar/bin/combinevds
    #results_dir = %(runtime_directory)s/jobs/%(job_name)s/results/
    
    [img2fits]
    recipe = img2fits
    
    [source_extraction]
    recipe = source_extraction
    detection_level = 3.
    radius = 5.
    
    [transient_search]
    recipe = transient_search
    detection_level = 1e6
    closeness_level = 3
    
    [feature_extraction]
    recipe = feature_extraction
    
    [classification]
    recipe = classification
    #schema = /home/evert/work/trap/jobs/A/parsets/classification.xml
    schema = classification
    weight_cutoff = 0.1
    
    [prettyprint]
    recipe = prettyprint
