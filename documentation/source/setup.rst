Setup
=====

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

- `Python Louie <http://pypi.python.org/pypi/Louie/1.1>`_ (to be
  dropped in future versions).


On heastro1
-----------

The necessary TKP libraries are installed in /opt/tkp/tkp/. The last
part of this path is a symbolic link to a nightly build in
/opt/tkp/tkp-yyyy-mm-dd/; use a specific nightly build if you have
long-running jobs or need a specific TKP library version. A similar
structure holds for /opt/LofIm/lofar, which points to
/opt/LofIm/lofar-yyyy-mm-dd.  Within the /opt/tkp/tkp/ directory,
there are three subdirectories: lib/, recipes/ and database/. Lib
contains libraries, and hols the TKP Python package, in
lib/python/. The recipes/ directory contains the TRAP specific
recipes, while the database/ directory contains the necessary database
setup files.


Your :envvar:`PYTHONPATH` (and your ``ppath`` variable in your main
configuration file) will need to include the
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
the usual pipeline way. An example would be 
:file:`~/work/trap/jobs/<dataset_name>/` for your working
directory. Example configuration files can be copied and adjusted from
:file:`/home/evert/work/trap/trap.cfg` and
:file:`/home/evert/work/trap/jobs/example/control/tasks.cfg`.

The recipes directory, :file:`/opt/tkp/tkp/recipes/`, contains practical
recipes for the TRAP. The main (SIP/TRIP) recipes live
:file:`/opt/pipeline/recipes`, but some of these have a slightly adjusted
variant in the TKP recipes directory. The TKP recipes main directory
also contains an example trap.py, that essentially is an end-to-end
pipeline run (so it includes the SIP/TRIP step).

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


Now edit :file:`control/runtrap.sh`. This is a simple script that first clears
directories (since the pipeline won't clobber existing files
normally), and then runs the TRAP with the correct job ID. Edit the
paths accordingly.

You will notice there is no :envvar:`PYTHONPATH` in the shell
script. I use the convenience that for Python 2.6 and 2.7, the python
executable automatically picks up modules in
${HOME}/.local/lib/python2.x/site-packages/. Within that directory, I
have installed a few necessary Python packags (:command:`python
setup.py install --user` does this for you), and made symlinks to
other Python packages. You can copy or symlink this directory, or
simple change the last line in :file:`runtrap.sh` to::

    PYTHONPATH=/home/evert/.local/lib/python2.6/site-packages \
          python trap.py -d --task-file=./tasks.cfg -j example \
           -c /home/${HOME}/work/trap/trap.cfg   $1


Now edit the :file:`control/tasks.cfg` file as necessary. In
particular, pay attention to the database credentials: for BBS, set
``db_name`` to your user name; for the skymodel databse (MonetDB), you
can use the tkp/tkp/tkp scratch database, or the default I'm using.

Last things to edit are the :file:`control/to_process.py` file and the
various parsets. Once you are happy with all settings, you can run the
trap with::

    ./runtrap.sh


Of course, the default involves an end-to-end pipeline, including
time-slicing. If you want only to use sections of the TRAP, edit
`trap.py <trap_py.rst>`_ accordingly.




On CEP/lfe001
-------------

The necessary TKP libraries are installed in /home/rol/tkp/tkp/. The
last part of the directory is a symbolic link to a nightly build in
/home/rol/tkp/tkp-yyyy-mm-dd/; use a specific nightly build if you
have long-running jobs or need a specific TKP library version. Within
the /home/rol/tkp/tkp/ directory, there exist a lib/, recipes/ and
databse/ subdirectories. lib/ contains a single library used by the
TKP, and in lib/python/ you can find the necessary Python packages and
modules.

The recipes/ directory contains the TRAP specific recipes. The
database/ directory contains the files necessary for your database
setup; for the daily scratch database, you need not to worry about
this directory.

Your :envvar:`PYTHONPATH` (and your ``ppath`` variable in your main
configuration file) will need to include the
lib/python-packages directory. Other directories to include
are (following from the dependencies listed above):

- /opt/pipeline/framework/lib/python2.5/site-packages

- /opt/LofIm/daily/lofar/lib/python2.5/site-packages

- /opt/LofIm/daily/pyrap/lib

- /opt/pythonlibs/lib/python/site-packages

- /opt/pipeline/dependencies/lib/python2.5/site-packages

Other dependencies should have been installed system-wide (eg in /usr
or /usr/local).

Your :envvar:`LD_LIBRARY_PATH` and ``lpath`` in your configuration file needs to include:

- /opt/LofIm/daily/lofar/lib

- /opt/external/boost/boost-1.40.0/lib

- /opt/wcslib/lib

- /opt/LofIm/daily/pyrap/lib

- /opt/LofIm/daily/casarest/build/lib

- /opt/hdf5/lib

- /opt/LofIm/daily/casacore/lib

- /opt/LofIm/external/log4cplus/lib/


Now set up your working directory structure and configuration files in
the usual pipeline way. An example would be to have
``~/work/trap/jobs/<dataset_name>/`` for your working
directory. Example configuration files can be copied and adjusted from
``/home/rol/work/trap/trap.cfg`` and
``/home/rol/work/trap/jobs/example/control/tasks.cfg``.

The recipes directory, /home/rol/tkp/tkp/recipes/, contains practical
recipes for the TRAP. Main (SIP/TRIP) recipes live
/home/rol/pipeline/recipes, and some of these have a slightly adjusted
variant in the TKP recipes directory; for example, the datamapper has
been adjusted in case you only want to use imaging subcluster
(subcluster 3:
/home/rol/tkp/tkp/recipes/master/datamapper_sub3.py). The TKP recipes
main directory also contains an example trap.py, that essentially is
an end-to-end pipeline run (so including the SIP/TRIP step).

It is assumed you know how to edit the :file:`trap.cfg` and :file:`tasks.cfg`
files, as well as set up parset and other files. For simplicity,
however, the example files mentioned in the :ref:`recipes section <recipes-section>` can be used.


.. _cep-simple-way:

Simple way
~~~~~~~~~~

This section is, naturally, very similar to the :ref:`heastro simple
way section <heastro-simple-way>`. Mainly directory names change, and
various PATHs are longer, since less software is installed in default
system directories.

This describes a copy-paste way to get the trap running on CEP/lfe001
essentially by copying my setup and adjust a few PATHs
accordingly. The PATH set up is done slightly different than the
previous section, but in essence is the same.

Firstly, lay out the usual pipeline directory structure::

    $HOME/work/trap/jobs/<job-id>

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
fine.

Now edit the ``control/tasks.cfg`` file as necessary. In particular,
pay attention to the database credentials. In particular, for BBS, set
``db_name`` to your user name.

Last things to edit are the ``control/to_process.py`` file and the
parsets. Once you are happy with all settings, you can run the trap
with::

    ./runtrap.sh


Of course, the default involves an end-to-end pipeline, including
time-slicing. If you want only to use sections of the TRAP, edit
`trap.py <trap_py.rst>`_ accordingly.
