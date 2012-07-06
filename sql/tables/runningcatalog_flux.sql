--DROP TABLE runningcatalog_flux;
/* 
 * stokes                   Stokes parameter:
 *                          1 = I, 2 = Q, 3 = U, 4 = V
 * f_datapoints             the number of datapoints for which the averages
 *                          were calculated
 * avg_f_peak               := average of peak flux
 * avg_f_peak_sq            := average of (peak flux)^2
 * avg_f_peak_weight        := average of one over peak flux errors squared
 * avg_weighted_f_peak      := average of ratio of (peak flux) and (peak flux errors squared)
 * avg_weighted_f_peak_sq   := average of ratio of (peak flux squared) and (peak flux errors squared)
 */
CREATE TABLE runningcatalog_flux
  (runcat INT NOT NULL
  ,band INT NOT NULL
  ,stokes TINYINT NOT NULL DEFAULT 1
  ,f_datapoints INT NOT NULL
  ,resolution DOUBLE NULL
  ,avg_f_peak DOUBLE NULL
  ,avg_f_peak_sq DOUBLE NULL
  ,avg_f_peak_weight DOUBLE NULL
  ,avg_weighted_f_peak DOUBLE NULL
  ,avg_weighted_f_peak_sq DOUBLE NULL
  ,avg_f_int DOUBLE NULL
  ,avg_f_int_sq DOUBLE NULL
  ,avg_f_int_weight DOUBLE NULL
  ,avg_weighted_f_int DOUBLE NULL
  ,avg_weighted_f_int_sq DOUBLE NULL
  ,PRIMARY KEY (runcat_id
               ,band
               ,stokes
               )
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (band) REFERENCES frequencyband (id)
  )
;

