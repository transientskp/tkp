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
 * assoc_lr_method  The applied method to determine the likelihood ratio 
 *          (0)     default, no method applied
 *          (1)     de Ruiter
 *          (2)     Rutledge
 *          (3)     Rutledge/Masci
 *          (4)     Sutherland & Saunders (1992)
 *          (5)     TKP (see doc)
 */
--CREATE SEQUENCE "seq_assoccatsources" ;

CREATE TABLE assoccatsources
  /*(id INT DEFAULT NEXT VALUE FOR "seq_assoccatsources"*/
  (xtrsrc_id INT NOT NULL
  ,assoc_catsrc_id INT NOT NULL
  ,assoc_weight double precision NULL
  ,assoc_distance_arcsec double precision NULL
  ,assoc_lr_method INT NULL DEFAULT 0
  ,assoc_r double precision NULL
  ,assoc_loglr double precision NULL
  /*,PRIMARY KEY (id)
  ,FOREIGN KEY (xtrsrc_id) REFERENCES extractedsources (xtrsrcid)
  ,FOREIGN KEY (assoc_catsrc_id) REFERENCES catalogedsources (catsrcid)*/
  )
;

