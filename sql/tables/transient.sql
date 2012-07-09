CREATE TABLE transient 
  (id INT AUTO_INCREMENT
  ,xtrsrc INT NOT NULL
  ,siglevel DOUBLE DEFAULT 0
  ,v DOUBLE
  ,eta DOUBLE
  ,detection_level DOUBLE DEFAULT 0
  ,trigger_xtrsrc_id INT NOT NULL
  ,status INT DEFAULT 0
  ,t_start TIMESTAMP
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
);

