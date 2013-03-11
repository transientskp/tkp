CREATE TABLE monitoringlist
  (id INTEGER AUTO_INCREMENT
  ,runcat INTEGER NULL
  ,ra DOUBLE DEFAULT 0
  ,decl DOUBLE DEFAULT 0
  ,dataset INTEGER NOT NULL
  ,userentry BOOLEAN DEFAULT FALSE
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  )
;
