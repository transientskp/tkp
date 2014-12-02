

Forced source-fitting
=====================
When the :ref:`source association <stage-association>` stage is complete,
the pipeline proceeds to handle forced-fits. These may be required either for
measuring 'null detections' or sources added to the monitoringlist.

.. _stage-nulldet:

Null detection handling
-----------------------

A "null detection" is the term used to describe a source which was expected to
be measured in a particular image (because it has been observed in previous
images covering the same field of view) but was in fact not detected by the
:ref:`blind extraction <stage-extraction>` step.

After the blindly-extracted source measurements have been stored to the
database and have been associated with the known sources in the running
catalogue, the null detection stage starts.
We retrieve from the database a list of sources that serve as the null detections.
Sources on this list come from the :ref:`schema-runningcatalog` and

* Do not have a counterpart in the extractedsources of the current
  image after source association has run.
* Have been seen (in any band) at a timestamp earlier than that of the
  current image.

We determine null detections only as those sources which have been
seen at earlier times which don't appear in the current image. 
Sources which have not been seen earlier, and which appear in 
different bands at the current timestep, are *not* null detections,
but are considered as "new" sources.

For all sources identified as null detections, we measure fluxes by performing
a forced elliptical Gaussian fit to the expected source position on the image.
The procedure followed is similar to that used for :ref:`blind extraction
<stage-extraction>`, but rather than allowing the pixel position of the
barycentre to vary freely, it is held to the known source position. No
deblending is performed.

The results of these "forced" source measurements are marked as such and
appended to the database.

After being added to the database, the forced fits are matched back to their
running catalog counterparts in order to append it as a datapoint in the light curve.
This matching is does not include the De Ruiter radius, since the source position came 
from the running catalog. 
It is sufficient to use the weighted positional error as a cone search, since the positions are identical.
Therefore the forced fit position is not included as 
an extra datapoint in the position of the running catalog.
The fluxes, however, are included into the statistical properties and the values are updated.

It is worth emphasizing that the above procedure guarantees that
every known source will have either a blind detection or a forced-fit
measurement in every image from the moment it was detected for the 
first time. 

Null-detection depends upon the same
:ref:`job configuration file <job_params_cfg>` parameters as the
:ref:`"blind" source-extraction stage<stage-extraction>`.

.. _stage-monitoringlist:

Monitoringlist
--------------
If monitoringlist positions have been specified when
:ref:`running a job<trap-manage-run>`,
then these are always force-fitted whenever an image's source-extraction region
contains the designated co-ordinates.
These forced fits are used to build up a special
:ref:`schema-runningcatalog` entry which is excluded from association with
regular extractions.