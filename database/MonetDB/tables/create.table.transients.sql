/**
 * This table contains the detected transients and their characteristics
 */
CREATE SEQUENCE "seq_transient" AS INTEGER;

CREATE TABLE transient 
  (transientid INT DEFAULT NEXT VALUE FOR "seq_transient"
  ,xtrsrc_id INT NOT NULL
  ,siglevel DOUBLE DEFAULT 0
  ,v DOUBLE
  ,eta DOUBLE
  ,detection_level DOUBLE DEFAULT 0
  ,trigger_xtrsrc_id INT NOT NULL
  ,status INT DEFAULT 0
  ,t_start TIMESTAMP
  )
;

