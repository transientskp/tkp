CREATE TABLE assocxtrsource
  (runcat INT NOT NULL
  ,xtrsrc INT NULL
  ,type TINYINT NOT NULL
  ,distance_arcsec DOUBLE NULL
  ,r DOUBLE NULL
  ,loglr DOUBLE NULL
  ,PRIMARY KEY (runcat, xtrsrc)
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
);

