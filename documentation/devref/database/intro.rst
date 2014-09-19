.. _database-section:

Database
========

This section concerns the (MonetDB or PostgreSQL) database that is used to
store extracted sources and determine variable sources.

Creating a database
-------------------

When :ref:`installing the TraP <installation>` you will have installed and
configured a pipeline database management system and configured it to allow
access to authorized users.

A single database management system can support a number of active databases.
Each database can contain the results from a number of separate pipeline runs.
Creating multiple databases can be convenient in a range of situations. For
example, different databases could correspond to different science projects,
or to different end users.

The procedure for creating a database varies slightly between PostgreSQL and
MonetDB. You need to create the database manually. The database then needs
to be populated with the TRAP database schema before it can be used.

MonetDB
+++++++

The instructions for creating MonetDB databases differ per operating system
and environment. The `MonetDB online documentation
<https://www.monetdb.org/Documentation/monetdbd>`_
explains how to create a database.


PostgreSQL
++++++++++

The instructions for creating PostgreSQL databases differ per operating system
and environment. The `PostreSQL online documentation
<http://www.postgresql.org/docs/9.3/static/sql-createdatabase.html>`_
explains how to create a database.


Populating the database
-----------------------

Set the details of the database you have created in the ``database``
section of your :ref:`pipeline_cfg`. These include the host and port number of
the system running the database management system, the name of the database,
and the username and password of a user that will have access to that
database.

When you created a database and you've added the database connection parameters
to your pipeline.cfg you can populate the database with the TKP schema. You can
use the tkp-manage.py initdb subcommand for this.

inside your project folder run::

  $ tkp-manage.py initdb


Recreating the database schema
------------------------------

PostgreSQL
++++++++++
For PostgreSQL there is the optional **-d** flag for the initdb subcommand,
which removes all content before populating the database.

MonetDB
+++++++

In the case of MonetDB you need to do this manually. You can do this with the
following commands, where **${dbname}** should be replaced with the database
name::

    monetdb stop ${dbname}
    monetdb destroy -f ${dbname}
    monetdb create ${dbname}
    monetdb start ${dbname}
    monetdb release ${dbname}

For security reasons you should change the default password::

    mclient -d ${dbname} -s"ALTER USER \"monetdb\" RENAME TO \"${uname}\";
    ALTER USER SET PASSWORD '${passw}' USING OLD PASSWORD 'monetdb';"
