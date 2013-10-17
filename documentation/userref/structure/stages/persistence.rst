.. _stage-persistence:

+++++++++++
Persistence
+++++++++++

A record of all images to be processed is made in the database. Within the
database, images are sorted into :ref:`datasets <dataset>`, which group
related images together for processing: searches for transients are performed
between images in a single databset, for instance. All images being processed
are added to the same dataset.

Optionally, a copy of the image pixel data may be stored to a :ref:`MongoDB
<mongodb-intro>` instance at the same time.

The following parameters may be configured in the :ref:`job configuration file
<job_params_cfg>`:

Section ``persistence``
-----------------------

``dataset_id``
   Integer. Specifies the unique ID of a dataset to which the current pipeline
   run should be appended. If ``-1``, a new dataset is created.

``description``
   String. The name under which the database will be stored in the database.
   This value is only used if a new dataset is constructed (see
   ``dataset_id``, below).

``copy_images``
   Boolean. If ``True``, image pixel data will be stored to a MongoDB database.

``mongo_host``, ``mongo_port``
   String, integer. Network hostname and port to use to connect to MongoDB.
   Only used if ``copy_images`` is ``True``.

``mongo_db``
   String. Name of MongoDB database in which to store image pixel data. Only
   used if ``copy_images`` is ``True``.
