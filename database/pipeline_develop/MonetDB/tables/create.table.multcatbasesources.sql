--DROP TABLE multcatbasesources;
/* This table contains the unique sources that were detected
 * during an observation.
 * TODO: The resolution element (from images table) is not implemented yet
 * Extractedsources not in this table are appended when there is no positional match
 * or when a source was detected in a higher resolution image.
 *
 * avg_weighted_ra := avg(ra/(ra_err*ra_err))
 * avg_ra_weight := avg(1/(ra_err*ra_err))
 */
CREATE TABLE multcatbasesources 
  (xtrsrc_id INT NOT NULL
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

