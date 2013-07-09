.. _database_introduction:

++++++++++++
Introduction
++++++++++++


The database subpackage consists of three modules. There are a few extra
modules (and a number of old modules that are not really used anymore), but the
main three modules are:

* database

* utils


Database
========

The database module provides a single class, :py:class:`Database`, which takes
care of the connection to the database. It provides a `connection` and
a `cursor` object to the database, as well as a few shortcut utility functions
for executing SQL queries.

The most typical use for the :py:class:`Database` class is something as follows,
assuming the default login settings (taking from the tkp configuration file)
are appropriate::

    from contextlib import closing

    with closing(Database()) as database:
        database.execute(<sql query>, <args>)
        results = database.fetchall()
        # or, more explicity:
        database.cursor.execute(<sql query>, <args>)
        results = database.cursor.fetchall()

For more details, see the :ref:`database <database-database>` section.


Dataset
=======

The dataset module provides a miniature object relation mapper (ORM) interface
to the database. This interface is not fully complete, but it does allow one to
treat several database tables and their data as Python classes and instances.
The mapped tables and their classes are:

* datasets: DataSet

* images: Image

* extractedsource: ExtractedSource

Each of these classes inherits from the DBOject class. This class provides
a few general methods to interface with the underlying database. Details are
provided in the corresponding :ref:`database <database-database>` documentation;
a typical usage example could look like this::

    db_image = DBImage(id=image_id, database=database)
    db_image.insert_extracted_sources(results)

where `database` is the database opened above, and image_id points to an
existing row in the images table. `results` is obtained from the source finder,
and are stored in the database per image into extractedsource. In case of
a new image, one would leave out the `id` keyword in the first line, and
instead supply a `data` keyword argument that is a dictionary with the
necessary information (again, see the :ref:`database documentation
<database-database>`).


Utils
=====

note: this probably has been depricated.

The utils module contains the actual SQL queries used for the various database
routines, such as source insertion, source association, keeping track of the
monitoring list, etcetera. All functions and queries within each function
follow a fixed pattern: functions accept a connection object (e.g.
Database().connection), and each query is executed within a try-except block in
case the database raises an error. There is some overhead in the sense that
a cursor is created within each function (instead of using the
Database().cursor object), but other than that, the routines in utils provide
the fastest and most direct interaction with the database.

Several functions are called from methods of the classes in the dataset module,
to provide a hopefully clearer interface, but can of course be called directly
as well. Finally, a number of functions are private to the module, and their
name is therefore preceded with an underscore. These functions tend to be
called from another funtion within utils, and should only be used as such. 
