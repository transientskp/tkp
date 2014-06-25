.. _database-section:

Database
========

.. warning::

   The information on this page is old and, in places, outdated.

This section concerns the (MonetDB or PostgreSQL) database that is used to
store extracted sources and determine variable sources. It does not deal with
the PostgreSQL database used by BBS.

The default scratch database, both on heastro1 and CEP, is simply
called tkp; the login and password are both tkp as well. On heastro1,
the database server is heastro1 or localhost, on CEP ldb001.

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
    $> mclient -dtkp [-hldb001]
    Welcome to mclient, the MonetDB/SQL interactive terminal
    Database: MonetDB v5.18.4, 'tkp'
    Type \q to quit, \? for a list of available commands
    auto commit mode: on
    sql>

The :option:`-h` host option is only necessary if you are connecting to
a database running on a different machine than the one you are currently logged
in to.

If you do not want to create a :file:`.monetdb` file or want to (temporarily)
access another database, simply use the :option:`-u<login>` option to use
a different login; the password will be asked interactively.

If you have your own MonetDB database, you may occasionaly need to update the
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
the necessary tables and functions.

You can check if everything went correct (assuming you didn't see any
errors in the output from the setup.db.batch script in the first
place) by logging in to your database (:command:`$> mclient -lsql -d<dbname>
-h<dbhost>`. Then execute the following commands::

    sql> select * from versions;

The first command should show a creation date of today.

Finally, for the latest-greatest and possibly unstable version of the database
setup, use `tkpdev` instead of `tkp`. This database gets wiped every night and
not backed-up though, so do not store anything valuable in it.

Installation
------------

If there is no working database on your system, you will have to install
MonetDB yourself. Grab the most recent (stable) release from www.monetdb.org,
then install in the usual way::

    $> ./configure 
    $> make
    ($> make check)
    $> (sudo) make install

Make sure the installation `bin` directory is in your path, then start up the
database server::

    $> monetdbd start

(notice the extra 'd' at the end: monetdb daemon.)

This will start one or more `mserver5` processes that take care of connections
to the database; the number of `mserver5` processes is dependent on the number
of databases in use.

You can have the databases stored in a different place than your default installation. This is convenient when you upgrade to newer MonetDB version; you can then still use the databases from the previous version. You have to point `monetdbd` to your so-called database farm. For example::

    $> monetdbd start /opt/dbfarm

You can check the status of any databases on your system::

    $> monetdb status

(Note: if you are using a non-default database farm location, as mentioned above, you don't need to give the path to the `monetdb` executable: it will normally find the correct `mserver` process.

You can easily create and then start a database::

    $> monetdb create <name>
    $> monetdb release <name>
    $> monetdb start <name>

Normally, the setup script in the `batches/` subdirectory of the database
directory will create the database automatically for you.

