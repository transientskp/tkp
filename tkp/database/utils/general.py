"""
A collection of back end subroutines (mostly SQL queries).

In this module we collect together various routines
that don't fit into a more specific collection.

Most of the basic insertion routines are kept here,
with exceptions of monitoringlist and transients.
"""

import math, sys
import logging

import monetdb.sql as db
from tkp.config import config
import tkp.database
from tkp.database import DataBase
from tkp.utility.coordinates import eq_to_cart

logger = logging.getLogger(__name__)

AUTOCOMMIT = config['database']['autocommit']


lightcurve_query = """
SELECT im.taustart_ts
      ,im.tau_time
      ,ex.f_int
      ,ex.f_int_err
      ,ex.id
      ,im.band
      ,im.stokes
  FROM extractedsource ex
      ,assocxtrsource ax
      ,image im
 WHERE ax.runcat IN (SELECT runcat
                       FROM assocxtrsource
                      WHERE xtrsrc = %(xtrsrc)s
                    )
   AND ax.xtrsrc = ex.id
   AND ex.image = im.id
ORDER BY im.taustart_ts
"""

update_dataset_process_ts_query = """
UPDATE dataset
   SET process_ts = %(process_ts)s
 WHERE id = %(dataset_id)s
"""



def filter_userdetections_extracted_sources(image_id, deRuiter_r, assoc_theta=0.03):
    """Remove the forced-fit user-entry sources, that have a counterpart
    with another extractedsource

    """
    filter_ud_xtrsrcs_query = """\
DELETE 
  FROM extractedsource
 WHERE id IN (SELECT x0.id
                FROM extractedsource x0
                    ,extractedsource x1
               WHERE x0.image = %(image_id)s
                 AND x0.extract_type = 3
                 AND x1.image = %(image_id)s
                 AND x1.extract_type IN (0, 1, 2)
                 AND x1.zone BETWEEN CAST(FLOOR(x0.decl - %(assoc_theta)s) as INTEGER)
                                 AND CAST(FLOOR(x0.decl + %(assoc_theta)s) as INTEGER)
                 AND x1.decl BETWEEN x0.decl - %(assoc_theta)s
                                 AND x0.decl + %(assoc_theta)s
                 AND x1.ra BETWEEN x0.ra - alpha(%(assoc_theta)s, x0.decl)
                               AND x0.ra + alpha(%(assoc_theta)s, x0.decl)
                 AND SQRT(  (x0.ra * COS(RADIANS(x0.decl)) - x1.ra * COS(RADIANS(x1.decl)))
                          * (x0.ra * COS(RADIANS(x0.decl)) - x1.ra * COS(RADIANS(x1.decl)))
                          / (x0.ra_err * x0.ra_err + x1.ra_err * x1.ra_err)
                         +  (x0.decl - x1.decl) * (x0.decl - x1.decl)
                          / (x0.decl_err * x0.decl_err + x1.decl_err * x1.decl_err)
                         ) < %(deRuiter_red)s
             )
    """
    try:
        conn = DataBase().connection
        args = {'image_id': image_id,
                'assoc_theta': assoc_theta,
                'deRuiter_red': deRuiter_r / 3600.
                }
        cursor = conn.cursor()
        q = filter_ud_xtrsrcs_query % (args)
        #print "FILTER Q:\n", q
        #answer=str(raw_input('Continue (y/n)? '))
        #if answer != 'y':
        #    sys.exit()
        filtered = cursor.execute(filter_ud_xtrsrcs_query, args)
        if not AUTOCOMMIT:
            conn.commit()
        if filtered == 0:
            logger.info("No user-entry sources removed from extractedsource for image %s" \
                            % (image_id,))
        else:
            logger.info("Removed %d sources from extractedsource for image %s" \
                            % (filtered, image_id))
        #answer=str(raw_input('Continue (y/n)? '))
        #if answer != 'y':
        #    sys.exit()
    except db.Error, e:
        logger.warn("Failed on query nr %s." % q)
        raise
    finally:
        cursor.close()


def update_dataset_process_ts(dataset_id, process_ts):
    """Update dataset start-of-processing timestamp.

    """
    conn = DataBase().connection
    args = {'dataset_id': dataset_id, 'process_ts': process_ts}
    cursor = tkp.database.query(conn, update_dataset_process_ts_query, args, commit=True)
    return dataset_id

def insert_dataset(conn, description):
    """Insert dataset with description as given by argument.

    DB function insertDataset() sets the necessary default values.
    """
    query = "SELECT insertDataset(%s)"
    arguments = description
    cursor = tkp.database.query(conn, query, arguments, commit=True)
    dataset_id = cursor.fetchone()[0]
    return dataset_id


def insert_image(conn,
                 dataset, freq_eff, freq_bw, taustart_ts, tau_time,
                 beam_maj, beam_min, beam_pa, deltax, deltay, url,
                 centre_ra, centre_decl, xtr_radius
                 ):
    """Insert an image for a given dataset with the column values
    given in the argument list.

    Args:
     - centre_ra, centre_decl, xtr_radius:
       These define the region within ``xtr_radius`` degrees of the
       field centre, that will be used for source extraction.
       (This obviously implies a promised on behalf of the pipeline not to do
       anything else!)
       Note centre_ra, centre_decl, extracion_radius should all be in degrees.

    """
    query = "SELECT insertImage(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    arguments = (dataset, tau_time, freq_eff, freq_bw, taustart_ts,
                 beam_maj, beam_min, beam_pa, deltax, deltay, url,
                 centre_ra, centre_decl, xtr_radius)
    cursor = tkp.database.query(conn, query, arguments, commit=True)
    image_id = cursor.fetchone()[0]
    return image_id


def insert_extracted_sources(image_id, results, extract):
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
    extract tells whether the source results are originating from:
    0: blind source extraction 
    1: from forced fits at null detection locations
    2: from forced fits for monitoringlist sources
    """
    
    #To do: Figure out a saner method of passing the results around
    # (Namedtuple for starters?) 
    if len(results) == 0:
        logger.info("No extract_type=%s sources added to extractedsource for image %s" \
                            % (extract, image_id))
    else:
        _insert_extractedsources(image_id, results, extract)

#TO DO(?): merge the private function below into the public function above?

def _insert_extractedsources(image_id, results, extract):
    """Insert all extracted sources with their properties

    The content of results is in the following sequence:
    (ra, dec, ra_fit_err, dec_fit_err, peak_flux, peak_flux_err, 
    int_flux, int_flux_err, significance level,
    beam major width (as), beam minor width(as), beam parallactic angle,
    ra_sys_err, dec_sys_err).
    See insert_extracted_sources() for a description of extract.
    
    ra_fit_err & dec_fit_err are the 1-sigma errors from the gaussian fit,
    in degrees.
    ra_sys_err and dec_sys_err represent the systematic errors in ra and declination, 
    and are in arcsec!
    ra_err^2 = ra_sys_err^2 + ra_fit_err^2, idem for decl_err.
    
    
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
    conn = DataBase().connection
    xtrsrc = []
    for src in results:
        r = list(src)
        r[2] = r[2] * 3600. # ra_fit_err converted to arcsec
        r[3] = r[3] * 3600. # decl_fit_err converted to arcsec
        # ra_err: sqrt of quadratic sum of sys and fit errors, in arcsec
        r.append(math.sqrt(r[12]**2 + r[2]**2)) 
        # decl_err: sqrt of quadratic sum of sys and fit errors, in arcsec
        r.append(math.sqrt(r[13]**2 + r[3]**2))
        r.append(image_id) # id of the image
        r.append(int(math.floor(r[1]))) # zone
        r.extend(eq_to_cart(r[0], r[1])) #Cartesian x,y,z
        r.append(r[0] * math.cos(math.radians(r[1]))) # ra * cos(radias(decl))
        if extract == 'blind':
            r.append(0)
        elif extract == 'ff_nd':
            r.append(1)
        elif extract == 'ff_mon':
            r.append(2)
        elif extract == 'ff_ud':
            r.append(3)
        else:
            raise ValueError("Not a valid extractedsource insert type: '%s'" % extract)
        xtrsrc.append(r)
    values = [str(tuple(xsrc)) for xsrc in xtrsrc]

    cursor = conn.cursor()
    try:
        query = """\
        INSERT INTO extractedsource
          (ra
          ,decl
          ,ra_fit_err
          ,decl_fit_err
          ,f_peak
          ,f_peak_err
          ,f_int
          ,f_int_err
          ,det_sigma
          ,semimajor
          ,semiminor
          ,pa
          ,ra_sys_err
          ,decl_sys_err
          ,ra_err
          ,decl_err
          ,image
          ,zone
          ,x
          ,y
          ,z
          ,racosdecl
          ,extract_type
          )
        VALUES
        """\
        + ",".join(values)
        cursor.execute(query)
        if not AUTOCOMMIT:
            conn.commit()
        if len(values) == 0:
                logger.info("No forced-fit sources added to extractedsource for image %s" \
                            % (image_id,))
        else:
            if extract == 'blind':
                logger.info("Inserted %d sources in extractedsource for image %s" \
                            % (len(values), image_id))
            elif extract == 'ff_nd':
                logger.info("Inserted %d forced-fit null detections in extractedsource for image %s" \
                            % (len(values), image_id))
            elif extract == 'ff_mon':
                logger.info("Inserted %d forced-fit monitoringsources in extractedsource for image %s" \
                            % (len(values), image_id))
            elif extract == 'ff_ud':
                logger.info("Inserted %d forced-fit user entries in extractedsource for image %s" \
                            % (len(values), image_id))
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
        A list of tuples, each tuple containing (in order):
            - observation start time as a datetime.datetime object
            - integration time (float)
            - integrated flux (float)
            - integrated flux error (float)
            - database ID of this particular source
            - frequency band ID
            - stokes
    """
    args = {'xtrsrc': xtrsrcid}
    cursor = tkp.database.query(conn, lightcurve_query, args)
    return cursor.fetchall()


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


def match_nearests_in_catalogs(conn, runcatid, radius, deRuiter_r,
                              catalogid=None):
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

        deRuiter_r (float): the De Ruiter radius, a dimensionless search radius.
        Source pairs with a De Ruiter radius that falls outside the cut-off
        are discarded as genuine association.
        
    The return values are ordered first by catalog, then by
    assoc_r. So the first source in the list is the closest match for
    a catalog.
    """
    
    results = []
    query = """\
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
        cursor.execute(query,  (runcatid,
                                radius, radius, radius, radius,
                                radius, radius, 
                                radius,
                                deRuiter_r/3600.))
        results = cursor.fetchall()
        results = [
            {'catsrcid': result[0], 'catsrcname': result[1],
             'catid': result[2], 'catname': result[3],
             'ra': result[4], 'decl': result[5],
             'ra_err': result[6], 'decl_err': result[7],
             'dist_arcsec': result[8], 'assoc_r': result[9]}
            for result in results]
    except db.Error, e:
        query = query % (runcatid,
                         radius, radius, radius, radius,
                         radius, radius,
                         radius,
                         deRuiter_r/3600.)
        logger.warn("Query failed:\n%s", query)
        raise
    finally:
        cursor.close()
    return results


