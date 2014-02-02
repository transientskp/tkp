"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines to deal with null detections.
"""
import logging
from collections import namedtuple

from tkp.db import general
import tkp.db


logger = logging.getLogger(__name__)


def get_nulldetections(image_id, deRuiter_r):
    """
    Returns the runningcatalog sources which:

      * Do not have a counterpart in the extractedsources of the current
        image after source association has run.
      * Have been seen (in any band) in a timestep earlier than that of the
        current image.

    NB This runs *after* the source association.

    We determine null detections only as those sources which have been
    seen at earlier times which don't appear in the current image. 
    Sources which have not been seen earlier, and which appear in 
    different bands at the current timestep, are *not* null detections.

    Output: list of tuples [(runcatid, ra, decl)]
    """
    
    # The first temptable t0 looks for runcat sources that have been seen 
    # in the same sky region as the current image, 
    # but at an earlier timestamp, irrespective of the band.
    # The second temptable t1 returns the runcat source ids for those sources 
    # that have an association with the current extracted sources.
    # The left outer join in combination with the t1.runcat IS NULL then
    # returns the runcat sources that could not be associated.
    
    query = """\
SELECT t0.id
      ,t0.wm_ra
      ,t0.wm_decl
  FROM (SELECT r.id
              ,r.wm_ra
              ,r.wm_decl
          FROM image i0
              ,assocskyrgn a0
              ,runningcatalog r0
              ,extractedsource x0
              ,image i1
         WHERE i0.id = %(image_id)s
           AND a0.skyrgn = i0.skyrgn
           AND r0.id = a0.runcat
           AND x0.id = r0.xtrsrc
           AND i1.id = x0.image
           AND i0.taustart_td > i1.taustart_ts
       ) t0
       LEFT OUTER JOIN (SELECT a.runcat
                          FROM extractedsource x
                              ,assocxtrsource a
                         WHERE x.image = %(image_id)s
                           AND a.xtrsrc = x.id
                       ) t1
       ON t0.id = t1.runcat
 WHERE t1.runcat IS NULL
"""    
    qry_params = {'image_id':image_id}
    cursor = tkp.db.execute(query, qry_params)
    results = zip(*cursor.fetchall())
    if len(results) != 0:
        return zip(list(results[1]), list(results[2]))
        #maxbeam = max(results[3][0],results[4][0]) # all bmaj & bmin are the same
    else:
        return []

