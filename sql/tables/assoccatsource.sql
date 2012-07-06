
CREATE TABLE assoccatsource
  (xtrsrc INT NOT NULL
  ,catsrc INT NOT NULL
  ,"type" TINYINT NOT NULL
  ,distance_arcsec DOUBLE NULL
  ,r DOUBLE NULL
  ,loglr DOUBLE NULL
  ,PRIMARY KEY (xtrsrc
               ,catsrc
               )
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
  ,FOREIGN KEY (catsrc) REFERENCES catalogedsource (id)
);

