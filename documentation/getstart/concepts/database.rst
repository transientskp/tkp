.. _database-intro:

+++++++++++++++++
Pipeline Database
+++++++++++++++++

The TraP consists of a very tightly-coupled set of logic implemented partial
in Python code and partially in a relational database. The database contains
measurements made of sources being processed by the TraP, as well as
information about the images being processed, the regions of the sky being
surveyed, and so on. The database is fundamental to the operation of the TraP:
except for a few :ref:`standalone tools <tools>`, use of a database is
absolutely required.

The tight coupling between the Python code and the database implies that the
version of the :ref:`database schema <database-schema>` in use must match the
version in the of the code. Note that the schema version referred to in this
document is |db_version|.

In general, a single database management system (RDBMS) can support more than
one independent database. It is suggested that each coherent "project"
processed through the TraP be given an independent database. For example, a
project in this sense  might include all the data from a particular survey, or
all the data processed by a particular user. The resulting data can then be
archived as a coherent unit, while other projects continue to use the same
RDBMS undisturbed.

Within the context of the TraP, we support two different RDBMSs: `MonetDB
<http://www.monetdb.org/>`_ and `PostgreSQL <http://www.postgresql.org/>`_.
All TraP functionality is available whichever database you choose: it is
suggested you experiment to determine which provides the best combination of
usability and performance for your particular usage.

See the :ref:`relevant section <database_background>` of the documentation for
much more information about configuring and operating the database as well as
understanding its contents.

Finally, it is important to note that the pipeline database does *not* contain
any image pixel data: it stored metadata and derived products only. It is
possible to store pixel data as part of a pipeline run, but that is a separate
subsystem: see :ref:`mongodb-intro`.
