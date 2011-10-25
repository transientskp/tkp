/* This table contains the unique sources that were detected
 * during an observation.
 * TODO: The resolution element (from images table) is not implemented yet
 * Extractedsources not in this table are appended when there is no positional match
 * or when a source was detected in a higher resolution image.
 */
--DROP TABLE tempbasesources;
CREATE TABLE tempbasesources 
  (xtrsrc_id INT NOT NULL
  ,datapoints INT NULL
  ,I_peak_sum double precision NULL
  ,I_peak_sq_sum double precision NULL
  ,weight_peak_sum double precision NULL
  ,weight_I_peak_sum double precision NULL
  ,weight_I_peak_sq_sum double precision NULL
  )
;

