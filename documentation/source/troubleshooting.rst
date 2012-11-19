.. _troubleshooting:

Troubleshooting the pipeline
============================
.. |last_updated| last_updated::
:Last updated: |last_updated|

This section deals with errors that may occur when running the
pipeline, either caused by incorrect use of recipes (eg, incorrect
parameter settings) or some fault in the overall pipeline usage. Of
course, pipeline breakage may also be because of a bug introduced in a
recent version, for which this section may still help debugging this
problem (to provide proper feedback to the actual
developers). Further, non-operational databases or bad input data
files may lead, at times, to confusing errors: it may look like a
recipe failed, while the cause is some dependency that is external to
the pipeline. In the case of bad data files, in can often help to see
if the errors shows up for every compute node, or just a few (those
with the bad data).


The obvious point to start looking for the cause of errors is the log;
remember that the log files are archived by timestamps in the
:file:`logs` directory for each "job". There will generally be a
traceback at the end of the pipeline run in case of an error; this
traceback, however, is generally on the front end (the master node)
and will rarely include the actual error that caused the pipeline to
fail. One has to go a bit further up to find the traceback of a node
recipe if that has failed, which will already be more indicative of
the error. That, however, will also not always point directly to the
error: in case of an external process launched on the compute nodes,
the pipeline will just indicate that the external process failed to
complete. One should go even further back up to see why that external
process failed. In case there were multiple processes running on
multiple nodes, that could mean going through the logging output of a
lot of processes to find this one error. Luckily, a (backward) search
for `ERROR` will often lead one directly to the actual error in such
cases.


Common errors
-------------

BBS: inconsistent time axis
  ::

    2012-01-06 15:19:10 DEBUG   trap-with-trip.bbs.GlobalControl: ERROR - [CalSessionException: Time axis inconsistent for kernel process: heastro1:24906]

  This error occurs when several subbands, after having passed through
  NDPPP, do not have identical begin and end times. The next step in
  the imaging pipeline, BBS, expects these times to be equal across
  all subbands, and when this is not the case, the above error will
  occur.

  To verify that non-identical begin or end times are indeed the cause of
  this crash, have a look at global VDS file :file:`vds/bbs.gvds`:
  this file should have all the start and end times of the used
  subbands, so it will be easy to see if these are all the same or not.

  One way to solve this problem, is to specify the start and end times
  to be used in the :file:`tasks.cfg`, eg::

    [ndppp]
    ...
    data_start_time=2010/10/09/09:04:00.000
    data_end_time=2010/10/09/13:03:00.000
      
  Alternatively, you could obtain these values from the VDS file and
  insert them within the recipe, as shown `here
  <http://lus.lofar.org/documentation/pipeline/pipelines/sip/recipes/sip.html>`_. While
  this is more flexible, there is the change that the resultant times
  are the maximum values, which will then cause NDPPP to crash instead
  on subbands with a shorter time range.

