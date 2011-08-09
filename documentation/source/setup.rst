Setup
=====

Preamble
--------

A few variables are used in the documentation below, indicating relevant directories that may differ from system to system:

- ${TKP}: the base TKP directory on your system. On the heastro
  machines, this would be /opt/tkp/dev/tkp, while on CEP2, this is
  /home/rol/tkp/dev/tkp.

- ${WORK}: your working directory for the pipeline, that is, where the
  jobs control is kept. For me, this is ${HOME}/work/trap, while for
  other people, this is often ${HOME}/pipeline_runtime. This directory
  contains the jobs/ subdirectory, and in my case, the trap.cfg as
  well.

- ${CONFIG}: the main configuration file for the pipeline
  framework. It contains sections such as [DEFAULT], [layout],
  [cluster], [deploy] and [logging]. At the moment, it also contains a
  [database] section, but this may be removed (keep an eye on this
  documentation). My configuration file lives at
  ${HOME}/work/trap/trap.cfg.

Dependencies
------------

You will need to make sure the following external dependencies exist
on your system, since these are not included in the TKP repository &
installation:

- The LOFAR pipeline framework

- The main LOFAR tree, with various standalone routines such as
  makevds, NDPPP, KernelControl etc. The latter are actually part of
  the TRIP (Transients Imaging Pipeline), but are a practical
  requirement for a full TRAP run.

  This includes various external libraries such as HDF5 and wcslib.

- A working MonetDB installation, together with the Python
  interface. See also the section on :ref:`the database
  <database-section>`.


On heastro1
-----------

The necessary TKP libraries are installed in /opt/tkp/dev/tkp/. The last
part of this path is a symbolic link to a nightly build in
/opt/tkp/dev/tkp-yyyy-mm-dd/; use a specific nightly build if you have
long-running jobs or need a specific TKP library version. A similar
structure holds for /opt/LofIm/lofar, which points to
/opt/LofIm/lofar-yyyy-mm-dd.  Within the /opt/tkp/tkp/ directory,
there are three subdirectories: lib/, recipes/ and database/. Lib
contains libraries, and hols the TKP Python package, in
lib/python/. The recipes/ directory contains the TRAP specific
recipes, while the database/ directory contains the necessary database
setup files.


Your :envvar:`PYTHONPATH` and the ``ppath`` variable in your main
configuration file will need to include the
lib/python directory. Other directories to include
are (following from the dependencies listed above):

- /opt/LofIm/lofar/lib/python2.6/dist-packages

- /opt/monetdb/lib/python2.6/site-packages

- /opt/pipeline/framework/lib/python2.6/site-packages

Other dependencies are system-wide installed.

Your ``lpath`` in your configuration file (not so much your
:envvar:`LD_LIBRARY_PATH`, in fact) needs to include:

- /opt/LofIm/lofar/lib

- /usr/local/lib

- /opt/tkp/tkp/lib


Now set up your working directory structure and configuration files in
the usual pipeline way.  Example configuration files can be copied and
adjusted from :file:`/home/evert/work/trap/trap.cfg` and
:file:`/home/evert/work/trap/jobs/example/control/tasks.cfg`.

The recipes directory, :file:`${TKP}/recipes/`, contains practical
recipes for the TRAP; these are in the master and nodes subdirectories
(frontend and compute node recipes). The main (SIP/TRIP) recipes can
be found in :file:`/opt/pipeline/recipes`, but some of these have a
slightly adjusted variant in the TKP recipes directory. The TKP
recipes main directory also contains example trap.py and
trap-images.py recipes: the first recipe is essentially is an
end-to-end pipeline run (so it includes the SIP/TRIP step), while the
second one takes a list of images as input, and starts at the source
extraction point (note: the former may not be completely up to date
anymore; please take care).

It is assumed you know how to edit the :file:`trap.cfg` and :file:`tasks.cfg`
files, as well as set up parset and other files. For simplicity,
however, the example files mentioned in the :ref:`recipes section
<recipes-section>` can be used.


.. _heastro-simple-way:

Simple way
~~~~~~~~~~

(For simplicity, me, myself and I in the following will simply refer to the
current author of this document.)

This describes a copy-paste way to get the trap running on heastro1,
essentially by copying my setup and adjust a few PATHs
accordingly. The PATH set up is done slightly different than the
previous section, but in essence is the same.

Firstly, lay out the usual pipeline directory structure::

    $HOME/work/trap/jobs/<job-id>

where job-id is probably named after the dataset you want to process.

Copy the directory and subdirs from ``~evert/work/trap/jobs/example/`` into this directory::

    cp -r ~evert/work/trap/jobs/example/*  $HOME/work/trap/jobs/<job-id>/.

And copy the trap configuration file::

    cp -r ~evert/work/trap/trap.cfg  $HOME/work/trap/trap.cfg
    
You should now have the following structure::

    $HOME/work/trap/trap.cfg
    $HOME/work/trap/jobs/<job-id>/
                                  control/
                                  parset/
                                  vds/
                                  results/
                                  logs/
                                    
The results, logs and vds directories will be empty.


Now edit trap.cfg. Only a few edits will be necessary. In particular, check:

- ``runtime_directory``

- ``lofarroot``

- ``default_working_directory``

You can use my cluster description file and recipes directories.  If
you have your own MonetDB database, change the login details in the
``[database]`` section accordingly, otherwise use mine or the default
scratch one: tkp/tkp/tkp.


Now edit :file:`control/runtrap.sh`. This is a simple script that
first clears directories (since the pipeline won't clobber existing
files normally), and then runs the TRAP with the correct job ID. Edit
the paths accordingly. Don't forget to change the job name (value to
-j option) as well!

Now edit the :file:`control/tasks.cfg` file as necessary. In
particular, pay attention to the database credentials: for BBS, set
``db_name`` to your user name; for the skymodel databse (MonetDB), you
can use the tkp/tkp/tkp scratch database, or the default I'm using.

Last things to edit are the :file:`control/to_process.py` or
:file:`control/images_to_process.py` files and the various
parsets. Once you are happy with all settings, you can run the trap
with::

    ./runtrap.sh




On CEP2/lhn001
-------------

The necessary TKP libraries are installed in /home/rol/tkp/dev/tkp/. The
last part of the directory is a symbolic link to a nightly build in
/home/rol/tkp//dev/tkp-yyyy-mm-dd/; use a specific nightly build if you
have long-running jobs or need a specific TKP library version. Within
the /home/rol/tkp/tkp/ directory, there exist a lib/, recipes/ and
databse/ subdirectories. lib/ contains a single library used by the
TKP, and in lib/python/ you can find the necessary Python packages and
modules.

The recipes/ directory contains the TRAP specific recipes. The
database/ directory contains the files necessary for your database
setup; for the daily scratch database, you need not to worry about
this directory.

Your :envvar:`PYTHONPATH` (and your ``engine_ppath`` variable in your main
configuration file) will need to include the
lib/python-packages directory. Other directories to include
are (following from the dependencies listed above):

- /opt/cep/pipeline/framework/lib/python2.6/site-packages

- /opt/cep/LofIm/daily/lofar/lib/python2.6/dist-packages

- /opt/cep/LofIm/daily/pyrap/lib

- /opt/cep/pythonlibs/lib/python/site-packages

- /home/rol/.local/lib/python2.6/site-packages

Other dependencies should have been installed system-wide (eg in /usr
or /usr/local).

Your :envvar:`LD_LIBRARY_PATH` and ``engine_lpath`` in your configuration file needs to include:

- /opt/cep/LofIm/daily/pyrap/lib

- /opt/cep/LofIm/daily/casacore/lib

- /opt/cep/hdf5/lib:/opt/cep/wcslib/lib


Now set up your working directory structure and configuration files in
the usual pipeline way. An example would be to have
``~/work/trap/jobs/<dataset_name>/`` for your working
directory. Example configuration files can be copied and adjusted from
``/home/rol/work/trap/trap.cfg`` and
``/home/rol/work/trap/jobs/example/control/tasks.cfg``.

The recipes directory, {$TKP}/recipes/, contains practical recipes for
the TRAP.  The TKP recipes main directory also contains example
trap.py and trap-images.py recipes: the first recipe is essentially is
an end-to-end pipeline run (so it includes the SIP/TRIP step), while
the second one takes a list of images as input, and starts at the
source extraction point (note: the former may not be completely up to
date anymore; please take care).

It is assumed you know how to edit the :file:`trap.cfg` and
:file:`tasks.cfg` files, as well as set up parset and other files. For
simplicity, however, the example files mentioned in the :ref:`recipes
section <recipes-section>` can be used.


.. _cep-simple-way:

Simple way
~~~~~~~~~~

This section is, naturally, very similar to the :ref:`heastro simple
way section <heastro-simple-way>`. Mainly directory names change, and
various PATHs are longer, since less software is installed in default
system directories.

This describes a copy-paste way to get the trap running on CEP2/lhn001
essentially by copying my setup and adjust a few PATHs
accordingly. The PATH set up is done slightly different than the
previous section, but in essence is the same.

Firstly, lay out the usual pipeline directory structure::

    ${WORK}/jobs/<job-id>

where job-id is probably named after the dataset you want to process.

Copy the directory and subdirs from ``~rol/work/trap/jobs/example/`` into this directory::

    cp -r ~rol/work/trap/jobs/example/*  $HOME/work/trap/jobs/<job-id>/.

And copy the trap configuration file:

    cp -r ~rol/work/trap/trap.cfg  $HOME/work/trap/trap.cfg
    
You should now have the following structure::

    $HOME/work/trap/trap.cfg
    $HOME/work/trap/jobs/<job-id>/
                                  control/
                                  parset/
                                  vds/
                                  results/
                                  logs/
                                    
The results, logs and vds directories will be empty.


Now edit trap.cfg. Only a few edits will be necessary. In particular, check:

- ``runtime_directory``

- ``lofarroot``

- ``default_working_directory``

- ``database``

You can use my cluster description file and recipes directories.  If
you have your own MonetDB database, change the login details in the
``[database]`` section accordingly, otherwise use mine or, preferred
for purely testing if you can run the TRAP, use the default tkp one
(see the :ref:`databases section <databases-section>`). If you use
your own database, make sure the table definitions are up to scratch.


Now edit ``control/runtrap.sh``. This is a simple script that first
clears directories (since the pipeline won't clobber existing files
normally), and then runs the TRAP with the correct job ID. Edit the
paths to your data directories accordingly. There is both a PYTHONPATH
and a LD_LIBRARY_PATH in front of the main executable; these should be
fine. Don't forget to change the job name (value to -j option) as
well!

Now edit the ``control/tasks.cfg`` file as necessary. Pay attention to
the database credentials. In particular, for BBS, set ``db_name`` to
your user name.

Last things to edit are the ``control/to_process.py`` file and the
parsets. Once you are happy with all settings, you can run the trap
with::

    ./runtrap.sh


Of course, the default involves an end-to-end pipeline, including
time-slicing. If you want only to use sections of the TRAP, edit
`trap.py <trap_py.rst>`_ accordingly.
