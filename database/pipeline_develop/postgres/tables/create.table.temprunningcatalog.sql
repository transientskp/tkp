--DROP TABLE temprunningcatalog;
/* This table contains the unique sources that were detected
 * during an observation.
 * TODO: The resolution element (from images table) is not implemented yet
 * Extractedsources not in this table are appended when there is no positional match
 * or when a source was detected in a higher resolution image.
 */
--DROP TABLE tempbasesources;
CREATE TABLE temprunningcatalog 
  (xtrsrc_id INT NOT NULL
  ,assoc_xtrsrc_id INT NOT NULL
  ,ds_id INT NOT NULL
  ,datapoints INT NOT NULL
  ,zone INT NOT NULL
  ,wm_ra double precision NOT NULL
  ,wm_decl double precision NOT NULL
  ,wm_ra_err double precision NOT NULL
  ,wm_decl_err double precision NOT NULL
  ,avg_wra double precision NOT NULL
  ,avg_wdecl double precision NOT NULL
  ,avg_weight_ra double precision NOT NULL
  ,avg_weight_decl double precision NOT NULL
  ,x double precision NOT NULL
  ,y double precision NOT NULL
  ,z double precision NOT NULL
  ,margin boolean not null default false
  ,beam_semimaj double precision NULL
  ,beam_semimin double precision NULL
  ,beam_pa double precision NULL
  ,avg_I_peak double precision NULL
  ,avg_I_peak_sq double precision NULL
  ,avg_weight_peak double precision NULL
  ,avg_weighted_I_peak double precision NULL
  ,avg_weighted_I_peak_sq double precision NULL
  )
;

