.. _stage-persistence:

=================
Persistence stage
=================

(See also the :ref:`relevant configuration parameters<job_params_persistence>`.)

A record of all images to be processed is made in the database. Within the
database, images are sorted into :ref:`datasets <schema-dataset>`, which group
related images together for processing: searches for transients are performed
between images in a single databset, for instance. All images being processed
are added to the same dataset.

Optionally, a copy of the image pixel data may be stored to a :ref:`MongoDB
<mongodb-intro>` instance at the same time. This is configured in
the :ref:`image_cache section <pipeline_cfg_image_cache>` of the pipeline config.

Note that only images which meet the :ref:`data accessor <accessors>`
requirements are stored in the database. Any other data provided to the
pipeline will be processed: an error will be logged, and that data will not be
included in further processing.

