/**
 */
CREATE TABLE dateandtimes (
  dtid INT NOT NULL AUTO_INCREMENT,
  txt VARCHAR(30) NULL,
  start_d DATE NULL, 
  start_ts TIMESTAMP NULL, 
  start_t TIME NULL,
  PRIMARY KEY (dtid)
) ENGINE=InnoDB;
