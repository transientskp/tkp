--drop table assocfreqruncatsources;
/**
 * This table stores the information about the sources that
 * could be associated.
 * src_type:        Either 'X' or 'C', for associations 
 *                  in extractedsources or catalogedsources
 * xrtsrc_id:       This is the xtrsrcid that corresponds to the 
 *                  first detection
 * assoc_xtrsrcid:  This is the id of the source that could be 
 *                  associated to a previously detection 
 *                  (corresponding to assoc_xtrsrcid)
 */

CREATE TABLE assocfreqruncatsources
  (xtrsrc_id INT NOT NULL
  ,band INT NOT NULL
  ,assoc_xtrsrc_id INT NOT NULL
  ,assoc_band INT NOT NULL
  ,assoc_method INT NULL DEFAULT 0
  ,assoc_distance_arcsec DOUBLE NULL
  ,assoc_r DOUBLE precision NULL
  ,assoc_loglr DOUBLE precision NULL
  )
;
