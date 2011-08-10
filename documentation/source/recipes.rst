.. _recipes-section:

TRAP recipes
============

The various recipes used in the TRAP are listed below. Some are SIP
recipes which have been included for completeness, some are adapted
SIP recipes (like cimager_trap). All recipes can be found in the
recipes subdirectory.

An example Python file showing how to connect all the recipes is shown
at the end of this section.

For more information on the NDPPP, BBS and imager recipes (in
particular the parsets), see eg the LOFAR imaging cookbook.

datamapper
----------

This recipe is part of the default pipeline framework.

Calculates a file that maps the datasets to their respective storage
or compute nodes and subclusters, so that the pipeline hands out the
correct jobs (with datafiles) to the correct nodes.

- inputs:
  
  - mapfile: the filename (full path) of the mapping file

- outputs:

  - the mapping filename. This is often used by the next recipe(s).

Important note: the datamapper recipe looks at the file path to
determine the node and subcluster. This only works on the LOFAR
Groningen offline cluster; for heastro1, there is a separate recipe
with a slight modification, so that heastro1 is always picked up as
the compute node.


new_vdsmaker
------------

This recipe is part of the default pipeline framework.

VDS files are another way to map files to their respective nodes; in
addition, VDS files store information like time and frequency range.

The new_vdsmaker recipe creates local and a global VDS file for the specified files.

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


new_ndppp
---------

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

This recipe is part of the default pipeline framework.

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

  - key: a key to identify the BBS session

  - db_host: the PostgreSQL database host name

  - db_user: the PostgreSQL database user, usually postgres.

  - db_name: the PostgreSQL database, usually your username.

  - makevds: the makevds executable

  - combinevds: the combinevds executable

  - makesourcedb: the makesourcedb executable

  - parmdb: the parmdb executable

  - nproc: maximum number of simultaneous processes per output node.

  - skymodel: an explicite sky model to be used by BBS. Usually,
    however, the sky model is set up on the fly using the catalogs in
    the database. See the section `skymodel` below.


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

The cimager recipes also contains a time slicing option, but while
this option still exists in `cimager_trap`, it may be removed in the
future. This will depend how the SIP deals with image time slices.

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



img2fits
--------

Convert a CASA image to a FITS file, including the necessary meta data
(header keywords) to run source finding. It also combines the subbands
into a single image.

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
  

source_extraction
-----------------

Run the source finding routine. In addition, this recipe will store
the detected sources inside the database, and tries to associate the
new sources with existing ones.

- inputs:

  - image: list of (FITS) images.

  - detection_level: detection level for sources, in background sigma.

  - dataset_id: dataset to which images belong. If run with the
    default of ``None``, a dataset_id will be created in the database,
    that can then be used in later iterations.

  - radius: relative radius for source association. Default is 1.

  - nproc: number of maximum simultaneous processors per node


- outputs:

  - dataset_id: see the dataset_id entry in the inputs.

Notes:

- In a future TRAP version, the source association part may get its
  own recipe.

- A future version will allow for other images than just FITS.



transient_search
----------------

Search through all matched sources and find variable sources by
looking for deviations in their light curve.

- inputs:

  - detection_level: Level above which a source is classified as a
    transient. This is done by looking at the chi-squared value of the
    light curve. Default = 3.

  - closeness_level: ignore associations with level > closeness
    level. Default = 3.

  - dataset_id: The dataset ID, likely obtained from the
    source_extraction recipe.

- outputs:
  
  - transient_ids: list of database IDs of the sources which are found
    to be transient.

  - siglevels: significance levels of the "transientness".

  - transients: list of :ref:`Transient
    <tkpapi:tkp.classification.manual.transient>` objects.


This routine is implemented by performing a database search, and thus
the recipe is simply run on the front-end node.


feature_extraction
------------------

Obtain characteristics from detected transient sources. This may fail
(ie, produces None or 0 for values) when little to no
background/steady-state information is known.

Current characteristics obtained are:

- duration

- peak flux

- increase and decrease from background to peak and back, and their
  ratio.

Each feature extraction is run as a separate node.

- inputs:

  - transients: list of :ref:`Transient
    <tkpapi:tkp.classification.manual.transient>` objects,
    previously obtained with the transient_search recipe.

  - nproc: number of maximum simultaneous processors per node.

- outputs:

  - transients: list of :ref:`Transient
    <tkpapi:tkp.classification.manual.transient>` objects.


classification
--------------

Attempt to classify the detected transients into one or more groups.

- inputs:

  - schema: Python file containing classification schema. Currently
    ignored (remnant from an old version). The schema is currently set
    by importing a class from
    tkp.classification.manual.classification. A future version wil
    make this more flexible.

  - weight_cutoff: set a cut-off: any classified transient with a
    total classification weight below this value will not be output.

  - transients: list of :ref:`Transient
    <tkpapi:tkp.classification.manual.transient>` objects,
    previously obtained with the transient_search recipe.

  - nproc: number of maximum simultaneous processors per node.

- outputs:

  - transients: list of :ref:`Transient
    <tkpapi:tkp.classification.manual.transient>` objects,
    amended with their classification.

