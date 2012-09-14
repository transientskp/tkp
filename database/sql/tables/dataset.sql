CREATE SEQUENCE seq_dataset AS INTEGER;

CREATE TABLE dataset
  (id INT NOT NULL DEFAULT NEXT VALUE FOR seq_dataset
  ,rerun INT NOT NULL DEFAULT '0'
  ,"type" TINYINT NOT NULL DEFAULT 1
  ,process_ts TIMESTAMP NOT NULL
  ,detection_threshold DOUBLE NULL
  ,analysis_threshold DOUBLE NULL
  ,assoc_radius DOUBLE NULL
  ,backsize_x SMALLINT NULL
  ,backsize_y SMALLINT NULL
  ,margin_width DOUBLE NULL
  ,description VARCHAR(100) NOT NULL
  ,node TINYINT NOT NULL DEFAULT %NODE%
  ,nodes TINYINT NOT NULL DEFAULT %NODES%
  ,PRIMARY KEY (id)
  )
;

