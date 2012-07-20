CREATE SEQUENCE seq_frequencyband AS SMALLINT;

CREATE TABLE frequencyband 
  (id SMALLINT NOT NULL DEFAULT NEXT VALUE FOR seq_frequencyband
  ,freq_central DOUBLE DEFAULT NULL
  ,freq_low DOUBLE DEFAULT NULL
  ,freq_high DOUBLE DEFAULT NULL
  ,PRIMARY KEY (id)
  )
;

