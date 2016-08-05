"""
This module contains lightweight container objects that corresponds
to a dataset, image or extracted source in the database; it is actually a
mini Object Relation Mapper (ORM). The correspondence between the object
and table row is matched through the private _id attributes.

Each dataset contains several database Images; each Image contains a
number of ExtractedSources. The database Images correspond to the
images table in the database, *not* to sourcefinder images or actual
image data files on disk (this distinction is important; while there
are certainly parts in common, several are not).


The current setup is done in large part to keep the database and
sourcefinder (and other parts of the TKP package) separate; tightly
integrated database tables/sourcefinder images/disk files make it more
difficult to improve the code or distribute parts separately.

Usage
=====

In practice, a DataSet object is created, and separate Images are
created referencing that DataSet() instance; ids are automatically
assigned where necessary (i.e., on creation of a new entry (row) in
the database).

Objects can also be created using an existing id; data is then taken
from the corresponding table row in the database.


Creating new objects
====================

The following code is an usage example, but should not be used as a
doc test (since the database value can differ, and thus the test would
fail)::

    # database sets up and holds the connection to the actual database
    >>> database = tkp.db.database.Database()

    # Each object type takes a data dictionary on creation, which for newly objects
    # has some required keys (& values). For a DataSet, this is only 'description';
    # for an Image, the keys are 'freq_eff', 'freq_bw_', 'taustart_ts',
    # 'tau_time' & 'url'
    # The required values are stored in the the REQUIRED attribute
    >>> dataset = DataSet(data={'description': 'a dataset'}, database=database)

    # Here, dataset indirectly holds the database connection:
    >>> dataset.database
    DataBase(host=heastro1, name=trap, user=trap, ...)
    >>> image1 = Image(data={'freq_eff': '80e6', 'freq_bw': 1e6, \
        'taustart_ts': datetime(2011, 5, 1, 0, 0, 0), 'tau_time': 1800.,  'url': '/'}, dataset=dataset)  # initialize with defaults
        # note the dataset kwarg, which holds the database connection
    >>> image1.tau_time
    1800.
    >>> image1.taustart_ts
    datetime.datetime(2011, 5, 1, 0, 0, 0)
    >>> image2 = Image(data={'freq_eff': '80e6', 'freq_bw': 1e6, \
        'taustart_ts': datetime(2011, 5, 1, 0, 1, 0), 'tau_time': 1500.,'url': '/'}, dataset=dataset)
    >>> image2.tau_time
    1500
    >>> image2.taustart_ts
    datetime.datetime(2011, 5, 1, 0, 1, 0)
    # Images created with a dataset object, are automatically added to that dataset:
    >>> dataset.images
    set([<tkp.database.dataset.Image object at 0x26fb6d0>, <tkp.database.dataset.Image object at 0x26fb790>])

Updating objects
================

To update objects, use the update() method.

This method does two things, in the following order:

1. it updates from the database to the object: if there have been
changes in the database, the object will reflect that after executing
update()

2. then, it updates the object (and the database) with values supplied
by the user. The latter values are optional; no supplied values simply
means there aren't any updates.


    >>> image2.update(tau_time=2500)    # updates the database as well
    >>> image2.tau_time
    2500
    >>> database.cursor.execute("SELECT tau_time FROM images WHERE imageid=%s" % \
                                 (image2.id,))
    >>> database.cursors.fetchone()[0]
    2500
    # Manually update the database
    >>> database.cursor.execute("UPDATE images SET tau_time=2000.0 imageid=%s" % \
                                 (image2.id,))
    >>> image2.tau_time   # not updated yet!
    2500
    >>> image2.update()
    >>> image2.tau_time
    2000


Assigning objects to a table row on creation
============================================

It is also possible to create a DataSet, Image or ExtractedSource instance from the
database, using the ``id`` in the initializer::

    >>> dataset2 = DataSet(id=dataset.id, database=database)
    >>> image3 = Image(imageid=image2.id, database=database)
    >>> image3.tau_time
    2000

If an ``id`` is supplied, ``data`` is ignored.
"""

import logging
from tkp.db.generic import columns_from_table, set_columns_for_table
from tkp.db.general import insert_dataset
from tkp.db.alchemy.image import insert_image
import tkp.db
import tkp.db.quality
from tkp.db.database import Database


logger = logging.getLogger(__name__)


class DBObject(object):
    """Generic mini-ORM object

    Derived objects will need to implement __init__, which for
    practical reasons is split up in __init__ and _init_data: the
    latter is called at the end __init__, so a derived __init__ would
    have super(Derived, self).__init__() at the start and
    super(Derived, self)._init_data() at the end.

    __init__ takes care of setting the id, the supplied `data` dictionary
    and the connection to the database.

    _init_data sets the actual data either from the database (in case
    of a supplied id) or from the `data` dictionary.
    """

    def __init__(self, data=None, database=None, id=None):
        """Basic initialization.

        Inherited classes need to implement any actual database action,
        by calling self._init_data() at the end of their __init__
        method.
        """
        # Call the id property to set the _id attribute
        self._id = id
        self._data = {} if data is None else data.copy()
        self.database = database

    def _init_data(self):
        """Set up the data, either by creating a new DBOject or
        updating it from the database using the id

        This method should only be called from __init__(), probably at the end.

        Note that this does prevent proper (multi) inheritance,
        because it would get called several times then.

        Raises:

            AttributeError if a required data keyword is missing.

        """
        if self._id is not None:
            # object created using an existing table row
            self.update()
        else:
            # Verify required data keys
            for key in self.REQUIRED:
                if key not in self._data:
                    raise AttributeError("missing required data key: %s" % key)
            self.id

    def __getattr__(self, name):
        """Obtain the 'name' attribute, where 'name' is a database column name"""
        #DEVELOPERS NOTE: if this property fails for some reason, python will
        #ignore it, and continue using the __getattr__ method. This is very
        #confusing. So if for any reason you are getting 'attribute not found'
        #errors while you don't expect it, I suggest temporarily disabling the
        #__getattr__ method until you located the problem.

        if name in self._data:
            return self._data[name]
        else:
            raise AttributeError("attribute '%s' not found" % name)

    @property
    def id(self):
        """Add or obtain an id to/from the table

        The id is generated if self._id does not exist, effectively
        creating a new row in the database.

        Several containers have their specific SQL function to create
        a new object, so this property will need to overridden.


        """
        if self._id is None:
            query = ("INSERT INTO " + self.TABLE + " (" +
                     ", ".join(self._data.iterkeys()) + ") VALUES (" +
                     ", ".join(["%s"] * len(self._data)) + ")"
                     )
            if self.database.engine == "postgresql":
                query = query + "RETURNING ID"
            values = tuple(self._data.itervalues())
            cursor = self.database.cursor
            try:
                # Insert a default source
                cursor.execute(query, values)
                if not self.database.connection.connection.autocommit:
                    self.database.connection.connection.commit()

                if self.database.engine == "monetdb":
                    self._id = cursor.lastrowid
                elif self.database.engine == "postgresql":
                    self._id = cursor.fetchone()[0]
                else:
                    raise self.database.connection.Error(
                         "Database engine not implemented in ORM.")

            except self.database.connection.Error:
                logger.warn("insertion into database failed: %s",
                             (query % values))
                raise
            except Exception as e:
                logging.error("ORM failed: %s" % str(e))
                raise
        return self._id

    def update(self, **kwargs):
        """Update attributes from database, and set database values to
        kwargs when provided

        This method performs two functions, the first always and the
        second optionally after the first:

            - it updates the attributes from the database. That is, it
              makes sure the Python instance is synchronized with the
              database.

            - (optional): it sets the column values in the database to
              the values provided through kwargs, for the associated
              database row. Attributes for the instance are of course
              also set to these values. Any kwargs that do not
              correspond to a column name are simply ignored.

        This function therefore first updates the instance from the
        database, and then optionally the database from the instance
        (with the provided keyword arguments).
        """

        self._sync_with_database()
        self._set_data(**kwargs)

    def _sync_with_database(self):
        """Update object attributes from the database"""
        results = columns_from_table(self.TABLE, keywords=None,
                                            where={self.ID: self._id})
        # Shallow copy, but that's ok: all database values are
        # immutable (including datetime objects)
        if results:
            # force to dict since sqlalchemy RowProxy doesn't have a copy
            self._data = dict(results[0]).copy()
        else:
            self._data = {}

    def _set_data(self, **kwargs):
        """Update the database with the supplied **kwargs.

        Supplied keywords that do not exist in the database will lead
        to a database error.
        """

        if not kwargs:
            return
        set_columns_for_table(self.TABLE, data=kwargs,
                                  where={self.ID: self._id})
        self._data.update(kwargs)


class DataSet(DBObject):
    """Class corresponding to the dataset table in the database"""

    TABLE = 'dataset'
    ID = 'id'
    REQUIRED = ('description',)

    def __init__(self, data=None, database=None, id=None):
        """If id is supplied, the data and image arguments are ignored."""
        super(DataSet, self).__init__(
            data=data, database=database, id=id)
        self.images = set()
        if not self.database:
            self.database = Database()
        self._init_data()

    def __str__(self):
        return 'DataSet: "%s". Database ID: %s, %d images.' % (
            self.description, str(self.id), len(self.images))

    # Inserting datasets is handled a little different than normal inserts
    # (We make use of the SQL function insertDataset)
    @property
    def id(self):
        """Add or obtain an id to/from the table
        """
        if self._id is None:
            try:
                self._id = insert_dataset(self._data['description'])
            except Exception as e:
                logger.error("ORM: error inserting dataset,  %s: %s" % (type(e).__name__, str(e)))
                raise
        return self._id

    def update_images(self):
        """Renew the set of images by getting the images for this
        dataset from the database. Implemented separately from update(),
        since normally this would be too much overhead"""
        query = "SELECT id FROM image WHERE dataset = %s ORDER BY id" % self._id
        cursor = tkp.db.execute(query)
        result = cursor.fetchall()
        image_ids = [row[0] for row in result]
        self.images = [Image(database=self.database, id=id) for id in image_ids]


class Image(DBObject):
    """Class corresponding to the images table in the database"""

    TABLE = 'image'
    ID = 'id'
    REQUIRED = ('dataset', 'tau_time', 'freq_eff', 'freq_bw', 'taustart_ts',
                'beam_smaj_pix', 'beam_smin_pix', 'beam_pa_rad',
                'deltax', 'deltay',
                'url', 'centre_ra', 'centre_decl', 'xtr_radius', 'rms_qc')

    def __init__(self, data=None, dataset=None, database=None, id=None):
        """If id is supplied, the data and image arguments are ignored."""
        super(Image, self).__init__(data=data, database=database, id=id)
        # Special part to deal when a DataSet() is supplied
        self.dataset = dataset
        self.rejected = False
        if self.dataset:
            if self.dataset.database and not self.database:
                self.database = self.dataset.database
            self.dataset.images.add(self)
            self._data.setdefault('dataset', self.dataset.id)
        self.sources = set()
        if not self.database:
            self.database = Database()
        self._init_data()
        if not self.dataset:
            self.dataset = DataSet(id=self._data['dataset'], database=self.database)

    @property
    def id(self):
        """Add or obtain an id to/from the table

        If the ID does not exist the image is inserted into the database
        """

        if self._id is None:
            args = self._data.copy()
            # somehow _data contains a garbage kwargs
            args.pop('kwargs', None)
            args['session'] = self.database.session
            try:
                image = insert_image(**args)
                self.database.session.commit()
                self._id = image.id
            except Exception as e:
                logger.error("ORM: error inserting image,  %s: %s" %
                                (type(e).__name__, str(e)))
                raise
        return self._id

    def update_sources(self):
        """Renew the set of sources by getting the sources for this
        image from the database

        This method is separately implemented, because it's not always necessary
        and potentially (for an image with dozens or more sources) time & memory
        consuming.
        """

        query = "SELECT id FROM extractedsource WHERE image = %s"
        try:
            self.database.cursor.execute(query, (self._id,))
            results = self.database.cursor.fetchall()
        except self.database.connection.Error, e:
            query = query % self._id
            logger.warn("database failed on query: %s", query)
            raise
        sources = set()
        for result in results:
            sources.add(ExtractedSource(database=self.database, id=result[0]))
        self.sources = sources


class ExtractedSource(DBObject):
    """Class corresponding to the extractedsource table in the database"""

    TABLE = 'extractedsource'
    ID = 'id'
    REQUIRED = ('image', 'zone',
                'ra', 'decl', 'ra_err', 'decl_err',
                'uncertainty_ew', 'uncertainty_ns',
                'ra_fit_err', 'decl_fit_err', 'ew_sys_err', 'ns_sys_err',
                'error_radius',
                'x', 'y', 'z',
                'racosdecl', 'det_sigma')

    def __init__(self, data=None, image=None, database=None, id=None):
        """If id is supplied, the data and image arguments are ignored."""
        super(ExtractedSource, self).__init__(
            data=data, database=database, id=id)
        # Special part to deal when an Image() is supplied
        self.image = image
        if self.image:
            if self.image.dataset.database and not self.database:
                self.database = self.image.dataset.database
            self.image.sources.add(self)
            self._data.setdefault('image', self.image.id)
        if not self.database:
            raise ValueError(
                "can't create ExtractedSource object without a Database() object")
        self._init_data()
