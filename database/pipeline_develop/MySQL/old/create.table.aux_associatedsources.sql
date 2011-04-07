/**
 * The assoc_type is one of the three:
 * C - assoc with catalog source
 * T - assoc with extracted source in time (same freq.)
 * B - assoc with extracted source, in frequency (same time)
 */
CREATE TABLE aux_associatedsources (
  id INT NOT NULL AUTO_INCREMENT,
  assoc_type CHAR(1) NULL,
  xtrsrcid1 INT NOT NULL,
  insert_src1 BOOLEAN NOT NULL,
  xtrsrcid2 INT NOT NULL,
  insert_src2 BOOLEAN NOT NULL,
  avgsrc_id INT NOT NULL,
  PRIMARY KEY (xtrsrcid1
              ,xtrsrcid2
              ),
  UNIQUE INDEX (id),
  INDEX (avgsrc_id),
  FOREIGN KEY (xtrsrcid1) REFERENCES averagedsources (xtrsrc_id1) 
) ENGINE=InnoDB;
