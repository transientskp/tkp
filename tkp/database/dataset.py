# -*- coding: utf-8 -*-

#
# LOFAR Transients Key Project
#
# Evert Rol
#
# discovery@transientskp.org
#
#
# Simplified miniature ORM to deal with the most basic and essential
# database tables.
#

"""
This module contains container objects that corresponds to a dataset,
image or extracted source in the database; it is actually a mini
Object Relation Mapper (ORM). The correspondence between the object
and table row is matched through the private _id attributes.

Each dataset contains several database Images; each Image contains a
number of ExtractedSources. The database Images correspond to the
images table in the database, *not* to sourcefinder images or actual
image data files on disk (this distinction is important; while there
are certainly parts in common, several are not).


The current setup is done in large part to keep the database and
sourcefinder (and other parts of the TKP package) separate; tightly
integrated database tables/sourcefinder images/disk files make it more
difficult to improve the code or distribute parts separately. While
not tested, it seems unlikely this will have a noticable influence on
the functioning of the actual TKP pipeline (TraP).

Every container object inherits from DBObject, which forms the
starting point for any new container objects created. See the doc
strings for DBOject for more information on how to do this.

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
    >>> database = tkp.database.database.DataBase()

    # Each object type takes a data dictionary on creation, which for newly objects
    # has some required keys (& values). For a DataSet, this is only 'inname';
    # for an Image, the keys are 'freq_eff', 'freq_bw_', 'taustart_ts',
    # 'tau_time' & 'url'
    # The required values are stored in the the REQUIRED attribute
    >>> dataset = DataSet(data={'inname': 'a dataset'}, database=database)

    # Here, dataset indirectly holds the database connection:
    >>> dataset.database
    DataBase(host=heastro1, name=trap, user=trap, ...)
    >>> image1 = Image(data={'freq_eff': '80e6', 'freq_bw': 1e6,
        'taustart_ts': datetime(2011, 5, 1, 0, 0, 0), 'tau_time': 1800., 'url': '/'},
        dataset=dataset)  # initialize with defaults
        # note the dataset kwarg, which holds the database connection
    >>> image1.tau_time
    1800.
    >>> image1.taustart_ts
    datetime.datetime(2011, 5, 1, 0, 0, 0)
    >>> image2 = Image(data={'freq_eff': '80e6', 'freq_bw': 1e6,
        'taustart_ts': datetime(2011, 5, 1, 0, 1, 0), 'tau_time': 1500., 'url': '/'},
        dataset=dataset)
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
    >>> database.cursor.execute("SELECT tau_time FROM images WHERE imageid=%s" %
                                 (image2.id,))
    >>> database.cursors.fetchone()[0]
    2500
    # Manually update the database
    >>> database.cursor.execute("UPDATE images SET tau_time=2000.0 imageid=%s" %
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

from __future__ import with_statement
import datetime
import logging
import utils as dbu
import monetdb.sql as db
from ..config import config
from .database import ENGINE


DERUITER_R = config['source_association']['deruiter_radius']


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
        # Get here when 'name' is not found as attribute
        # That likely means it is stored in self._data
        try:
            return self._data[name]
        except KeyError:
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
                     ", ".join(["%s"] * len(self._data)) + ")")
            if ENGINE == 'postgresql':
                query += " RETURNING " + self.ID
            values = tuple(self._data.itervalues())
            cursor = self.database.cursor
            try:
                # Insert a default source
                cursor.execute(query, values)
                if not self.database.autocommit:
                    self.database.connection.commit()
                self._id = cursor.lastrowid
                if ENGINE == 'postgresql':
                    self._id = cursor.fetchone()[0]
            except self.database.Error:
                logging.warn("insertion into database failed: %s",
                             (query % values))
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
        results = dbu.columns_from_table(
            self.database.connection, self.TABLE, keywords=None,
            where={self.ID: self._id})
        # Shallow copy, but that's ok: all database values are
        # immutable (including datetime objects)
        self._data = results[0].copy()

    def _set_data(self, **kwargs):
        """Update the database with the supplied **kwargs.

        Supplied keywords that do not exist in the database will lead
        to a database error.
        """

        if not kwargs:
            return
        dbu.set_columns_for_table(self.database.connection, self.TABLE,
                                  data=kwargs, where={self.ID: self._id})
        self._data.update(kwargs)
        

class DataSet(DBObject):
    """Class corresponding to the dataset table in the database"""

    TABLE = 'dataset'
    ID = 'id'
    REQUIRED = ('inname',)
    
    def __init__(self, data=None, database=None, id=None):
        """If id is supplied, the data and image arguments are ignored."""
        super(DataSet, self).__init__(
            data=data, database=database, id=id)
        self.images = set()
        if not self.database:
            raise ValueError(
                "can't create DataSet object without a DataBase() object")
        self._init_data()

    def __str__(self):
        return 'DataSet: "%s". Database ID: %s %d images.' % (
            self.name, str(self._dsid), len(self.images))

    # Inserting datasets is handled a little different than normal inserts
    # (We make use of the SQL function insertDataset)
    @property
    def id(self):
        """Add or obtain an id to/from the table

        This uses the SQL function insertDataset().
        """

        if self._id is None:
            try:
                self._id = dbu.insert_dataset(self.database.connection,
                                              self._data['inname'])
            except self.database.Error, e:
                logging.warn("insertion of DataSet() into the database failed")
                raise
        return self._id

    # Get all images from database; implemented separately from update(),
    # since normally this would be too much overhead
    def update_images(self):
        """Renew the set of images by getting the images for this
        dataset from the database"""

        query = "SELECT id FROM image WHERE dataset = %s"
        try:
            self.database.cursor.execute(query, (self._id,))
            results = self.database.cursor.fetchall()
        except db.Error, e:
            query = query % self._id
            logging.warn("database failed on query: %s", query)
            raise
        images = set()
        for result in results:
            images.add(Image(database=self.database, id=result[0]))
        self.images = images
                           
    # TO DO: Verify constants
    def detect_variables(self,  V_lim=0.2, eta_lim=3.):
        """Search through the whole dataset for variable sources"""

        return dbu.detect_variable_sources(
            self.database.connection, self._id, V_lim, eta_lim)


class Image(DBObject):
    """Class corresponding to the images table in the database"""

    TABLE = 'image'
    ID = 'id'
    REQUIRED = ('dataset', 'tau_time', 'freq_eff', 'freq_bw', 'taustart_ts')
    
    def __init__(self, data=None, dataset=None, database=None, id=None):
        """If id is supplied, the data and image arguments are ignored."""
        super(Image, self).__init__(
            data=data, database=database, id=id)
        # Special part to deal when a DataSet() is supplied
        self.dataset = dataset
        if self.dataset:
            if self.dataset.database and not self.database:
                self.database = self.dataset.database
            self.dataset.images.add(self)
            self._data.setdefault('dataset', self.dataset.id)
        self.sources = set()
        if not self.database:
            raise ValueError(
                "can't create Image object without a DataBase() object")
        self._init_data()

    # Inserting images is handled a little different than normal inserts
    # -- We call an SQL function 'insertImage' which takes care of  
    #    assigning a new image id.
    @property
    def id(self):
        """Add or obtain an id to/from the table

        This uses the SQL function insertImage()
        """

        if self._id is None:
            try:
                if 'bsmaj' not in self._data:
                    self._data['bsmaj']=None
                    self._data['bsmin']=None
                    self._data['bpa']=None
                # Insert a default image
                self._id = dbu.insert_image(
                    self.database.connection, self.dataset.id,
                    self._data['freq_eff'], self._data['freq_bw'],
                    self._data['taustart_ts'],self._data['tau_time'],
                    self._data['bsmaj'],self._data['bsmin'],  
                    self._data['bpa'],
                    self._data['url'],
                )
            except self.database.Error, e:
                logging.warn("insertion of Image() into the database failed")
                raise
        return self._id

    # Get all sources from database; implemented separately from update(),
    # since normally this would be too much overhead
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
        except db.Error, e:
            query = query % self._id
            logging.warn("database failed on query: %s", query)
            raise
        sources = set()
        for result in results:
            sources.add(ExtractedSource(database=self.database, id=result[0]))
        self.sources = sources

    def insert_extracted_sources(self, results):
        """Insert a list of sources

        Args:

            results (list): list of
                utility.containers.ExtractionResult objects (as
                returned from
                sourcefinder.image.ImageData().extract()), or a list
                of data tuples with the source information as follows:
                (ra, dec,
                ra_err, dec_err, 
                peak, peak_err, 
                flux, flux_err,
                significance level,
                beam major width (as), beam minor width(as),
                beam parallactic angle).
       """
       #To do: Figure out a saner method of passing the results around
       # (Namedtuple, for starters?)
       
        dbu.insert_extracted_sources(
            self.database.connection, self._id, results=results)
        
    def associate_extracted_sources(self, deRuiter_r=DERUITER_R):
        """Associate sources from the last images with previously
        extracted sources within the same dataset

        Args:

            deRuiter_r (float): The De Ruiter radius for source
                association. The default value is set through the
                tkp.config module
        """
        dbu.associate_extracted_sources(
            self.database.connection, self._id, deRuiter_r)

    def monitoringsources(self):
        return dbu.monitoringlist_not_observed(self.database.connection,
                                               self._id)

    def insert_monitoring_sources(self, results):
        """Insert the list of measured monitoring sources for this image into
        extractedsource and runningcatalog

        Note that the insertion into runningcatalog can be done by
        xtrsrc_id from monitoringlist. In case it is negative, it is
        appended to runningcatalog, and xtrsrc_id is updated in the
        monitoringlist.
        """

        dbu.insert_monitoring_sources(self.database.connection, results,
                                      self._id)
        
        
class ExtractedSource(DBObject):
    """Class corresponding to the extractedsource table in the database"""

    TABLE = 'extractedsource'
    ID = 'id'
    REQUIRED = ('image', 'zone', 'ra', 'decl', 'ra_err', 'decl_err',
                'x', 'y', 'z', 'det_sigma')

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
                "can't create ExtractedSource object without a DataBase() object")
        self._init_data()

    def lightcurve(self):
        """Obtain the complete light curve (within the current dataset)
        for this source.

        Returns:

            (list) list of 5-tuples, each tuple being:

                - observation start time as a datetime.datetime object

                - integration time (float)

                - peak flux (float)

                - peak flux error (float)

                - database ID of this particular source
        """

        return dbu.lightcurve(self.database.connection, self._id)
