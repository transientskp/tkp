/**
 * This table stores the information about the major catalog sources
 * that could be associated with each other.
 * Sources that could be associated have a reference to the sourcelist
 * table, in which a weighted averaged source is listed.
 * catsrc_id:       This is the catsrcid that corresponds to the 
 *                  catalog source 
 * assoc_catsrcid:  This is the id of another catalog source that 
 *                  could be associated with the catalog source
 *                  (corresponding to assoc_xtrsrcid)
 * src_id:          Reference to the source in the sourcelist table.
 *                  This is an averaged source according to the 
 *                  associations.
 * 
 * TODO: What catalogs do we keep here?
 * WENSS, VLSS, NVSS, 8C, ...?
 */
CREATE TABLE associatedcatsources (
  id INT NOT NULL AUTO_INCREMENT,
  catsrc_id INT NOT NULL,
  assoc_catsrcid INT NULL,
  src_id INT NULL,
  assoc_class_id INT NULL,
  PRIMARY KEY (id),
  UNIQUE INDEX (catsrc_id
               ,assoc_catsrcid
               ),
  FOREIGN KEY (catsrc_id) REFERENCES catalogedsources (catsrcid),
  FOREIGN KEY (assoc_catsrcid) REFERENCES catalogedsources (catsrcid),
  INDEX (src_id),
  FOREIGN KEY (src_id) REFERENCES sourcelist (srcid),
  INDEX (assoc_class_id),
  FOREIGN KEY (assoc_class_id) REFERENCES associationclass (assoc_classid)
) ENGINE=InnoDB;
