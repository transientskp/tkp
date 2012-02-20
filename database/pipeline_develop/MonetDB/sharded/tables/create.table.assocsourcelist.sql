/**
 */
--CREATE SEQUENCE "seq_assocsourcelist" AS INTEGER;

CREATE TABLE assocsourcelist (
  /*id INT DEFAULT NEXT VALUE FOR "seq_assocsourcelist",*/
  xtrsrc_id INT NOT NULL,
  assoc_catsrc_id INT NOT NULL,
  assoc_distance_arcsec DOUBLE NULL,
  assoc_lr DOUBLE NULL,
  cnt_sf INT NULL,
  cnt_bg INT NULL,
  assoc_rely DOUBLE NULL,
  p_id DOUBLE NULL,
  p_noid DOUBLE NULL
  /*PRIMARY KEY (id),*/
  /*FOREIGN KEY (xtrsrc_id) REFERENCES extractedsources (xtrsrcid),
  FOREIGN KEY (assoc_catsrc_id) REFERENCES catalogedsources (catsrcid)*/
);
