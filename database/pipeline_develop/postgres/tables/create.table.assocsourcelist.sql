/**
 */
--CREATE SEQUENCE "seq_assocsourcelist" ;

CREATE TABLE assocsourcelist (
  /*id INT DEFAULT NEXT VALUE FOR "seq_assocsourcelist",*/
  xtrsrc_id INT NOT NULL,
  assoc_catsrc_id INT NOT NULL,
  assoc_distance_arcsec double precision NULL,
  assoc_lr double precision NULL,
  cnt_sf INT NULL,
  cnt_bg INT NULL,
  assoc_rely double precision NULL,
  p_id double precision NULL,
  p_noid double precision NULL
  /*PRIMARY KEY (id),*/
  /*FOREIGN KEY (xtrsrc_id) REFERENCES extractedsources (xtrsrcid),
  FOREIGN KEY (assoc_catsrc_id) REFERENCES catalogedsources (catsrcid)*/
);
