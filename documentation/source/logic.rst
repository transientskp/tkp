.. _logic:

****************************
Trap logic flow overview
****************************

.. |last_updated| last_updated::
:Last updated: |last_updated|


This page gives a step-by-step breakdown of what the trap scripts actually do,
along with a quick summary of the command line arguments.
For more detail on arguments, or just a reminder at the command line, try:: 

    trap-script.py --help

at the command line.

Currently there is only one trap script in operation, :py:mod:`trap-images.py`.

=========================
:py:mod:`trap-images.py`
=========================

Command line args
-------------------

**Monitor coords**

  Manually define co-ordinates for flux monitoring, by typing them in at the command line.

  Examples::

    -m [[RA1,DEC1]]
    -m [[RA1,DEC1],[RA2,DEC2]]
    --monitor-coords=[[RA1,DEC1],[RA2,DEC2]]

      

**Monitor list**

  Same as monitor coords, but specify a file containing the coordinates, rather than list them at the command line.

  Examples::

    -l monitor_list.txt
    --monitor-list=monitor_list.txt

  Where :file:`monitor_list.txt` either contains exactly the same contents as the command line entry, or if you prefer, 
  the same but with extra whitespace e.g.
  
  :file:`monitor_list.txt`::

    [
    [RA1, DEC1], 
    [RA2, DEC2], 
    ]


**Dataset Id**
  Specifies a previous dataset to add measurements to, e.g.::

    --dataset-id=12


Main logic flow
----------------

.. To do: update documentation for each recipe, link to them here...

For :py:data:`image` in :py:data:`input_list`, run:
 * :py:mod:`source_extraction.py`  (includes per-image-association)
 * :py:mod:`monitoringlist.py` (includes first search for transient candidates)
 * :py:mod:`transient_search.py` (lightcurve variability analysis) 
 * :py:mod:`feature_extraction.py` (Attempt to characterise our transients)
 * :py:mod:`classification.py` (Basically a placeholder currently).
 * :py:mod:`prettyprint.py`

