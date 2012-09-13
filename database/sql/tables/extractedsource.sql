CREATE TABLE extractedsource
  (id INT AUTO_INCREMENT
  ,image INT NOT NULL
  ,zone INT NOT NULL
  ,ra DOUBLE NOT NULL
  ,decl DOUBLE NOT NULL
  ,ra_err DOUBLE NOT NULL
  ,decl_err DOUBLE NOT NULL
  ,x DOUBLE NOT NULL
  ,y DOUBLE NOT NULL
  ,z DOUBLE NOT NULL
  ,racosdecl DOUBLE NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT 0
  ,det_sigma DOUBLE NOT NULL
  ,semimajor DOUBLE NULL
  ,semiminor DOUBLE NULL
  ,pa DOUBLE NULL
  ,f_peak DOUBLE NULL
  ,f_peak_err DOUBLE NULL
  ,f_int DOUBLE NULL
  ,f_int_err DOUBLE NULL
  ,extract_type TINYINT NULL
  ,node TINYINT NOT NULL DEFAULT %NODE%
  ,nodes TINYINT NOT NULL DEFAULT %NODES%
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (image) REFERENCES image (id)
  )
;

