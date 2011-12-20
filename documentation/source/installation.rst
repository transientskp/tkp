.. _installation:

Installation
============

Dependencies
------------

You need to have the following dependencies installed for using the
transients pipeline and the TKP library:

+ pyrap, which in turn depends on 

+ casacore and casarest

+ wcslib

+ boost

  The boost libraries, in particular the python one, to convert the wcslib
  library (or rather, part thereof) into a Python module.

+ the LOFAR pipeline framework

  Since the pipeline framework and the occasional part of the
  transients pipeline use parsets, you will also need to install the
  parset libraries from the LOFAR software. If you plan to use the
  imaging pipeline as well, you're probably best off installing all of
  the LOFAR imaging software (the LofIm package).

+ MonetDB, including the Python module (installed by default).

  This is the database that the transients pipeline uses. Note that
  for the imaging pipeline, you will also need a PostgreSQL
  database. MonetDB can be obtained from `http://www.monetdb.org`
  (please use the latest version. As of 2011-11-28, this is version
  11.5.9 (the August 2011 SP3 build).

+ numpy and scipy

  These Python modules are used throughout the TKP modules.

  In addition, f2py that comes with scipy is used to turn a FORTRAN routine
  into a Python module.

+ The Gnu Scientific Library, and the Python module `pygsql`.

  This is used by the classification module in the TKP library



Repository checkout and structure
---------------------------------

This section details the installation of the TRAP, and in addition the
TKP (since they share code, and can be found in the same
repository). The installation is from source, from the Subversion
repository. It is assumed you have access to that, and have done a
recent checkout (requiring a login) or update::

    $> svn checkout http://svn.transientskp.org/code tkp-code
    $> cd tkp-code
    $> svn up

At the base of the repository, you find several subdirectories, detailed shortly below:

+ tkp: the TKP Python library. The library consists of a set of Python
  modules, as well as a few 'external' modules, which interface with
  compiled C or FORTRAN libraries. The Python routines here form the
  core of the TKP software, and are used by the routines in the
  transients pipeline.

+ trap: the Transients Pipeline recipes, which are combined into a
  transients pipeline. A few extra recipes exist for the Transients
  Imaging Pipeline (TRIP) as well here.

+ trip: a few optimised parsets for running the pipeline suitable for
  the TKP project.

+ database: this contains the necessary database specific utilities,
  such as database functions and catalogs stored in the database.

+ other: at the moment, this contains various data that are not
  involved in running the pipeline, and can thus safely be ignored.

+ cmake: specific CMake routines for finding specific libraries, such
  as Boost, libwcs etc.

Note that each subdirectory (subproject, in fact) has a trunk and
branches subdirectories (cmake excepted). Normally, trunk is used (by
the default build script) for building the pipeline and installation;
we try to keep this stable enough to be able to run the pipeline on.


Building the pipeline and TKP software
--------------------------------------

In the base directory of the repository, there's a build.bash script,
which eases the building process. It essentially runs cmake to
configure the build, then make, then runs tests and finally installs
the TKP library and pipeline. bild.bash has several options:

+ :option:`--prefix <directory>`: the main installation directory (eg /opt/tkp)

+ :option:`--daily`: also create a daily (nightly) build directory; a `tkp`
  symlink is created to this directory.

+ :option:`--install`: install the library and pipeline

+ :option:`--develop`: install the development build (trunk). Use as default

+ :option:`--test`: perform unittests

+ :option:`--testlog <filename>`: log file for the output of the unittests. 

.. note::

    Option arguments are separated by a space from the option
    keyword, not by an equal ('=') sign (this is for OS X
    compatibilty).

The easiest way is to go ahead and try building the software. It will
do this in a separate build/ subdirectory, which you can remove
afterwards, eg for redoing a build with different settings::

    ./build.bash --prefix /opt/tkp --install --develop --daily --test --testlog /opt/tkp/unittests.log


If all goes well, you should end with the following directory structure (not all directories are shown):

    tkp/
    tkp/bin/
    tkp/lib/
    tkp/lib/python/
    tkp/lib/python/tkp/
    tkp/lib/python/tkp/utility/
    tkp/lib/python/tkp/database/
    tkp/lib/python/tkp/sourcefinder/
    tkp/lib/python/tkp/classification/
    tkp/lib/python/tkp/classification/features/
    tkp/lib/python/tkp/classification/manual/
    tkp/recipes/
    tkp/recipes/master/
    tkp/recipes/nodes/
    tkp/database/
    tkp/database/batches/
    tkp/database/functions/
    tkp/database/procedures/
    tkp/database/init/
    tkp/database/load/
    tkp/database/tables/


The :file:`bin` directory contains the :file:`trapinit.py` script (see
the :ref:`cookbook`); the lib directory contains
:file:`libwcstool.so`, a shared library used by some Python routines,
:file:`lib/python` contains a few shared Python libraries and the tkp
package (with its subpackages). :file:`recipes/` contains pipeline
recipes for master and node processes, and several main example
recipes (:file:`trap-images.py`, :file:`trap-with-trip.py` and
:file:`trap-alerts.py`). Finally, the :file:`database/` directory
contains the various tables and functions to initialize the
database.

Alternative install
~~~~~~~~~~~~~~~~~~~

If you have problems running the above script, or want to understand
in more detail what it does, you can build and install the pipeline
manually (in fact, stepping through the :file:`build.bash` script will
show you exactly what to do).

Firstly, make a build directory (simply called :file:`build`); within the root
of the SVN repository is probably fine (just don't check it in). Inside that
:file:`build` directory, execute::

    cmake <path-to-main-CMakeLists.txt-file> -DCMAKE_INSTALL_PREFIX=<root-dir-of-installation> -DTKP_DEVELOP

If this fails, carefully read the output of cmake; it likely did not find
a dependency. Check you have the required dependencies, then possibly edit the
corresponding :file:`Find<package>.cmake` file to ensure cmake can find your
installation.

Once the configuration completes, run make (:option:`-j` added for parallel = faster build)::

    make -j

And to install::

    make install

For running the tests, see below.

If the make step fails, try adding the `VERBOSE=1` flag for more information::

    make -j VERBOSE=1


Setting up the database
-----------------------

Notes on actually installing the MonetDB database system are :ref:`here
<database-section>`.

Before you run the database setup script, you need to check that the
database can actually find the catalog files, since these are not
included in the repository. The install script will try to search for
this in a few places, but on unknown systems, you may need to
explicitly point the database setup script to these files. In
:file:`database/load`, edit :file:`load.cat.vlss.sql`,
:file:`load.cat.nvss.sql` and :file:`load.cat.wenss.sql`: find the
catalog file names below the `COPY ????  RECORDS INTO
aux_catalogedsources FROM` lines and add the corresponding filenames
there, without the comment marks of course.

Then, to set up the database, go into the :file:`database/batches/`
subdirectory and run one of the corresponding bash scripts. Currently
(2011-10-20), that would be the :file:`setup.db.Aug2011-SP1.batch`
script. It requires four arguments::

    $> ./setup.db.batch <hostname> <database-name> <username> <password>

which you probably should have, either from the person who set up the
database for you, or when you created the database. Of course, this
all assumes your MonetDB is running fine; you can check this with

    $> monetdbd status

and::

    $> monetdb status

provided you have the rights to run the MonetDB commands (meaning you should be
in the `monetdb` system group).

It will take a couple of minutes to load the catalogs. You can always
perform a quick check to see if things went ok by going into the
database (replace trap with the corresponding database and login)::

    $> mclient -d trap -u trap -s 'select name from sys.tables where system = false;'
    password:
    +----------------------+
    | name                 |
    +======================+
    | versions             |
    | frequencybands       |
    | datasets             |
    | images               |
    | catalogs             |
    | catalogedsources     |
    | extractedsources     |
    | assoccatsources      |
    | assocxtrsources      |
    | lsm                  |
    | spectralindices      |
    | runningcatalog       |
    | temprunningcatalog   |
    | detections           |
    | node                 |
    | selectedcatsources   |
    | tempmergedcatalogs   |
    | mergedcatalogs       |
    | assoccrosscatsources |
    | transients           |
    | classification       |
    | monitoringlist       |
    +----------------------+
    22 tuples

    $> mclient -d trap -u trap -s 'select count(*) from catalogedsources;'           
    password:
    +---------+
    | L1      |
    +=========+
    | 2071205 |
    +---------+
    1 tuple


.. note::

    The build script in the root of the repository now (2011-11-28)
    will actually try and install the development database `tkpdev`. For that
    to work, however, it will still need to know where the catalog files are.
    If you are making regular (nightly) builds instead of just a one-time
    setup, you could choose to edit the three corresponding files, add the path
    to your catalog files and then commit those changes into the repository.


Testing the installation
------------------------

Once you have passed the build stage (either through the
:file:`build.bash` script or manually, after running :command:`make`),
you can run the various unit tests. Some of these require a running
database, which in turn may require a proper :file:`tkp.cfg`
configuration file for the database login details (if different from
the default).

First, you need to copy some extra files into the build directory. If
your :file:`build` directory is indeed at the root of the repository,
this should work::

    mkdir -p tkp/trunk/tests
    rsync -a --exclude=".svn" ../tkp/trunk/tests/ tkp/trunk/tests

and then run the test (the options make the tests quite verbose, but
that can be convenient to see what happened when a test fails)::

    ctest -VV --output-on-failure


.. note::

    The tests actually verify if the build worked, not so much the
    installation. You would need to edit the various (PYTHON)PATH
    settings in :file:`tkp/trunk/tests/runtests.bash` to test the
    installed modules instead.

