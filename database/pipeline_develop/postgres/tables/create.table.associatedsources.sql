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
CREATE TABLE associatedsources (
  id SERIAL PRIMARY KEY,
  xtrsrc_id INT NOT NULL,
  assoc_type CHAR(1) NOT NULL,
  assoc_xtrsrc_id INT NULL,
  assoc_catsrc_id INT NULL,
  assoc_weight double precision NULL,
  assoc_distance_arcsec double precision NULL,
  FOREIGN KEY (xtrsrc_id) REFERENCES extractedsources (xtrsrcid),
  FOREIGN KEY (assoc_xtrsrc_id) REFERENCES extractedsources (xtrsrcid),
  FOREIGN KEY (assoc_catsrc_id) REFERENCES catalogedsources (catsrcid)
);
