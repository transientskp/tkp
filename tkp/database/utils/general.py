# -*- coding: utf-8 -*-

#
# LOFAR Transients Key Project
#
# Bart Scheers, Evert Rol, Tim Staley
#
# discovery@transientskp.org
#

"""
A collection of back end subroutines (mostly SQL queries).

In this module we collect together various routines 
that don't fit into a more specific collection. 

Most of the basic insertion routines are kept here,
with exceptions of monitoringlist and transients. 
"""
import math
import logging
import monetdb.sql as db
from tkp.config import config

logger = logging.getLogger(__name__)

AUTOCOMMIT = config['database']['autocommit']
DERUITER_R = config['source_association']['deruiter_radius']
BG_DENSITY = config['source_association']['bg-density']



def insert_dataset(conn, description):
    """Insert dataset with description as given by argument.

    DB function insertDataset() sets the necessary default values.
    """

    newdsid = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT insertDataset(%s)
        """
        cursor.execute(query, (description,))
        if not AUTOCOMMIT:
            conn.commit()
        newdsid = cursor.fetchone()[0]
    except db.Error, e:
        logger.warn("Query failed: %s." % query)
        raise
    finally:
        cursor.close()
    return newdsid



def insert_image(conn, dataset,
                 freq_eff, freq_bw, 
                 taustart_ts, tau_time,
                 beam_maj, beam_min, beam_pa,  
                 url):
    """Insert an image for a given dataset with the column values
    given in the argument list.
    """
    #tau_mode = 0 ###Placeholder, this variable is not well defined currently.

    newimgid = None
    try:
        cursor = conn.cursor()
        query = """\
        SELECT insertImage(%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (dataset
                              ,tau_time
                              ,freq_eff
                              ,freq_bw
                              ,taustart_ts
                              ,beam_maj
                              ,beam_min
                              ,beam_pa
                              ,url
                              ))
        newimgid = cursor.fetchone()[0]
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logger.warn("Query failed: %s." % query)
        raise
    finally:
        cursor.close()
    return newimgid


def insert_extracted_sources(conn, image_id, results):
    """Insert all extracted sources

    Insert the sources that were detected by the Source Extraction
    procedures into the extractedsources table.

    Therefore, we use a temporary table containing the "raw" detections,
    from which the sources will then be inserted into extractedsources.
    
    (ra , dec , [deg]
    ra_err, dec_err, [deg, but converted to as in db] 
    peak, peak_err,  [Jy]
    flux, flux_err,    [Jy]
    significance level,
    beam major width , beam minor width, [as]
    beam parallactic angle).  [deg]
    """
    
    #To do: Figure out a saner method of passing the results around
    # (Namedtuple for starters?) 
    if len(results):
        _insert_extractedsources(conn, image_id, results)

#TO DO(?): merge the private function below into the public function above?

def _insert_extractedsources(conn, image_id, results):
    """Insert all extracted sources with their properties

    The content of results is in the following sequence:
    (ra, dec, ra_err, dec_err, peak_flux, peak_flux_err, 
    int_flux, int_flux_err, significance level,
    beam major width (as), beam minor width(as), beam parallactic angle).
    
    For all extracted sources additional parameters are calculated,
    and appended to the sourcefinder data. Appended and converted are:
    - the image id to which the extracted sources belong to 
    - the zone in which an extracted source falls is calculated, based 
      on its declination. We adopt a zoneheight of 1 degree, so
      the floor of the declination represents the zone.
    - the positional errors are converted from degrees to arcsecs
    - the Cartesian coordinates of the source position
    - ra * cos(radians(decl)), this is very often being used in 
      source-distance calculations

    """
    xtrsrc = []
    for src in results:
        r = list(src)
        r[2] = r[2] * 3600. # ra_err converted to arcsec
        r[3] = r[3] * 3600. # decl_err is converted to arcsec
        r.append(image_id) # id of the image
        r.append(int(math.floor(r[1]))) # zone
        r.append(math.cos(math.radians(r[1])) * math.cos(math.radians(r[0]))) # Cartesian x
        r.append(math.cos(math.radians(r[1])) * math.sin(math.radians(r[0]))) # Cartesian y
        r.append(math.sin(math.radians(r[1]))) # Cartesian z
        r.append(r[0] * math.cos(math.radians(r[1]))) # ra * cos(radias(decl))
        xtrsrc.append(r)
    values = [str(tuple(xsrc)) for xsrc in xtrsrc]

    cursor = conn.cursor()
    try:
        query = """\
        INSERT INTO extractedsource
          (ra
          ,decl
          ,ra_err
          ,decl_err
          ,f_peak
          ,f_peak_err
          ,f_int
          ,f_int_err
          ,det_sigma
          ,semimajor
          ,semiminor
          ,pa
          ,image
          ,zone
          ,x
          ,y
          ,z
          ,racosdecl
          )
        VALUES
        """\
        + ",".join(values)
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
    except db.Error, e:
        logger.warn("Failed on query nr %s." % query)
        raise
    finally:
        cursor.close()


def lightcurve(conn, xtrsrcid):
    """Obtain a light curve for a specific extractedsource

    Args:

        xtrsrcid (int): the source identifier that corresponds to a
        point on the light curve. Note that the point does not have to
        be the start (first) point of the light curve.

    Returns:

        A list of 5-tuples, each tuple containing (in order):

            - observation start time as a datetime.datetime object

            - integration time (float)

            - integrated flux (float)

            - integrated flux error (float)

            - database ID of this particular source
    """
    #TODO: This lightcurve returns fluxes for every band and stokes if available.

    cursor = conn.cursor()
    try:
        query = """\
        SELECT im.taustart_ts
              ,im.tau_time
              ,ex.f_int
              ,ex.f_int_err
              ,ex.id
          FROM extractedsource ex
              ,assocxtrsource ax
              ,image im
         WHERE ax.runcat IN (SELECT runcat
                               FROM assocxtrsource
                              WHERE xtrsrc = %s
                            )
           AND ax.xtrsrc = ex.id
           AND ex.image = im.id
        ORDER BY im.taustart_ts
        """
        cursor.execute(query, (xtrsrcid,))
        results = cursor.fetchall()
    except db.Error:
        query = query % xtrsrcid
        logger.warn("Failed to obtain light curve")
        logger.warn("Query failed:\n%s", query)
        raise
    finally:
        cursor.close()
    return results





def get_imagefiles_for_ids(conn, image_ids):
    """Return a list of image filenames for the give image ids

    The actual returned list contains 2-tuples of (id, url)
    """
    
    where_string = ", ".join(["%s"] * len(image_ids))
    where_tuple = tuple(image_ids)
    query = ("""SELECT id, url FROM image WHERE id in (%s)""" %
             where_string)
    cursor = conn.cursor()
    try:
        querytxt = query % where_tuple
        cursor.execute(query, where_tuple)
        results = cursor.fetchall()
        ## extra
        #if not AUTOCOMMIT:
        #    conn.commit()
    except db.Error, e:
        query = query % where_tuple
        logger.warn("Query failed: %s", query)
        raise
    finally:
        cursor.close()
    return results


def match_nearests_in_catalogs(conn, runcatid, radius=1.0,
                              catalogid=None, assoc_r=DERUITER_R/3600.):
    """Match a source with position ra, decl with catalogedsources
    within radius

    The function does not return the best match, but a list of sources
    that are contained within radius, ordered by distance.

    One can limit the list of matches using assoc_r for a
    goodness-of-match measure.
    
    Args:

        runcatid: id of source in runningcatalog

    Kwargs:
    
        radius (float): search radius around the source to search, in
        degrees

        catalogid (int or list of ints): the catalog(s) to search. If
        none, all catalogs are searched for. A single integer
        specifies one catalog, while a list of integers specifies
        multiple catalogs.

        assoc_r (float): dimensionless search radius, in units of the
        De Ruiter radius. 3.7/3600. is a good value, though the
        default is 180 (which will match all sources). Assoc_r sets a
        cut off for the found sources.
        
    The return values are ordered first by catalog, then by
    assoc_r. So the first source in the list is the closest match for
    a catalog.
    """
    
    #zoneheight = 1.0
    #catalog_filter = ""
    #if catalogid is None:
    #    catalog_filter = ""
    #else:
    #    try:
    #        iter(catalogid)
    #        # Note: cast to int, to ensure proper type
    #        catalog_filter = (
    #            "c.catid in (%s) AND " % ", ".join(
    #            [str(int(catid)) for catid in catalogid]))
    #    except TypeError:
    #        catalog_filter = "c.catid = %d AND " % catalogid
    #
    #subquery = """\
    #SELECT cs.catsrcid
    #      ,c.catid
    #      ,c.catname
    #      ,cs.catsrcname
    #      ,cs.ra
    #      ,cs.decl
    #      ,cs.ra_err
    #      ,cs.decl_err
    #      ,3600 * DEGREES(2 * ASIN(SQRT( (rc.x - cs.x) * (rc.x - cs.x)
    #                                   + (rc.y - cs.y) * (rc.y - cs.y)
    #                                   + (rc.z - cs.z) * (rc.z - cs.z)
    #                                   ) / 2)
    #                     ) AS assoc_distance_arcsec
    #      ,3600 * SQRT(  (rc.wm_ra - cs.ra) * COS(RADIANS(rc.wm_decl)) 
    #                   * (rc.wm_ra - cs.ra) * COS(RADIANS(rc.wm_decl))
    #                     / (rc.wm_ra_err * rc.wm_ra_err + cs.ra_err * cs.ra_err)
    #                  + (rc.wm_decl - cs.decl) * (rc.wm_decl - cs.decl)
    #                    / (rc.wm_decl_err * rc.wm_decl_err + cs.decl_err * cs.decl_err)
    #                  ) AS assoc_r
    #  FROM (SELECT wm_ra - alpha(%%s, wm_decl) as ra_min
    #              ,wm_ra + alpha(%%s, wm_decl) as ra_max
    #              ,CAST(FLOOR((wm_decl - %%s) / %%s) AS INTEGER) as zone_min
    #              ,CAST(FLOOR((wm_decl + %%s) / %%s) AS INTEGER) as zone_max
    #              ,wm_decl - %%s as decl_min
    #              ,wm_decl + %%s as decl_max
    #              ,x
    #              ,y
    #              ,z
    #              ,wm_ra
    #              ,wm_decl
    #              ,wm_ra_err
    #              ,wm_decl_err
    #          FROM runningcatalog
    #         WHERE xtrsrc = %%s
    #       ) rc
    #      ,catalogedsources cs
    #      ,catalogs c
    # WHERE %(catalog_filter)s
    #      cs.cat_id = c.catid
    #  AND cs.zone BETWEEN rc.zone_min 
    #                  AND rc.zone_max
    #  AND cs.ra BETWEEN rc.ra_min 
    #                and rc.ra_max
    #  AND cs.decl BETWEEN rc.decl_min 
    #                  and rc.decl_max
    #  AND cs.x * rc.x + cs.y * rc.y + cs.z * rc.z > COS(RADIANS(%%s))
    #""" % {'catalog_filter': catalog_filter}
    ##  AND cs.ra BETWEEN rc.wm_ra - alpha(%%s, rc.wm_decl)
    ##                AND rc.wm_ra + alpha(%%s, rc.wm_decl)
    #query = """\
    #SELECT 
    #    t.catsrcid
    #   ,t.catsrcname
    #   ,t.catid
    #   ,t.catname
    #   ,t.ra
    #   ,t.decl
    #   ,t.ra_err
    #   ,t.decl_err
    #   ,t.assoc_distance_arcsec
    #   ,t.assoc_r
    #FROM (%(subquery)s) as t
    #WHERE t.assoc_r < %%s
    #ORDER BY t.catid ASC, t.assoc_r ASC
    #""" % {'subquery': subquery}
    
    results = []
    # TODO: I would suggest this:
    q_alt = """\
    SELECT c.id
          ,c.catsrcname
          ,c.catalog
          ,k.name
          ,c.ra
          ,c.decl
          ,c.ra_err
          ,c.decl_err
          ,3600 * DEGREES(2 * ASIN(SQRT( (r.x - c.x) * (r.x - c.x)
                                       + (r.y - c.y) * (r.y - c.y)
                                       + (r.z - c.z) * (r.z - c.z)
                                       ) / 2)
                         ) AS distance_arcsec
          ,3600 * SQRT(  (r.wm_ra - c.ra) * COS(RADIANS(r.wm_decl)) 
                       * (r.wm_ra - c.ra) * COS(RADIANS(r.wm_decl))
                         / (r.wm_ra_err * r.wm_ra_err + c.ra_err * c.ra_err)
                      + (r.wm_decl - c.decl) * (r.wm_decl - c.decl)
                        / (r.wm_decl_err * r.wm_decl_err + c.decl_err * c.decl_err)
                      ) AS assoc_r
      FROM runningcatalog r
          ,catalogedsource c
          ,catalog k
     WHERE r.id = %s
       AND c.zone BETWEEN CAST(FLOOR(r.wm_decl - %s) AS INTEGER)
                      AND CAST(FLOOR(r.wm_decl + %s) AS INTEGER)
       AND c.decl BETWEEN r.wm_decl - %s
                      AND r.wm_decl + %s
       AND c.ra BETWEEN r.wm_ra - alpha(%s, r.wm_decl)
                    AND r.wm_ra + alpha(%s, r.wm_decl)
       AND c.x * r.x + c.y * r.y + c.z * r.z > COS(RADIANS(%s))
       AND c.catalog = k.id
       AND SQRT(  (r.wm_ra - c.ra) * COS(RADIANS(r.wm_decl)) 
                       * (r.wm_ra - c.ra) * COS(RADIANS(r.wm_decl))
                         / (r.wm_ra_err * r.wm_ra_err + c.ra_err * c.ra_err)
                      + (r.wm_decl - c.decl) * (r.wm_decl - c.decl)
                        / (r.wm_decl_err * r.wm_decl_err + c.decl_err * c.decl_err)
                      ) < %s
    ORDER BY c.catalog
            ,assoc_r
    """

    try:
        cursor = conn.cursor()
        #cursor.execute(query,  (radius, radius, radius, zoneheight,
        #                        radius, zoneheight, radius, radius,
        #                        srcid, radius, assoc_r))
        cursor.execute(q_alt,  (runcatid,
                                radius, radius, radius, radius,
                                radius, radius, 
                                radius,
                                assoc_r))
        results = cursor.fetchall()
        results = [
            {'catsrcid': result[0], 'catsrcname': result[1],
             'catid': result[2], 'catname': result[3],
             'ra': result[4], 'decl': result[5],
             'ra_err': result[6], 'decl_err': result[7],
             'dist_arcsec': result[8], 'assoc_r': result[9]}
            for result in results]
    except db.Error, e:
        #query = query % (radius, radius, radius, zoneheight,
        #                 radius, zoneheight,
        #                 radius, radius, srcid, radius, assoc_r)
        #logger.warn("Query failed: %s", query)
        query = q_alt % (runcatid,
                         radius, radius, radius, radius,
                         radius, radius,
                         radius,
                         assoc_r)
        logger.warn("Query failed:\n%s", query)
        raise
    finally:
        cursor.close()
    return results


