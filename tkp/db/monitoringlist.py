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
        cursor = tkp.db.execute(query, entry, commit=False)
        upd += cursor.rowcount
    tkp.db.commit()
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
