/**
 * This table contains the averaged positions of the sources 
 * that could be associated.
 * Positions are weighted averages of the associated sources.
 */
CREATE SEQUENCE "seq_averagedsources" AS INTEGER;

CREATE TABLE averagedsources (
  avgsrcid INT DEFAULT NEXT VALUE FOR "seq_averagedsources",
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
  UNIQUE (xtrsrc_id1)
  /* TODO:
   * This foreign key does not work:
   * Error message:
   * MAPI  = lofar@localhost:50000
   * QUERY = CREATE TABLE averagedsources (
   * ERROR = !CONSTRAINT FOREIGN KEY: could not find referenced PRIMARY KEY in table 'associatedsources'
  FOREIGN KEY (xtrsrc_id1) REFERENCES associatedsources (xtrsrc_id)
  */
);
