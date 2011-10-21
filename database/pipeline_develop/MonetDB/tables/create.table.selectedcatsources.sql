/**
 * This table contains the known sources that were detected previously, 
 * either by LOFAR itself or other instruments. 
 * It is a selection from the table containing all the catalog 
 * sources (in the catlogue area). 
 * Every observation has its field(s) of view and for this all the 
 * known sources are collected. This table will be loaded from the 
 * catalog table in the catalog database before every observation.
 * This table will be used to load the sources table 
 * and will not be touched any more during an observation.
 * Fluxes are in Jy, ra, decl, ra_err and decl_err in degrees.
 * PA, major, minor in degrees
 *
 * TODO: Probably it is better not te set catsrcid to auto_incr,
 * because we will copy them from the catalog database.
 */
CREATE TABLE selectedcatsources 
  (catsrc_id INT NOT NULL
  ,cat_id INT NOT NULL
  ,zone INT NOT NULL
  ,ra DOUBLE NOT NULL
  ,decl DOUBLE NOT NULL
  ,ra_err DOUBLE NOT NULL
  ,decl_err DOUBLE NOT NULL
  ,x DOUBLE NOT NULL
  ,y DOUBLE NOT NULL
  ,z DOUBLE NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT 0
  ,I_peak DOUBLE NULL
  ,I_peak_err DOUBLE NULL
  ,I_int DOUBLE NULL
  ,I_int_err DOUBLE NULL
  )
;

