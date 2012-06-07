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
  ,I_peak_vlss DOUBLE NULL
  ,I_peak_vlss_err DOUBLE NULL
  ,I_int_vlss DOUBLE NULL
  ,I_int_vlss_err DOUBLE NULL
  ,I_peak_wenssm DOUBLE NULL
  ,I_peak_wenssm_err DOUBLE NULL
  ,I_int_wenssm DOUBLE NULL
  ,I_int_wenssm_err DOUBLE NULL
  ,I_peak_wenssp DOUBLE NULL
  ,I_peak_wenssp_err DOUBLE NULL
  ,I_int_wenssp DOUBLE NULL
  ,I_int_wenssp_err DOUBLE NULL
  ,I_peak_nvss DOUBLE NULL
  ,I_peak_nvss_err DOUBLE NULL
  ,I_int_nvss DOUBLE NULL
  ,I_int_nvss_err DOUBLE NULL
  ,alpha_v_wm DOUBLE NULL
  ,alpha_v_wp DOUBLE NULL
  ,alpha_v_n DOUBLE NULL
  ,alpha_wm_wp DOUBLE NULL
  ,alpha_wm_n DOUBLE NULL
  ,alpha_wp_n DOUBLE NULL
  ,alpha_v_wm_n DOUBLE NULL
  ,chisq_v_wm_n DOUBLE NULL
  )
;

