--DROP TABLE tempmultcatbasesources;
/* This table contains the unique sources that were detected
 * during an observation.
 * TODO: The resolution element (from images table) is not implemented yet
 * Extractedsources not in this table are appended when there is no positional match
 * or when a source was detected in a higher resolution image.
 */
--DROP TABLE tempbasesources;
CREATE TABLE tempmultcatbasesources 
  (xtrsrc_id INT NOT NULL
  ,assoc_xtrsrc_id INT NOT NULL
  ,zone INT NOT NULL
  ,ra_avg DOUBLE NOT NULL
  ,decl_avg DOUBLE NOT NULL
  ,ra_err_avg DOUBLE NOT NULL
  ,decl_err_avg DOUBLE NOT NULL
  ,x DOUBLE NOT NULL
  ,y DOUBLE NOT NULL
  ,z DOUBLE NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT 0
  ,beam_semimaj DOUBLE NULL
  ,beam_semimin DOUBLE NULL
  ,beam_pa DOUBLE NULL
  ,datapoints INT NOT NULL
  ,avg_weighted_ra DOUBLE NOT NULL
  ,avg_weighted_decl DOUBLE NOT NULL
  ,avg_ra_weight DOUBLE NOT NULL
  ,avg_decl_weight DOUBLE NOT NULL
  ,I_peak_sum DOUBLE NULL
  ,I_peak_sq_sum DOUBLE NULL
  ,weight_peak_sum DOUBLE NULL
  ,weight_I_peak_sum DOUBLE NULL
  ,weight_I_peak_sq_sum DOUBLE NULL
  )
;

