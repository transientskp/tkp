--drop table assocxtrsource;
/**
 * This table stores the information about the sources that
 * could be associated.
 * runcat_id:       refers to the runcatid in runningcatalog. 
 *                  It is the "base" id of a series of polarized 
 *                  spectral lightcurve datapoints.
 * assoc_xtrsrc_id: This is the id of the extracted source that 
 *                  could be associated to runningcatalog source 
 * Together, the runcat_id and the assoc_xtrsrc_id form a unique pair.
 * assoc_type:      Type of association:
 *                  x-y, where x is the number of runningcatalog sources,
 *                  and y the number of extractedsources
 *                  1: 1-1
 *                  2: 1-n
 *                  3: n-1
 *                  4: n-m
 *                  5: 0-1
 * assoc_distance_arcsec    The distance in arcsec 
 *                  between the associated sources
 * assoc_r          The dimensionless distance (De Ruiter radius) between 
 *                  the associated sources. It is determined as the 
 *                  positional differences weighted by the errors
 *                  (Scheers thesis ch3).
 * assoc_loglr      The logarithm of the likelihood ratio of the 
 *                  associated sources (Scheers thesis ch3).
 */

CREATE TABLE assocxtrsource
  (runcat_id INT NOT NULL
  ,assoc_xtrsrc_id INT NULL
  ,assoc_type TINYINT NOT NULL
  ,assoc_distance_arcsec DOUBLE NULL
  ,assoc_r DOUBLE NULL
  ,assoc_loglr DOUBLE NULL
  ,PRIMARY KEY (runcat_id
               ,assoc_xtrsrc_id
               )
  )
;

