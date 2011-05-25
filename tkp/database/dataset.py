"""
This module contains container objects that corresponds to a dataset
and image in the database The correspondence is matched through the
private _dsid and _imageid attributes.

Each dataset contains several database Images; database Images
correspond to the images table in the databse, *not* to sourcefinder
images or actual image data files on disk (this distinction is
important; while there are certainly parts in common, several are
not). This is in contrast to earlier versions of this module, where a
sourcefinder could basically not exist without a database.

The current setup is done in large part to keep the database and
sourcefinder (and other parts of the TKP package) separate; tightly
integrated database tables/sourcefinder images/data files make it more
difficult to improve the code or distribute parts separately. While
not tested, it seems unlikely this will have a noticable influence on
the functioning of the actual TKP pipeline (TRAP).


Usage
=====

In practice, a DataSet object is created, and separate Images are
created referencing that DataSet() instance; ids are automatically
assigned where necessary:

>>> database = tkp.database.database.DataBase()
>>> dataset = DataSet('some name', database=database)
>>> image1 = Image(dataset=dataset)  # initialize with defaults
>>> image1.tau_time
0
>>> image1.taustart_ts
datetime.datetime(1970, 1, 1, 0, 0, 0)
>>> image2 = Image(dataset=dataset, data={'tau_time': 1500,
                        'taustart_ts': datetime.datetime(2011, 5, 1, 0, 0, 0)})
>>> image2.tau_time
1500
>>> image2.taustart_ts
datetime.datetime(2011, 5, 1, 0, 0, 0)
>>> dataset.images
[<tkp.database.dataset.Image object at 0x10151ce10>,
 <tkp.database.dataset.Image object at 0x10151cc90>]

Changes in the images are immediately reflected in the database;
changes in the database, on the other hand, do require a call to
update() for the Image() instance to be updated to its corresponding
images row.

>>> image2.tau_time = 2500    # updates the database as well
>>> database.cursor.execute("SELECT tau_time FROM images WHERE imageid=%s" %
                             (image2.imageid,))
>>> database.cursors.fetchone()[0]
2500

At the moment, similar functionality is lacking for the DataSet class.


It is also possible to create a DataSet or Image instance from the
database, using the ``dsid`` or ``imageid`` in the initializer:

>>> dataset2 = DataSet(dsid=dataset.dsid)
>>> image3 = Image(imageid=image2.imageid)
>>> image3.tau_time
2500

"""

from __future__ import with_statement
import datetime
import logging


class DataSet(object):
    """
    A DataSet contains a list of Image objects which fall logically
    together as one unit: potentially from the same set of
    observations, the same HDF5 file or similar. These are therefore
    associated by having the same dataset id in the database, and thus
    the same DataSet object.
    """

    COLUMNS = dict(rerun=0, dstype=1, process_ts=datetime.datetime(1970, 1, 1),
                   dsinname='', dsoutname='', description='')

    # note: 'id' has been replaced by dsid, to avoid confusion with
    # the builtin 'id'
    def __init__(self, name='', database=None, dsid=None):
        """Create or initialize a dataset

        Kwargs:

            name (str): The DataSet name. Ignored if dsid is used to
                find the dataset in the database. The name is
                equivalent to the dsinname column in the database.

            database (tkp.database.DataBase): This contains the
                connection to the database. If None, the DataSet acts
                as a dummy object.

            dsid (int): The dataset id in the database. If None, a new
                dataset entry (row) is created in the database, and
                the current DataSet instance is assigned to it.

        Returns:

            None
        """

        self.database = database
        self.images = []
        # Database ID placeholder: see the id() method below.
        self._dsid = dsid
        self.name = name
        # Initialize the other data
        for key, value in DataSet.COLUMNS.items():
            object.__setattr__(self, '_' + key, value)
        # Create an id in the DB if not available
        if self._dsid is None:
            self.dsid
            self._set_data(data={'dsinname': self.name})
        else:
            self._update_data()
            self._update_images()

    def __setattr__(self, name, value):
        if name in DataSet.COLUMNS:
            object.__setattr__(self, '_' + name, value)
            self._set_value(name, value)
            if name == 'dsinname':
                self.name = value
        else:
            object.__setattr__(self, name, value)

    def __str__(self):
        return 'DataSet: "%s". Database ID: %s %d images.' % (
            self.name, str(self._dsid), len(self.images))

    def _set_value(self, name, value):
        if self.database and self.database.connection:
            if self._dsid:
                try:
                    # The following won't work, because the value of name
                    # gets quoted.
                    # Eg, "UPDATE datasets SET 'rerun'='2' ...", which fails
                    # #self.database.cursor.execute(
                    # #    "UPDATE datasets SET %s=%s WHERE dsid=%s",
                    # #    (name, value, self._dsid))
                    # So the command string is created first, before sending it
                    # to cursor.execute()
                    command = ("UPDATE datasets SET %s=%%s WHERE dsid=%%s" %
                               name)
                    self.database.cursor.execute(command, (value, self._dsid))
                    self.database.connection.commit()
                except self.database.Error:
                    logging.warn("Failed to set %s for DataSet with id=%s.",
                                 name, self._dsid)
                    raise

    def _set_data(self, data=None):
        """Set one or more 'columns' in the DataSet

        This is an alternative to using the direct attribute assignment
        """
        if data is None:
            data = {}
        self._rerun = data.get('rerun', self._rerun)
        self._dstype = data.get('dstype', self._dstype)
        self._process_ts = data.get('process_ts', self._process_ts)
        if 'name' in data:  # ignore 'dsinname'
            self.name = data['name']
            self._dsinname = self.name
        elif 'dsinname' in data:
            self._dsinname = data['dsinname']
            self.name = self._dsinname
        self._dsoutname = data.get('dsoutname', self._dsoutname)
        self._description = data.get('description', self._description)
        if self._dsid:
            try:
                self.database.cursor.execute("""\
UPDATE datasets
  SET rerun=%s, dstype=%s, process_ts=%s, dsinname=%s, dsoutname=%s,
      description=%s
WHERE dsid=%s""", (self._rerun, self._dstype, self._process_ts, self._dsinname,
                   self._dsoutname, self._description, self._dsid))
                self.database.connection.commit()
            except self.database.Error:
                logging.warn("Failed to set data for with id=%s.",
                             self._dsid)
                raise

    def _update_data(self):
        """Retrieve data from database. This (re)sets the members,
        including the name"""
        try:
            self.database.cursor.execute("""\
SELECT rerun, dstype, process_ts, dsinname, dsoutname, description
FROM datasets
WHERE dsid=%s""", (self._dsid,))
        except self.database.Error:
            logging.warn("""\
Failed to retrieve data from the database for dataset ID = %s""", self._dsid)
            raise
        results = self.database.cursor.fetchone()
        self._rerun, self._dstype, self._process_ts = results[:3]
        self._dsinname, self._dsoutname, self._description = results[3:]
        self.name = self._dsinname

    def _update_images(self):
        """Update the list of images to those found in the database for
        this dataset"""

        try:
            self.database.cursor.execute(
                """SELECT imageid FROM images WHERE ds_id=%s""",
                (self._dsid,))
            for imageid in self.database.cursor.fetchall():
                Image(dataset=self, imageid=imageid[0])
        except self.database.Error:
            raise

    @property
    def dsid(self):
        """Add a dataset ID to the database

        A dataset will be added to the database. A dataset id will be
        generated for every dataset name. If the name already exists the
        rerun value in the table will be incremented by 1. If the database is
        not enabled the id is set to "None".

        The stored function insertDataset() is called. It takes the name as
        input and returns the generated id.
        """

        if self._dsid is None:
            try:
                self.database.cursor.execute(
                    """SELECT insertDataset(%s)""", (self.name,))
                self.database.connection.commit()
                self._dsid = int(self.database.cursor.fetchone()[0])
            except self.database.Error:
                logging.warn("Insert DataSet %s failed.", self.name)
                raise
        return self._dsid


class Image(object):
    """Class corresponding to the image table in the database"""

    COLUMNS = dict(tau_time=0., freq_eff=0., freq_bw=0.,
                   taustart_ts=datetime.datetime(1970, 1, 1),
                   url='')

    def __init__(self, dataset, imageid=None, data=None):
        """Create an Image object filled with relevant image data

        Args:

            dataset (tkp.database.dataset.DataSet): The
                DataSet instance in which the image is stored. This
                also takes care of the database access, since this is
                done through the dataset. If None, no database
                interaction is possible, and the dataset (and the
                obtainment of an imageid) has to be done manually.

        Kwargs:

            imageid (int or None): the id of the image (row) in the
                database. If None, an id will be created once the data
                is stored with Image().store()

            data (dict or None): A dict with the relevant image
                data. The keys correspond to the columns in the
                database table, except for imageid. Keys not present
                will be filled with a default empty value ('', 0 or None),
                while extra keys not present in the table are
                ignored. If data is None, an empty dict is used.

                Available keys are:

                - tau_time (float)

                - freq_eff (float)

                - freq_bw (float)

                - taustart_ts (datetime.datetime)

                - url (str)

        Returns:

            (None)

        """

        if not isinstance(dataset, DataSet):
            raise TypeError("dataset should be of type Dataset")
        self.dataset = dataset
        self.dataset.images.append(self)
        self._imageid = imageid
        if self._imageid is None:
            for key, value in Image.COLUMNS.items():
                setattr(self, key, value)
            self.imageid
            self._set_data(data=data)
        else:
            self._retrieve_from_database()

    def __getattr__(self, name):
        if name in Image.COLUMNS.keys():
            return getattr(self, '_' + name)

    def __setattr__(self, name, value):
        if name in Image.COLUMNS.keys():
            object.__setattr__(self, '_' + name, value)
            self._set_value(name, value)
            if name == 'dsinname':
                self.name = value
        else:
            object.__setattr__(self, name, value)

    def _set_data(self, data=None):

        if data is None:
            data = {}
        self._tau_time = data.get('tau_time', self._tau_time)
        self._freq_eff = data.get('freq_eff', self._freq_eff)
        self._freq_bw = data.get('freq_bw', self._freq_bw)
        self._taustart_ts = data.get('taustart_ts', self._taustart_ts)
        self._url = data.get('url', self._url)

        connection = self.dataset.database.connection
        cursor = self.dataset.database.cursor
        if self._imageid:
            try:
                cursor.execute("""\
UPDATE images
    SET tau_time=%s, freq_eff=%s, freq_bw=%s, taustart_ts=%s, url=%s
WHERE imageid=%s""", (self.tau_time, self.freq_eff, self.freq_bw,
                      self.taustart_ts, self.url, self.imageid))
                connection.commit()
            except self.dataset.database.Error:
                logging.warn("Failed to set data for Image with id=%s.",
                             self._imageid)
                raise

    def _set_value(self, name, value):
        if (self.dataset is not None and self.dataset.database and
            self.dataset.database.connection):
            connection = self.dataset.database.connection
            cursor = self.dataset.database.cursor
            if self._imageid:
                try:
                    command = ("UPDATE images SET %s=%%s WHERE imageid=%%s" %
                               name)
                    cursor.execute(command, (value, self._imageid))
                    connection.commit()
                except self.dataset.database.Error:
                    logging.warn("Failed to set %s for Image with id=%s.",
                                 name, self._imageid)

    def _retrieve_from_database(self):
        """Fill in the image details from a database image table entry"""

        cursor = self.dataset.database.cursor
        cursor.execute("""\
SELECT tau_time, freq_eff, freq_bw, taustart_ts, url FROM images
WHERE imageid=%s""" % (self._imageid,))
        results = cursor.fetchone()
        self._tau_time = results[0]
        self._freq_eff = results[1]
        self._freq_bw = results[2]
        self._taustart_ts = results[3]
        self._url = results[4]

    @property
    def imageid(self):
        """Add or obtain an imageid to/from the images table"""

        connection = self.dataset.database.connection
        cursor = self.dataset.database.cursor
        if self._imageid is None:
            try:
                # Insert a default image
                cursor.execute("""\
INSERT INTO
    images (ds_id, tau, band, tau_time, freq_eff, freq_bw, taustart_ts, url)
    VALUES (%s, 0, 0, %s, %s, %s, %s, %s)""",
                             (self.dataset.dsid, self.tau_time, self.freq_eff,
                              self.freq_bw, self.taustart_ts, self.url))
                connection.commit()
                self._imageid = self.dataset.database.cursor.lastrowid
            except self.dataset.database.Error:
                logging.warn("Insertion of Image() failed.")
                raise
        return self._imageid

    def update(self):
        """Update the image if the database has changed"""

        # In the future, should this be done automatically
        # and instanteneously?

        self._retrieve_from_database()
