
datamapper
----------

This recipe is part of the default pipeline framework.

Calculates a file that maps the datasets to their respective storage
or compute nodes and subclusters, so that the pipeline hands out the
correct jobs (with datafiles) to the correct nodes.

- inputs:
  
  - mapfile: the filename (full path) of the mapping file

  - subcluster (optional): is the subcluster name is not "encoded"
    inside the file name (that is, on CEP I the second directory in
    the path name contains the subcluster), set this option to
    indicate the subcluster you're using. This will likely be
    "heastro" or "lofar1".

- outputs:

  - the mapping filename. This is often used by the next recipe(s).

Important note: the datamapper recipe looks at the file path to
determine the node and subcluster. This only works on the LOFAR
Groningen offline cluster; for heastro1, there is a separate recipe
with a slight modification, so that heastro1 is always picked up as
the compute node.


vdsmaker
------------

This recipe is part of the default pipeline framework.

VDS files are another way to map files to their respective nodes; in
addition, VDS files store information like time and frequency range.

The vdsmaker recipe creates local and a global VDS file for the specified files.

- Inputs:

  - gvds: Global VDS output file name.

  - directory: the output directory (for the local individual VDS files).

  - makevds: the makevds executable

  - combinevds: the combinevds executable

  - unlink: remove the local individual VDS files are combining them
    into a GVDS file? By default this is set to True, but if you need
    the local VDS files in another recipe, set this is False.

  - nproc: maximum number of simultaneous processes per output node.

- outputs:

  - gvds: the GVDS filename


ndppp
-----

This recipe is part of the default pipeline framework.

NDPPP is the default flagger for LOFAR (but can be replaced with the AOFlagger).

- inputs:

  - executable: the NDPPP executable

  - initscript: an initialization script that setups up the
    environment for NDPPP. Usually lofarinit.sh works fine.

  - parset: the parset configuration file for NDPPP

  - suffix: suffix to add to the output (MS) file.

  - working_directory: where to store the new flagged files

  - data_start_time, data_end_time: chop files to selected times. Used
    to prevent eg BBS from crashing on subbands with unequal
    durations.

  - nproc: maximum number of simultaneous processes per output node.

  - nthreads: number of threads pr NDPPP process
 
  - mapfile: output mapping file (see also the `datamapper` recipe).

  - clobber: remove pre-existing output files.

    

bbs
---

This recipe is a wrapper around the new_bbs recipe that is part of the
default pipeline framework. It adds the `nproc` option, so that BBS
won't eat up all processing power if you don't want it to.

BlackBoard Selfcal (BBS) is the calibration routine for LOFAR. 

BBS uses quite a few parameters, including ones to access the
PostgreSQL database is uses behind the scenes and ones that point to
external commands.

- inputs:

  - control_exec: BBS control executable
  
  - kernel_exec: BBS kernel executable
  
  - initscript: an initialization script that setups up the
    environment for BBS. Usually lofarinit.sh works fine.

  - parset: the BBS configuration parset

  - db_key: a key to identify the BBS session

  - db_host: the PostgreSQL database host name

  - db_user: the PostgreSQL database user, usually postgres.

  - db_name: the PostgreSQL database, usually your username.

  - data_mapfile: the mapping file that will contain the BBS
    calibrated data. Any file (and file name) will do, but it is
    probably best to this in the parset directory.

  - skymodel: an explicite sky model to be used by BBS. Usually,
    however, the sky model is set up on the fly using the catalogs in
    the database. See the section `skymodel` below.

  - nproc: maximum number of simultaneous processes per output node.

vdsreader
---------

Very simple recipe to read through a global VDS file. 

- inputs:

  - gvds: the gvds file that will be read. By default this is probably 
    ``%(runtime_directory)s/jobs/%(job_name)s/vds/%(job_name)s.gvds``.


parmdb
------

Adds a parameter database to input Measurement Sets.

- inputs:

  - executable: the `parmdbm` executable. By default this is probably
    ``%(lofarroot)s/bin/parmdbm``.


  - working_directory: just the default working directory

  - mapfile: output mapping file.

sourcedb
--------

Adds a source database to input Measurement Sets.

- inputs:

  - executable: the `makesourcedb` executable. By default this is
    probably ``%(lofarroot)s/bin/makesourcedb``.

  - skymodel: the BBS sky model (created by the skymodel
    recipe). Something like
    ``%(runtime_directory)s/jobs/%(job_name)s/parsets/bbs.skymodel``

  - working_directory: just the default working directory

  - mapfile: output mapping file.

skymodel
--------

Creates a sky model from the database to be used by BBS.

- inputs:

  - ra, dec: Right Ascension and declination of the sky model centre
    (in floating point degrees).

  - search_size: radius of the circle in which to find sources for the
    sky model.

  - min_flux: minimum integrated flux (Jy) for selecting database
    sources.

  - skymodel_file: output filename

- outputs:

  - source_name, source_flux: the central source name and flux.



time_slicing
------------

Creates a list of time slices, that can be used to iterate on sections
of the data.

The various imagers also contain time slicing options, but because of
the way the imager create the images, one looses the necessary
metadata. The time_slicing recipe attempts to fix this, by slicing up
the actual MS and creating subdirectories for those sliced MSs. Note
that the sliced MS is just a "view" into the original, so there is
little extra disk space needed.

Once metadata gets properly transported into created images, this
recipe will become obsolete.

See also the `img2fits` recipe.

- inputs:

  - interval: time interval, specified in hh:mm:ss. Multiple slices
    will be generated with this interval size; the last slice will at
    least be as large as the specified time interval: a 5 hour
    observations split into 2 hours will result in a 2 and 3 hour slice.

  - gvds_file: file name of the GVDS file

  - mapfiledir = directory to store datamapper files (eg parset directory).

  - nproc: number of maximum simultaneous processors per node

- outputs:

  - timesteps: list of 3-tuples, each tuple containing ``(start_time,
    end_time, MS path)``.  

  - mapfiles: list of datamapper files, one for each timeslice (same
    order as timesteps).

Once data is sliced, you can then iterate through it, for example::

    outputs = self.run_task("time_slicing", gvds_file=gvds_file)
    mapfiles = outputs['mapfiles']
    subdirs = ["%d" % int(starttime) for starttime, endtime in
               outputs['timesteps']]
    for iteration, (mapfile, subdir) in enumerate(zip(mapfiles,
                                                    subdirs)):



cimager_trap
------------

**This recipe, and the cimager, is now deprecated. Please use the awimager recipe**.

A slightly more TRAP specific version of the SIP cimager recipe. It
stores the host and original MS in the outputs, which can be used to
obtain the ncessary meta data when source finding is run.

- inputs:

  - imager_exec: cimager executable

  - convert_exec: convertimagerparset executable

  - make_vds, combine_vds: makevds and combinevds executables

  - vds_dir: VDS working directory

  - parset: imager parset, in mwimager or cimager format

  - parset_type = "mwimager" (default) or "cimager"

  - results_dir = directory to store resulting images. Note that for
    TRAP, it is better to store images on the local nodes, for the
    conversion to FITS (see `img2fits`).

  - nproc: number of maximum simultaneous processors per node

  - timestep: ignored (see `time_slicing`).

- outputs:

  - gvds: the global VDS file

  - images: list of tuples holding the image name and original MS
    name. The image name consists is of the format ``host:path``.
    This list is used for conversion to FITS, including the meta data
    (taken from the MS).


awimager
--------

Run the awimager. 

- inputs:

  - executable: the awimager executable

  - parset: the parameter set that contains all the awimager
    options. See below for more explanation.

  - nproc: number of maximum simultaneous processors per
    node. **Safest to leave this at one (the default)**. See below for
    an explanation.

  - nthreads: Number of simultaneous threads per process. See below
    for an explanation.

The parameter set for the awimager specifies all the options that are
normally specified on the command line when running the awimager. You
can run `awimager -h` to see all these options.

A number of options are ignored, since these do not make sense in the
context of a pipeline recipe:

- hdf5, fits: the output format is fixed to be a CASA image.

- ms, image, restored: the input and output filenames are fixed.

All other options can (and should) be specified using the parset. Example::

    npix = 128
    verbose = 0
    niter = 100
    weight = natural
    wmax = 500
    npix = 256
    cellsize = 30arcsec
    data = CORRECTED_DATA
    padding = 1.
    niter = 10
    wprojplanes = 50
    timewindow = 300
    StepApplyElement = 2
    stokes = I
    threshold = 0
    operation = csclean

nproc & nthreads
~~~~~~~~~~~~~~~~

The awimager is parallelised, so that a single awimager run can use
multiple cores (thus making it faster); the number of cores used to be
run simultaneously is specified using the nthreads configuration
parameter.

Of course, there is also the option of running multiple awimager
together, e.g. when processing multiple subbands. This may cause
problems, however: the awimager creates some extra files, that have a
fixed filename (independent of the input MS file name); when the
subbands being processed are in the same directory, these extra files
start to overwrite each other, causing the awimager to (likely)
crash. There, until there is a work around, it is advised to leave
`nproc` at 1, and use `nthreads` instead to speed up the awimager
process.

The additional advantage of using `nthreads` over `nproc` is that,
even for the processing of a single subband, a speed gain is obtained,
which wouldn't be possible using `nproc`.


img2fits
--------

Convert a CASA image to a FITS file, including the necessary meta data
(header keywords) to run source finding. These meta data are found
from the sliced MSs created using the `time_slicing` recipe.

It also combines the subbands into a single image.

- inputs:

  - images: list of images, specified as 2-tuples ``(image_name,
    MS_name)``.

  - results_dir: directory to store the resulting images

  - combine: how to combine the (subband) images: ``average``
    (default) or ``sum``.

  - nproc: number of maximum simultaneous processors per node

- outputs:

  - fitsfiles: list of output FITS files

  - combined_fitsfile: combined image from all subbands.
  