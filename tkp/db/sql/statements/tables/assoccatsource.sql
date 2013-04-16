CREATE TABLE assoccatsource
  (xtrsrc INT NOT NULL
  ,catsrc INT NOT NULL
  ,type SMALLINT NOT NULL
  ,distance_arcsec DOUBLE PRECISION NULL
  ,r DOUBLE PRECISION NULL
  ,loglr DOUBLE PRECISION NULL
  ,PRIMARY KEY (xtrsrc ,catsrc)
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
  ,FOREIGN KEY (catsrc) REFERENCES catalogedsource (id)
);

