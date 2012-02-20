/* This table contains the unique sources that were detected
 * during an observation.
 * TODO: The resolution element (from images table) is not implemented yet
 * Extractedsources not in this table are appended when there is no positional match
 * or when a source was detected in a higher resolution image.
 */
--DROP TABLE tempbasesources;
CREATE TABLE tempbasesources 
  (xtrsrc_id INT NOT NULL
  /*,ds_id INT NOT NULL
  ,image_id INT NOT NULL
  ,zone INT NOT NULL
  ,ra DOUBLE NOT NULL
  ,decl DOUBLE NOT NULL
  ,ra_err DOUBLE NOT NULL
  ,decl_err DOUBLE NOT NULL
  ,x DOUBLE NOT NULL
  ,y DOUBLE NOT NULL
  ,z DOUBLE NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT 0
  ,beam_semimaj DOUBLE NULL
  ,beam_semimin DOUBLE NULL
  ,beam_pa DOUBLE NULL*/
  ,datapoints INT NULL
  ,I_peak_sum DOUBLE NULL
  ,I_peak_sq_sum DOUBLE NULL
  ,weight_peak_sum DOUBLE NULL
  ,weight_I_peak_sum DOUBLE NULL
  ,weight_I_peak_sq_sum DOUBLE NULL
  )
;

