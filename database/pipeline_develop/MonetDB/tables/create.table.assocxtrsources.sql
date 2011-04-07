--drop table assocxtrsources;
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
--CREATE SEQUENCE "seq_assocxtrsources" AS INTEGER;

CREATE TABLE assocxtrsources 
  /*(id INT DEFAULT NEXT VALUE FOR "seq_assocxtrsources"*/
  (xtrsrc_id INT NOT NULL
  ,assoc_xtrsrc_id INT NULL
  ,assoc_weight DOUBLE NULL
  ,assoc_distance_arcsec DOUBLE NULL
  ,assoc_lr_method INT NULL DEFAULT 0
  ,assoc_r DOUBLE NULL
  ,assoc_lr DOUBLE NULL
  /*,PRIMARY KEY (id)
  ,FOREIGN KEY (xtrsrc_id) REFERENCES extractedsources (xtrsrcid)
  ,FOREIGN KEY (assoc_xtrsrc_id) REFERENCES extractedsources (xtrsrcid)*/
  )
;

