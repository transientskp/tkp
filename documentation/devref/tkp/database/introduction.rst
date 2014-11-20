.. _database_introduction:

++++++++++++
Introduction
++++++++++++


The database subpackage consists of several modules dedicated to their tasks. 
The main modules are:

* database

* general


Database
========

The database module provides a single class,
:py:class:`tkp.db.database.Database`, which takes care of the connection to
the database. It provides a `connection` and a `cursor` object to the
database, as well as a few shortcut utility functions for executing SQL
queries.

The most typical use for the :py:class:`tkp.db.database.Database` class is
something as follows, assuming the default login settings (taken from the tkp
configuration file) are appropriate::

    from tkp.db import execute as execute

    cursor = execute(<sql query>, <args>)
    results = cursor.fetchall()

For more details, see the :ref:`database <database-database>` section.


General: dataset, image, extracted sources
==========================================

The dataset module provides a miniature object relation mapper (ORM) interface
to the database. This interface is not fully complete, but it does allow one to
treat several database tables and their data as Python classes and instances.
The mapped tables and their classes are:

* datasets: DataSet

* images: Image

* extractedsource: ExtractedSource

Each of these classes inherits from the DBOject class. This class provides
a few general methods to interface with the underlying database. 
A typical usage example could look like this::

    db_image = DBImage(id=image_id, database=database)
    db_image.insert_extracted_sources(results,'blind')

where `database` is the database opened above, and image_id points to an
existing row in the images table. `results` is obtained from the source finder,
and are stored in the database per image into extractedsource. In case of
a new image, one would leave out the `id` keyword in the first line, and
instead supply a `data` keyword argument that is a dictionary with the
necessary information (again, see the :ref:`database documentation
<database-database>`).

Currently, the usage described above is sometimes used in the unittest code. In the pipeline
code we try to restrict the usage of the orm, since it can get quite complex. 
Inserting the extracted sources for a particular image looks like this::

    from tkp.db import general as dbgen
    dbgen.insert_extracted_sources(image.id, results.sources, 'blind')

where image.id is the id of the image to which the sources belong to.


Other
=====

The remaining modules contain the actual SQL queries used for the various database
routines, such as source insertion, source association, keeping track of the
monitoring sources and null detections, etc. 
All functions and queries within each function call follow a fixed pattern: 
functions inherit the connection object, and each query is executed 
within a try-except block in case the database raises an error. 
There is some overhead in the sense that a cursor is created 
for each function call, but other than that, the routines provide 
the fastest and most direct interaction with the database.

Several functions are called from methods of the classes in the dataset module,
to provide a hopefully clearer interface, but can of course be called directly
as well. Finally, a number of functions are private to the module, and their
name is therefore preceded with an underscore. These functions tend to be
called from another funtion within the same module, but may be called from 
another module as well.
