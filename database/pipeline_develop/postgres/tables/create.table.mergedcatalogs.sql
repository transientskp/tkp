--DROP TABLE runningcatalog;
/* This table contains the unique sources that were detected
 * during an observation.
 * TODO: The resolution element (from images table) is not implemented yet
 * Extractedsources not in this table are appended when there is no positional match
 * or when a source was detected in a higher resolution image.
 *
 * We maintain weighted averages for the sources (see ch4, Bevington)
 * wm_ := weighted mean
 *
 * wm_ra := avg_wra/avg_weight_ra
 * wm_decl := avg_wdecl/avg_weight_decl
 * wm_ra_err := 1/(N * avg_weight_ra)
 * wm_decl_err := 1/(N * avg_weight_decl)
 * avg_wra := avg(ra/ra_err^2)
 * avg_wdecl := avg(decl/decl_err^2)
 * avg_weight_ra := avg(1/ra_err^2) 
 * avg_weight_decl := avg(1/decl_err^2)
 */
CREATE TABLE mergedcatalogs
  (catsrc_id INT NOT NULL
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
  ,I_peak_vlss double precision NULL
  ,I_peak_vlss_err double precision NULL
  ,I_int_vlss double precision NULL
  ,I_int_vlss_err double precision NULL
  ,I_peak_wenssm double precision NULL
  ,I_peak_wenssm_err double precision NULL
  ,I_int_wenssm double precision NULL
  ,I_int_wenssm_err double precision NULL
  ,I_peak_wenssp double precision NULL
  ,I_peak_wenssp_err double precision NULL
  ,I_int_wenssp double precision NULL
  ,I_int_wenssp_err double precision NULL
  ,I_peak_nvss double precision NULL
  ,I_peak_nvss_err double precision NULL
  ,I_int_nvss double precision NULL
  ,I_int_nvss_err double precision NULL
  ,alpha_v_wm double precision NULL
  ,alpha_v_wp double precision NULL
  ,alpha_v_n double precision NULL
  ,alpha_wm_wp double precision NULL
  ,alpha_wm_n double precision NULL
  ,alpha_wp_n double precision NULL
  ,alpha_v_wm_n double precision NULL
  ,chisq_v_wm_n double precision NULL
  )
;

