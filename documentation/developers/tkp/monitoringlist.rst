.. _monitoringlist:

Monitoring list
===============
.. |last_updated| last_updated::

:author: Evert Rol
:Last updated: |last_updated|


Introduction
------------

The monitoring list is a list of sources that require the flux to be
measured at the given source position, regardless of actually being
detected (i.e., their flux is above the detection level). The list is
normally made in two distinct ways: detected transients will be
inserted by the pipeline into this list automatically if not already
present (here type I), and sources can be externally added (here type
II). The latter type II sources can have their coordinates derived
from e.g. optical or X-ray observations, and it is therefore important
that these exact coordinates will be used in the flux
measurements. The former type I sources will have updated coordinates
as long as they are detected, since every single measurement of these
transients results in a position that is combined to produced weighted
mean coordinates.

The monitoring list is active for the duration of a "dataset" entity
(as implemented in the database), which may span a single observation,
but certainly could span multiple observations of the same field. This
is often user defined.


Database tables
---------------

The database tables concerned are three:

- monitoringlist: naturally, this holds the list of currently
  monitored sources. One column flags whether the source was user
  inserted (type II) or not (type I). An ID key points to the
  runningcatalog for the coordinates of type I sources. An image ID
  column gives the last image for which this source was detected.

- runningcatalog: this is the growing list of detected sources, with
  their weighted averaged coordinates. This catalog is tied to a
  dataset, as mentioned before.

- extractedsources: less relevant, this table contains detected
  sources for each individual image.

The actual columns in `monitoringlist` are: 

  + `monitorid`: the primary key.

  + `xtrsrc_id`: the key that points to the runningcatalog. This is
    used to obtain the coordinates from the `runningcatalog` for type
    I sources. It can be negative (not used) when type II sources are
    newly inserted and have not yet been measured; once measured, such
    sources also end up in the runningcatalog (even when below the
    detection threshold) and `xtrsrc_id` will be set to that, but is
    otherwise not used.

  + `ra` and `decl`: the positions of the sources (default 0, 0). Only
    used for type II sources.

  + `userentry`: boolean field denoting whether the source was user
    inserted (type II) or not (type I).

  + `image_id`: refers to the last image for which the monitoringlist
     has been updated. This is to know which positions have not yet
     been measured in the current image.


Program flow
------------

Below, the flow of pipeline in the context of the monitoringlist is
indicated.


1. Recipe: sourcefinder

  a. Sources are blindly detected above a certain threshold.

  b. Found sources are inserted into the database

  c. Found sources are matched against previous sources, building light
     curves and updating the positions in runningcatalog. Newly found
     sources are added to the runningcatalog.

  d. Found sources are matched against those in the monitoringlist. Sources
     that have no match yet (`xtrsrc_id` < 0), have their xtrsrc_id
     updated.
     
     The `image_id` column is updated for all matched sources. This
     flags these sources as already found.


2. Recipe: monitoringlist

  a. Obtain a list of sources that have not been detected in the
     current image (the `image_id` does not equal the current
     image). These sources are both type I and type II sources.

  b. Measure the flux levels at the given positions.
 
  c. Insert the fluxes into the `extractedsources`, and associate with
     `runningcatalog` for light curves.

  d. No attempt is made to associate the current "sources" (all below
     the detection threshold) with an existing catalog; nor will the
     average positions in `runningcatalog` be updated, since at these
     (presumably low) flux levels, the positional errors will be large
     and add only noise.

     The association of the extracted sources with the
     `runningcatalog` is simpler, since all these extracted sources
     come indirectly from the `monitoringlist`, and the latter holds
     an `xtrsrc_id` reference to the `runningcatalog`; matching can be
     done using the ids. (New "user" defined sources (xtrsrc_id < 0)
     are not matched, but inserted as a new source into the
     runningcatalog.)

     (In practice, the id association is somewhat harder, because of
     limitations in SQL. For details, see the source in
     database.utils.py.)

  e. The `image_id` column in the monitoringlist is updated.


3. Recipe: transient_search

  a. New (and current) transients are searched for by calculating the
     deviation from a flat light curve.

  b. Newly found transients are added to the monitoringlist.
