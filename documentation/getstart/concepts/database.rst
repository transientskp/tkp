.. _database-intro:

+++++++++
Databases
+++++++++

The Trap consists of a very tightly-coupled set of logic implemented partial
in Python code and partially in a relational database. The database is
fundamental to the operation of the Trap: except for a few :ref:`standalone
tools <tools>`, use of a database is absolutely required.

The tight coupling between the Python code and the database implies that the
version of the :ref:`database schema <database_schema>` in use must match the
version in the of the code. Note that the schema version referred to in this
document is |db_version|.

In general, a single database management system (RDBMS) can support more than
one independent database. It is suggested that each coherent "project"
processed through the Trap be given an independent database. For example, a
project in this sense  might include all the data from a particular survey, or
all the data processed by a particular user. The resulting data can then be
archived as a coherent unit, while other projects continue to use the same
RDBMS undisturbed.

Within the context of the Trap, we support two different RDBMSs: `MonetDB
<http://www.monetdb.org/>`_ and `PostgreSQL <http://www.postgresql.org/>`_.
All Trap functionality is available whichever database you choose: it is
suggested you experiment to determine which provides the best combination of
usability and performance for your particular usage.

See the :ref:`relevant section <database_background>` of the documentation for
much more information about configuring and operating the database as well as
understanding its contents.
