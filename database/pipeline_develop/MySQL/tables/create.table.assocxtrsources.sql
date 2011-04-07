/**
 * This table stores the information about the sources that
 * could be associated.
 * assoc_type:      Either 'X' or 'C', for associations 
 *                  in extractedsources or catalogedsources
 * xrtsrc_id:       This is the xtrsrcid that corresponds to the 
 *                  first detection
 * assoc_xtrsrcid:  This is the id of the source that could be 
 *                  associated to a previously detection 
 *                  (corresponding to assoc_xtrsrcid)
 */
CREATE TABLE assocxtrsources (
  /*id INT NOT NULL AUTO_INCREMENT,*/
  xtrsrc_id INT NOT NULL,
  assoc_xtrsrc_id INT NULL,
  assoc_weight DOUBLE NULL,
  assoc_distance_arcsec DOUBLE NULL,
  assoc_lr_method INT NULL DEFAULT 0,
  assoc_r DOUBLE NULL,
  assoc_lr DOUBLE NULL,
  /*PRIMARY KEY (id),*/
  INDEX (xtrsrc_id),
  FOREIGN KEY (xtrsrc_id) REFERENCES extractedsources (xtrsrcid),
  INDEX (assoc_xtrsrc_id),
  FOREIGN KEY (assoc_xtrsrc_id) REFERENCES extractedsources (xtrsrcid)
) ENGINE=InnoDB;
