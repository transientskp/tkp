/**
 * This table stores the information about the extractedsources that
 * could be associated with a catalogedsource
 * xrtsrc_id:               This refers to the xtrsrcid of the extractedsource
 * assoc_catsrcid:          This is the id of the catalogedsource that could be 
 *                          associated to the extractedsource as its counterpart
 * assoc_type               Type of the association
 * assoc_distance_arcsec    The distance in arcsec between the associated sources
 * assoc_r                  The dimensionless distance (De Ruiter radius) between 
 *                          the associated sources. It is determined as the 
 *                          positional differences weighted by the errors
 *                          (Scheers thesis ch3).
 * assoc_loglr              The logarithm of the likelihood ratio of the 
 *                          associated sources (Scheers thesis ch3).
 */

CREATE TABLE assoccatsource
  (xtrsrc_id INT NOT NULL
  ,assoc_catsrc_id INT NOT NULL
  ,assoc_type TINYINT NOT NULL
  ,assoc_distance_arcsec DOUBLE NULL
  ,assoc_r DOUBLE NULL
  ,assoc_loglr DOUBLE NULL
  ,PRIMARY KEY (xtrsrc_id
               ,assoc_catsrc_id
               )
  )
;

