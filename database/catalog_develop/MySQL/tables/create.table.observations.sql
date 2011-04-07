/*
 * This table contains the information about the current observation
 * time_s & _e: BIGINT is used to simulate a ms accurate timestamp
 */
CREATE TABLE observations (
  obsid INT  NOT NULL AUTO_INCREMENT,
  time_s BIGINT  NULL,
  time_e BIGINT  NULL,
  description VARCHAR(500) NULL,
  PRIMARY KEY (obsid)
) ENGINE=InnoDB;
