/**
 * This is a temporary table, used to load
 * the detections from the sources extraction.
 */
CREATE TABLE detections 
  (lra DOUBLE NOT NULL 
  ,ldecl DOUBLE NOT NULL 
  ,lra_err DOUBLE NOT NULL 
  ,ldecl_err DOUBLE NOT NULL 
  ,lI_peak DOUBLE NULL 
  ,lI_peak_err DOUBLE NULL 
  ,lI_int DOUBLE NULL 
  ,lI_int_err DOUBLE NULL 
  ,ldet_sigma DOUBLE NOT NULL
  ,lsemimajor DOUBLE 
  ,lsemiminor DOUBLE 
  ,lpa DOUBLE 
  )
;

