tkp-user-config
===============

Example pipeline invocation scripts and configuration files aimed at end users of the LOFAR-TKP software packages. The aim of this repository is to maintain an up to date, minimal and easily configurable working set.

I have attempted to layout the files and scripts in such a way that the user only ever needs one central set of files, with the exception of the parset (and data listing) files which probably *should* be job specific. Note that if you wish to use the same set of parsets for a whole bunch of data this is easy - just set the `default_parset_directory` in `pipeline.cfg` accordingly.

Likewise if you wish to use specific config (`pipeline.cfg`) or tasks files, you should simply edit the runblah.sh scripts. These are short and fairly self-explanatory, I leave the rest to you!


The .cfg files use the python configparser syntax. For details, see: <http://docs.python.org/library/configparser.html>.

Caveat Emptor
---
- This is currently a work in progress not really intended for end user consumption, e.g. the sip.py is full of old and ugly code.
- These config files and scripts are a good example of how to lay out your working system, but they are merely a starting point. 
To to properly utilise the pipline (and to do good science) you, the end user, *must* be aware of the pipeline inner workings, at least at the conceptual level [1].

Config
---

- Create your `pipeline-runtime` folder - this will be the parent directory where your jobs are stored; e.g. `/data/lofar-pipeline`

- Edit `pipeline.cfg` according to your setup, e.g. the `pipeline-runtime` directory location. Note that variables defined under the `[default]` section can be referenced throughout the rest of the config files, to save redefining locations over and over.

- You will likely also need to edit `sip-tasks.cfg`, specifically the entries:  
   - `subcluster = blah`    
    (under `[datamapper_storage]`)
    and  
   -  `db_host = blah`  
    (under `[bbs]`).  
    

- Lastly, the runX.sh scripts will need adjusting so that they pull in the correct set of pipeline initialisation scripts for your system.

Note that if you are using the Lofar software on a TKP system (e.g. those at UvA, Southampton) then there may already be a branch of the repository configured for your local setup.

Usage
---

- **Create a job directory** under `$PIPELINE_RUNTIME_DIR/jobs`, e.g.  
`/data/lofar-pipeline/jobs/GRB120422A`   
(more precisely, create it so it will match the location defined as your `job_directory` in `pipeline.cfg`, but this example fits the default settings.)

- **Copy job specific files to the job directory**, e.g. using   
'cp -r ${TKP\_USER\_CONF_DIR}/job-specific/sip/* /data/lofar-pipeline/jobs/GRB120922A' for an imaging run.

- **Edit** the `datafiles_to_process.py` and the parsets to your liking.

- `cd` to the job directory and **invoke** the pipeline like so:  
`bash $TKP_USER_CONF_DIR/runsip.sh -j GRB120922A`

- Scientific **fun and profit ensues**.

Details
---
- You may wish to keep your working files along with your results, in which case I recommend setting   
`working_directory = %(default_job_directory)s/working_dir`  
But otherwise it's much easier to keep them all in one easily deletable folder:    
`working_directory = %(runtime_directory)s/working_dir/%(job_name)s`


[1]: If in doubt, talk to John.



