"""
A collection of back end subroutines (mostly SQL queries).

This module contains the routines dealing with analysis of transients,
mostly involving the 'transient' table.

"""
import os
import sys
import math
import logging
import monetdb.sql as db
from tkp.config import config


AUTOCOMMIT = config['database']['autocommit']
DERUITER_R = config['source_association']['deruiter_radius']
BG_DENSITY = config['source_association']['bg-density']



def insert_transient(conn, transient, dataset, images=None):
    """Insert a transient source in the database.
    Transients are stored in the transients table, as well as in
    the monitoring list.

    A check is performed where the base id (asocxtrsources.runcat)
    for the light curve of the transient is queried, by assuming the
    current srcid falls within a light curve
    (assocxtrsource.xtrsrc = srcid). If this id already in the
    table, we replace that transient by this one.

    The reason we check the assocxtrsource, is that when there is a
    1-to-many source match, the main source id (as stored in the
    runningcatalog) may change; this results in transients already
    stored having a different id than the current transient, while
    they are in the fact the same transient. The runcat of the
    stored id, however, should still be in the light curve of the new
    runcat, as an xtrsrc. We thus update the transient,
    and replace the current transients.xtrsrc by the new srcid
    (=assocxtrsource.xtrsrc)

    We store the transient in the monitoring list to ensure its flux
    will be measured even when the transient drops below the detection
    threshold.
    """

    srcid = transient.srcid
    cursor = conn.cursor()
    try:  # Find the possible transient associated with the current source
        query = """\
        SELECT id 
          FROM transient
         WHERE runcat = %s
        """
        cursor.execute(query, (srcid,))
        transientid = cursor.fetchone()
        if transientid:  # update/replace existing source
            query = """\
            UPDATE transient
               SET runcat = %s
                  ,eta = %s
                  ,V = %s
             WHERE id = %s
            """
            cursor.execute(query, (srcid, transient.eta, transient.V, transientid[0]))
        else:  # insert new source
            # First, let'find the current xtrsrc_id that belongs to the
            # current image: this is the trigger source id
            if images is None:
                image_set = ""
            else:
                image_set = ", ".join([str(image) for image in images])
            query = """\
            SELECT ex.id 
              FROM extractedsource ex
                  ,assocxtrsource ax
             WHERE ex.image IN (%s) 
               AND ex.id = ax.xtrsrc 
               AND ax.runcat = %%s
            """ % image_set
            cursor.execute(query, (srcid,))
            trigger_srcid = cursor.fetchone()[0]
            query = """\
            INSERT INTO transient
              (runcat
              ,eta
              ,V
              ,trigger_xtrsrc
              )
            VALUES 
              (%s
              ,%s
              ,%s
              ,%s
              )
            """
            cursor.execute(query, (srcid, transient.eta, transient.V, trigger_srcid))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        logging.warn("Query %s failed", query)
        logging.debug("Query %s failed", query)
        cursor.close()
        raise
    try:
        #TODO: File a MonetDB bug report, since
        # no two fk can be inserted
        query = """\
        INSERT INTO monitoringlist
          (runcat
          ,ra
          ,decl
          ,dataset
          )
          SELECT r.id
                ,0
                ,0
                ,%s
            FROM runningcatalog r
           WHERE r.id = %s
        """
        cursor.execute(query, (dataset, srcid))
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        query = query % (dataset,srcid)
        logging.warn("Failed on query:\n%s" % query)
        cursor.close()
        raise
    cursor.close()



def _select_variability_indices(conn, dsid, V_lim, eta_lim):
    """Select sources and variability indices in the running catalog

    This comes relatively easily, since we have kept track of the
    average fluxes and the variance measures, and thus can quickly
    obtain any sources that exceed a constant flux by a certain amount.

    Args:

        dsid (int): dataset of interest

        V_lim ():

        eta_lim ():
    """

    # To do: explain V_lim and eta_lim
    
    results = []
    cursor = conn.cursor()
    try:
        query = """\
SELECT runcat
      ,dataset
      ,f_datapoints
      ,wm_ra
      ,wm_decl
      ,wm_ra_err
      ,wm_decl_err
      ,t1.V_inter / t1.avg_f_peak AS V
      ,t1.eta_inter / t1.avg_f_peak_weight AS eta
  FROM (SELECT runcat
              ,dataset
              ,f_datapoints
              ,wm_ra
              ,wm_decl
              ,wm_ra_err
              ,wm_decl_err
              ,avg_f_peak
              ,avg_f_peak_weight
              ,CASE WHEN rf0.f_datapoints = 1
                    THEN 0
                    ELSE SQRT(CAST(rf0.f_datapoints AS DOUBLE) * (avg_f_peak_sq - avg_f_peak * avg_f_peak) 
                             / (CAST(rf0.f_datapoints AS DOUBLE) - 1.0)
                             )
               END AS V_inter
              ,CASE WHEN rf0.f_datapoints = 1
                    THEN 0
                    ELSE (CAST(rf0.f_datapoints AS DOUBLE) / (CAST(rf0.f_datapoints AS DOUBLE) - 1.0)) 
                         * (avg_f_peak_weight * avg_weighted_f_peak_sq - avg_weighted_f_peak * avg_weighted_f_peak)
               END AS eta_inter
          FROM runningcatalog rc0
              ,runningcatalog_flux rf0
         WHERE rc0.dataset = %s
           AND rc0.id = rf0.runcat
       ) t1
 WHERE t1.V_inter / t1.avg_f_peak > %s
   AND t1.eta_inter / t1.avg_f_peak_weight > %s
"""
        cursor.execute(query, (dsid, V_lim, eta_lim))
        results = cursor.fetchall()
        results = [dict(
            srcid=x[0], npoints=x[2], v_nu=x[7], eta_nu=x[8], dataset=x[1],
            ra=x[3], dec=x[4], ra_err=x[5], dec_err=x[6])
                   for x in results]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error:
        query = query % (dsid, V_lim, eta_lim)
        logging.warn("Query failed:\n%s", query)
        raise
    finally:
        cursor.close()
    return results

        
def detect_variable_sources(conn, dsid, V_lim, eta_lim):
    """Detect variability in extracted sources compared to the previous
    detections"""

    return _select_variability_indices(conn, dsid, V_lim, eta_lim)


