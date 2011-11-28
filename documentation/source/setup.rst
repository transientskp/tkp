Setup
=====

Preamble
--------

A few variables are used in the documentation below, indicating
relevant directories that may differ from system to system:

- :envvar:`${TKP}`: the base TKP directory on your system. On the heastro
  machines, this would be :file:`/opt/tkp/dev/tkp`, while on CEP2, this is
  :file:`/home/rol/tkp/dev/tkp`.

- :envvar:`${WORK}`: your working directory for the pipeline, that is, where the
  jobs control is kept. For me, this is :file:`${HOME}/work/trap`, while for
  other people, this is often :file:`${HOME}/pipeline_runtime`. This directory
  contains the jobs/ subdirectory, and in my case, the trap.cfg as
  well.

- :envvar:`${CONFIG}`: the main configuration file for the pipeline
  framework. It contains sections such as [DEFAULT], [layout],
  [cluster], [deploy] and [logging]. At the moment, it also contains a
  [database] section, but this may be removed (keep an eye on this
  documentation). My configuration file lives at
  :file:`${HOME}/work/trap/trap.cfg`.

- You will also need a TKP configuration file that has the database
  login details, unless you can rely upon the default (below), The TKP
  configuration should be :file:`${HOME}/.tkp.cfg`, and has the same syntaxa
  as the other pipeline configuration files. The default configuration
  for the pipeline looks as follows::

    [database]
    enabled = True
    host = localhost
    name = tkp
    user = tkp
    password = tkp
    port = 50000


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


On heastro1/2
-------------

The necessary TKP libraries are installed in :file:`/opt/tkp/dev/tkp/`. The last
part of this path is a symbolic link to a nightly build in
:file:`/opt/tkp/dev/tkp-yyyy-mm-dd/`; use a specific nightly build if you have
long-running jobs or need a specific TKP library version. A similar
structure holds for :file:`/opt/LofIm/lofar`, which points to
:file:`/opt/LofIm/lofar-yyyy-mm-dd`.  Within the :file:`/opt/tkp/tkp/` directory,
there are three subdirectories: lib/, recipes/ and database/. Lib
contains libraries, and hols the TKP Python package, in
lib/python/. The recipes/ directory contains the TRAP specific
recipes, while the database/ directory contains the necessary database
setup files.


Your :envvar:`PYTHONPATH` and the ``ppath`` variable in your main
configuration file will need to include the
lib/python directory. Other directories to include
are (following from the dependencies listed above):

- :file:`/opt/LofIm/lofar/lib/python2.6/dist-packages`

- :file:`/opt/monetdb/lib/python2.6/site-packages`

- :file:`/opt/pipeline/framework/lib/python2.6/site-packages`

Other dependencies are system-wide installed.

Your ``lpath`` in your configuration file (not so much your
:envvar:`LD_LIBRARY_PATH`, in fact) needs to include:

- :file:`/opt/LofIm/lofar/lib`

- :file:`/usr/local/lib`

- :file:`/opt/tkp/tkp/lib`


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

This describes a copy-paste way to get the trap running on heastro1 or
heastro2, essentially by copying my setup and adjust a few PATHs
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
--------------

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
(see the :ref:`databases section <database-section>`). If you use
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


Additional setup
----------------

There are two parts that you may want to set up for using the pipeline that are not part of the transients pipeline. The first part is passwordless ssh, the second part is the postgres database for using BBS (the calibration software). This information can also be found in the LOFAR imaging cookbook (sections 1.3.2 and 1.4).

Passwordless ssh
~~~~~~~~~~~~~~~~

When using the pipeline over the cluster, it generally uses ssh connections. Since you do not want to type in your password for every connection it makes, you create authorization keys with a blank password (if you find that insecure, you can also use something like ssh-agent to store the password. On most clusters, however, the security comes from your initial login to the frontend node anyway). To do this::

    $> ssh-keygen -t dsa

Enter a blank password (just press return). Then::

    $> cat ~/.ssh/id_dsa.pub >> ~/.ssh/authorized_keys

Since the `.ssh` directory is located in your home directory, the `authorized_keys` file is available on all cluster nodes, and you should now have a passwordless login to every cluster node.

You also want to disable the host key check that ssh performs every first time you log in to a node. You can do that by setting StrictHostKeyChecking to 'no'::

    $> cat >> ~/.ssh/config 
    StrictHostKeyChecking no
    <ctrl-D>


postgres
~~~~~~~~

This assumes you have a postgres database running, and can access that as root (through the postgres account). 

First, you need to obtain the bbs-sql.tgz file that contains the
various table definitions. This can for example be downloaded from
`http://www. lofar.org/wiki/lib/exe/fetch.php?media=engineering:software:tools:bbs:bbs-sql.tgz`.

