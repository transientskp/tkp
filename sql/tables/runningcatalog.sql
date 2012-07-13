/* 
 * TODO: The resolution element (from images table) is not implemented yet
*/

CREATE TABLE runningcatalog
  (id INT AUTO_INCREMENT
  ,xtrsrc INT NOT NULL
  ,dataset INT NOT NULL
  ,datapoints INT NOT NULL
  ,zone INT NOT NULL
  ,wm_ra DOUBLE NOT NULL
  ,wm_decl DOUBLE NOT NULL
  ,wm_ra_err DOUBLE NOT NULL
  ,wm_decl_err DOUBLE NOT NULL
  ,avg_wra DOUBLE NOT NULL
  ,avg_wdecl DOUBLE NOT NULL
  ,avg_weight_ra DOUBLE NOT NULL
  ,avg_weight_decl DOUBLE NOT NULL
  ,x DOUBLE NOT NULL
  ,y DOUBLE NOT NULL
  ,z DOUBLE NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT 0
  ,PRIMARY KEY(id)
  ,UNIQUE (xtrsrc)
  ,FOREIGN KEY (xtrsrc) REFERENCES extractedsource (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  )
;

