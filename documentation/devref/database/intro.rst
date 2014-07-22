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
MonetDB.

MonetDB
+++++++

Set the details of the database you would like to create in the ``database``
section of your :ref:`pipeline_cfg`. These include the host and port number of
the system running the database management system, the name of the database,
and the username and password of a user that will have access to that
database. The last three are all at your discretion: choose appropriate
database and user names, and make sure the password is secure.

In addition, when configuring MonetDB, you will have set a passphrase. This
passphrase provides the appropriate administrative access to create new
databases and users on the database management system. Specify it in the
pipeline configuration.

Finally, run::

  $ tkp-manage.py initdb

Your database will be created, and is then available for use.

PostgreSQL
++++++++++

When installing PostgreSQL, you will have created a user with administrative
powers. In order to create a new database, you must log in as that user.
Therefore, edit the ``database`` section of your :ref:`pipeline_cfg`. Set the
host name and port number of the system running the database management
system, provide the username and password of the administrative user, and set
the database name to the name of the database you wish to create. Then run::

  $ tkp-manage.py initdb

This will create a database with the name you have requested. It will also
create a new user which has username and password equal to the database name,
and which has access to the database. You should use this user to access the
database when running pipeline jobs. Therefore, you will need to edit your
pipeline configuration and replace the name and password of the superuser with
the name of the newly created database.

Your database is now available for use.
