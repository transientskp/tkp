"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines to deal with flagging and monitoring
of transient candidates, mostly involving the monitoringlist.
"""
import logging
from collections import namedtuple

from tkp.db import general
import tkp.db


logger = logging.getLogger(__name__)


def get_nulldetections(image_id, deRuiter_r):
    """Returns the runcat sources that do not have a counterpart in the
    extractedsources of the current image.

    NB This is run *prior* to source association.

    We do not have to take into account associations with monitoringlist
    sources, since they have been added to extractedsources at the beginning
    of the association procedures (marked as extract_type=1 sources), and so
    they must have an occurence in extractedsource and runcat.

    Output: list of tuples [(runcatid, ra, decl)]
    """
    #The first subquery looks for extractedsources without runcat associations.
    # The second subquery looks for runcat entries we expect to see in this image.
    #NB extra clause on x.image is necessary for performance reasons.
    query = """\
SELECT r1.id
      ,r1.wm_ra
      ,r1.wm_decl
  FROM runningcatalog r1
      ,image i1
      ,runningcatalog_flux rf1
 WHERE i1.id = %(imgid)s
   AND i1.dataset = r1.dataset
   AND rf1.runcat = r1.id
   AND rf1.band = i1.band
   AND r1.id NOT IN (SELECT r.id
                       FROM runningcatalog r
                           ,extractedsource x
                           ,image i
                           ,runningcatalog_flux rf
                      WHERE i.id = %(imgid)s
                        AND x.image = i.id
                        AND x.image = %(imgid)s
                        AND i.dataset = r.dataset
                        AND rf.runcat = r.id
                        AND rf.band = i.band
                        AND r.zone BETWEEN CAST(FLOOR(x.decl - i.rb_smaj) AS INTEGER)
                                       AND CAST(FLOOR(x.decl + i.rb_smaj) AS INTEGER)
                        AND r.wm_decl BETWEEN x.decl - i.rb_smaj
                                          AND x.decl + i.rb_smaj
                        AND r.wm_ra BETWEEN x.ra - alpha(i.rb_smaj, x.decl)
                                        AND x.ra + alpha(i.rb_smaj, x.decl)
                        AND SQRT(  (x.ra - r.wm_ra) * COS(RADIANS((x.decl + r.wm_decl)/2))
                                 * (x.ra - r.wm_ra) * COS(RADIANS((x.decl + r.wm_decl)/2))
                                 / (x.uncertainty_ew * x.uncertainty_ew + r.wm_uncertainty_ew * r.wm_uncertainty_ew)
                                + (x.decl - r.wm_decl) * (x.decl - r.wm_decl)
                                 / (x.uncertainty_ns * x.uncertainty_ns + r.wm_uncertainty_ns * r.wm_uncertainty_ns)
                                ) < %(drrad)s
                    )
            AND r1.id IN(SELECT rc2.id
                           FROM runningcatalog rc2
                               ,assocskyrgn asr2
                               ,image im2
                          WHERE im2.id = %(imgid)s
                            AND asr2.skyrgn = im2.skyrgn
                            AND asr2.runcat = rc2.id
                        )
"""
    qry_params = {'imgid':image_id, 'drrad': deRuiter_r}
    cursor = tkp.db.execute(query, qry_params)
    results = zip(*cursor.fetchall())
    if len(results) != 0:
        return zip(list(results[1]), list(results[2]))
        #maxbeam = max(results[3][0],results[4][0]) # all bmaj & bmin are the same
    else:
        return []


def adjust_transients_in_monitoringlist(image_id, transients):
    """Adjust transients in monitoringlist, by either adding or
    updating them

    """
    _update_known_transients_in_monitoringlist(transients)
    _insert_new_transients_in_monitoringlist(image_id)


def _update_known_transients_in_monitoringlist(transients):
    """Update transients in monitoringlist"""
    query = """\
    UPDATE monitoringlist
       SET ra = %(wm_ra)s
          ,decl = %(wm_decl)s
      WHERE runcat = %(runcat)s
    """
    upd = 0
    for entry in transients:
        cursor = tkp.db.execute(query, entry, commit=True)
        upd += cursor.rowcount
    if upd > 0:
        logger.info("Updated %s known transients in monitoringlist" % (upd,))


def _insert_new_transients_in_monitoringlist(image_id):
    """
    Copy newly identified transients from transients table into monitoringlist.

    We grab the transients and check that their runcat ids are not in the
    monitoringlist.
    """
    query = """\
INSERT INTO monitoringlist
  (runcat
  ,ra
  ,decl
  ,dataset
  )
  SELECT t.runcat
        ,r.wm_ra
        ,r.wm_decl
        ,r.dataset
    FROM transient t
        ,runningcatalog r
        ,image i
   WHERE t.runcat = r.id
     AND r.dataset = i.dataset
     AND i.id = %(image_id)s
     AND t.runcat NOT IN (SELECT m0.runcat
                            FROM monitoringlist m0
                                ,runningcatalog r0
                                ,image i0
                           WHERE m0.runcat = r0.id
                             AND r0.dataset = i0.dataset
                             AND i0.id = %(image_id)s
                         )
"""
    cursor = tkp.db.execute(query, {'image_id': image_id}, commit=True)
    ins = cursor.rowcount
    if ins == 0:
        logger.info("No new transients inserted in monitoringlist")
    else:
        logger.info("Inserted %s new transients in monitoringlist" % (ins,))


def add_nulldetections(image_id):
    """
    Add null detections (intermittent) sources to monitoringlist.

    Null detections are picked up by the source association and
    added to extractedsource table to undergo normal processing.

    Variable or not, intermittent sources are interesting enough
    to be added to the monitoringlist.

    Insert checks whether runcat ref of source exists
    """

    # TODO:
    # Do we need to take care of updates here as well (like the adjust_transients)?
    # Or is that correctly done in update monlist

    # Optimise by using image_id for image and extractedsource
    # extract_type = 1 -> the null detections (forced fit) in extractedsource
    #Note extra clauses on image id ARE necessary (MonetDB performance quirks)
    query = """\
INSERT INTO monitoringlist
  (runcat
  ,ra
  ,decl
  ,dataset
  )
  SELECT r.id AS runcat
        ,r.wm_ra AS ra
        ,r.wm_decl AS decl
        ,r.dataset
    FROM extractedsource x
        ,image i
        ,runningcatalog r
        ,assocxtrsource a
   WHERE x.image = %(image_id)s
     AND x.image = i.id
     AND i.id = %(image_id)s
     AND i.dataset = r.dataset
     AND r.id = a.runcat
     AND a.xtrsrc = x.id
     AND x.extract_type = 1
     AND NOT EXISTS (SELECT m0.runcat
                       FROM extractedsource x0
                           ,image i0
                           ,runningcatalog r0
                           ,assocxtrsource a0
                           ,monitoringlist m0
                      WHERE x0.image = %(image_id)s
                        AND x0.image = i0.id
                        AND i0.id = %(image_id)s
                        AND i0.dataset = r0.dataset
                        AND r0.id = a0.runcat
                        AND a0.xtrsrc = x0.id
                        AND x0.extract_type = 1
                        AND r0.id = m0.runcat
                    )
"""
    cursor = tkp.db.execute(query, {'image_id': image_id}, commit=True)
    ins = cursor.rowcount
    if ins > 0:
        logger.info("Added %s forced fit null detections to monlist" % (ins,))


def add_manual_entry_to_monitoringlist(dataset_id, ra, dec):
    """
    Add manual entry to monitoringlist.

    In this case, the runcat_id defaults to null initially,
    since there is no associated source yet.
    (This is updated when we perform our first forced extraction
    at these co-ordinates.)
    """
    query = """\
INSERT INTO monitoringlist
  (ra
  ,decl
  ,dataset
  ,userentry
  )
  SELECT %s
        ,%s
        ,%s
        ,TRUE
"""
    cursor = tkp.db.execute(query, commit=True)
