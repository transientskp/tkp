/**
 */
CREATE SEQUENCE "seq_detection" AS INTEGER;

CREATE TABLE detections (
  detid INT NOT NULL DEFAULT NEXT VALUE FOR "seq_detection",
  image_id INT NOT NULL, 
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  det_sigma DOUBLE NOT NULL,
  I_peak DOUBLE NULL,
  I_peak_err DOUBLE NULL,
  Q_peak DOUBLE NULL,
  Q_peak_err DOUBLE NULL,
  U_peak DOUBLE NULL,
  U_peak_err DOUBLE NULL,
  V_peak DOUBLE NULL,
  V_peak_err DOUBLE NULL,
  I_int DOUBLE NULL,
  I_int_err DOUBLE NULL,
  Q_int DOUBLE NULL,
  Q_int_err DOUBLE NULL,
  U_int DOUBLE NULL,
  U_int_err DOUBLE NULL,
  V_int DOUBLE NULL,
  V_int_err DOUBLE NULL,
  PRIMARY KEY (detid),
  FOREIGN KEY (image_id) REFERENCES images (imageid)
);
