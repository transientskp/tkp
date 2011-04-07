/**
 * This table contains the averaged positions of the sources 
 * that could be associated.
 * Positions are weighted averages of the associated sources.
 */
CREATE TABLE averagedsources (
  avgsrcid INT NOT NULL AUTO_INCREMENT,
  xtrsrc_id1 INT NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  det_sigma DOUBLE NULL,
  I_peak DOUBLE NULL,
  I_peak_err DOUBLE NULL,
  /*Q_peak DOUBLE NULL,
  Q_peak_err DOUBLE NULL,
  U_peak DOUBLE NULL,
  U_peak_err DOUBLE NULL,
  V_peak DOUBLE NULL,
  V_peak_err DOUBLE NULL,*/
  I_int DOUBLE NULL,
  I_int_err DOUBLE NULL,
  /*Q_int DOUBLE NULL,
  Q_int_err DOUBLE NULL,
  U_int DOUBLE NULL,
  U_int_err DOUBLE NULL,
  V_int DOUBLE NULL,
  V_int_err DOUBLE NULL,*/
  PRIMARY KEY (avgsrcid),
  UNIQUE INDEX (xtrsrc_id1),
  FOREIGN KEY (xtrsrc_id1) REFERENCES associatedsources (xtrsrc_id)
) ENGINE=InnoDB;
