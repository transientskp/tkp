CREATE TABLE image 
  (id INT AUTO_INCREMENT
  ,dataset INT NOT NULL
  ,tau INT NOT NULL
  ,band INT NOT NULL
  ,stokes CHAR(1) NOT NULL DEFAULT 'I'
  ,tau_time DOUBLE NOT NULL
  ,freq_eff DOUBLE NOT NULL
  ,freq_bw DOUBLE NULL
  ,taustart_ts TIMESTAMP NOT NULL
  ,bmaj_syn DOUBLE NULL
  ,bmin_syn DOUBLE NULL
  ,bpa_syn DOUBLE NULL
  ,url VARCHAR(120) NULL
  ,node TINYINT NOT NULL DEFAULT %NODE%
  ,nodes TINYINT NOT NULL DEFAULT %NODES%
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  );

