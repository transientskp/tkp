.. _database-section:

Database
========

This section concerns the (MonetDB) database that is used to store
extracted sources and determine variable sources. In addition, it
stores catalogs from previous surveys, which can be used for creating
a sky model for BBS, and it stores some characteristics of
(classified) transient sources. It does not deal with the PostgreSQL
database used by BBS.

The default scratch database, both on heastro1 and CEP, is simply
called tkp; the login and password are both tkp as well. On heastro1,
the database server is heastro1 or localhost, on CEP ldb001.

Be warned that this database gets completely wiped and rebuild every
night: do not save any essential data here!

Interactive login
-----------------

You can login to the scratch database using the :command`mclient` command
(on lhn001, best is probably to use a locally build version, eg
:command:`/home/rol/.local/bin/mclient`. On heastro1,
it's :command:`/opt/monetdb/bin/mclient`). 

This allows you to manually inspect the data that is stored in the
database, which is sometimes useful for debugging purposes.

You will need a :file:`$HOME/.monetdb` file that contains the login
details (user and password). The following should work::

    $> cat > ~/.monetdb <<EOF
    user=tkp
    password=tkp
    EOF
    $> mclient -lsql -dtkp [-hldb001]
    Welcome to mclient, the MonetDB/SQL interactive terminal
    Database: MonetDB v5.18.4, 'tkp'
    Type \q to quit, \? for a list of available commands
    auto commit mode: on
    sql>


If you have your own MonetDB database, you may need to update the
tables to the current definition. These table and function definitions
are stored in the TKP daily build directory, in the database
subdirectory. You probably first want to create a dump of any contents
you'd like to save (using the :command:`sql>\\D` command on the
``sql>`` prompt; see :command:`sql>\\?`). After that, remove all tables
(:command:`sql>drop table <name> cascade;`. Do this for all tables)
and possibly even functions (you can get an overview of the latter
using :command:`sql>select name from sys.functions where mod =
'user';`).

Then, cd into the daily build :file:`database/batches`
directory(:file:`/opt/tkp/tkp/database/batches` on heastro1 and
:file:`/home/rol/tkp/tkp/database/batches` on lfe001), and run::

    $> ./setup.db.batch --no-create-database ldb001 <dbname>

(Again, this requires a correct :file:`~/.monetdb` file.)
The :option:`--no-create-database` will prevent the script from completely
deleting and recreating the database, and instead it will just create
the necessary tables and functions. It will also load various catalogs
(NVSS, WENSS, VLSS); this may take a while, so if the script seems to
pause for a while, it is probably loading those catalogs.

You can check if everything went correct (assuming you didn't see any
errors in the output from the setup.db.batch script in the first
place) by logging in to your database (:command:`$> mclient -lsql -d<dbname>
-h<dbhost>`. Then execute the following commands::

    sql> select * from versions;

    sql> select * from catalogs;

    sql> select count(*) from catalogedsources;

The first command should show a creation date of today. The second
command will tell you which catalogs have been loaded (currently,
March 2011, there are four, since the WENSS comes in two parts). The
third command will tell you how many catalog sources there are (March
2011, 2071205 sources).


Installation
------------

If there is no working database on your system, you will have to install MonetDB yourself. Grab the most recent (stable) release from www.monetdb.org, then install in the usual way::

    $> ./configure 
    $> make
    ($> make check)
    $> (sudo) make install

Make sure the installation `bin` directory is in your path, then start up the database server::

    $> monetdbd start

(notice the extra 'd' at the end: monetdb daemon.)

You can check the status of any databases on your system::

    $> monetdb status

You can easily create and then start a database::

    $> monetdb create <name>
    $> monetdb release <name>
    $> monetdb start <name>

Normally, the setup script in the `batches/` subdirectory of the database directory will create the database automatically for you.
