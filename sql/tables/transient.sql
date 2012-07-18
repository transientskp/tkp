CREATE TABLE transient 
  (id INT AUTO_INCREMENT
  ,runcat INT NOT NULL
  ,siglevel DOUBLE DEFAULT 0
  ,v DOUBLE
  ,eta DOUBLE
  ,detection_level DOUBLE DEFAULT 0
  ,trigger_xtrsrc INT NOT NULL
  ,status INT DEFAULT 0
  ,t_start TIMESTAMP
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (trigger_xtrsrc) REFERENCES extractedsource (id)
);

