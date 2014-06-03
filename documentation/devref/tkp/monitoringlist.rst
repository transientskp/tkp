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
detected (i.e., their flux is above the detection level). 
The list is provided only externally in two ways, either as a tuple of 
source positions (ra,dec) on the command line or by a file containing
the source positions. The sources can have their coordinates derived
from e.g. optical or X-ray observations, and it is therefore important
that these exact coordinates will be used in the flux
measurements. 

The monitoring list is active for the duration of a "dataset" entity
(as implemented in the database), which may span a single observation,
but certainly could span multiple observations of the same field. It
is user defined.


Database tables
---------------

The database tables concerned are three:

- runningcatalog: this is the growing list of detected sources, with
  their weighted averaged coordinates. This catalog is tied to a
  dataset, as mentioned before. Sources from the monitoring list
  are the special property of ``mon_src = true`` set.

- extractedsources: forced fits at the positions of the monitoring sources
  are added to this table for every image. To discriminate these from the 
  blind and null detections, the monitoring sources have the attribute
  ``extract_type = 2`` set.

- assocxtrsource: the light curve of the monitoring sources are maintained
  in this table. All associations are of the type 1-to-1, so monitoring sources
  not associated or mixed up with the blind and/or null detections.


Program flow
------------

Below, the flow of pipeline in the context of the monitoringlist is
indicated.


1. Recipe: monitoringlist

  a. It should be noted that the monitoring list procedures run a
     after the `normal` association procedures of the blindly extracted
     sources and null detections are completed.
  
  b. Obtain the list of source positions to be monitored that were 
     provided at the start of a pipeline run.

  c. Measure the flux levels at the given positions (forced fit) in
     every image, if it is in the field of view.
 
  d. Insert the fluxes into the `extractedsources` as ``extract_type = 2``, 
     and associate with `runningcatalog` sources that are marked as 
     monitoring sources (``mon_src = true``) for 1-to-1 light curves.

  e. Association of the extracted monitoring sources with the known
     monitoring sources in the runningcatalog are carried out. Only 
     1-to-1 associations are done. Together with the counterpart ids 
     are the variability indices stored for every image timestep.
     The average positions for the ``mon_src`` `runningcatalog` will
     not be updated, since at these the positions are fixed.


2. Recipe: transient_search

  a. New (and current) transients are searched for by calculating the
     deviation from a flat light curve.

  b. Newly found transients are added to the transient table. Known 
     transients in the table are updated.
