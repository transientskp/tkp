/**
 * This is a temporary table, used to load
 * the detections from the sources extraction.
 */
CREATE TABLE detections 
  (lra double precision NOT NULL 
  ,ldecl double precision NOT NULL 
  ,lra_err double precision NOT NULL 
  ,ldecl_err double precision NOT NULL 
  ,lI_peak double precision NULL 
  ,lI_peak_err double precision NULL 
  ,lI_int double precision NULL 
  ,lI_int_err double precision NULL 
  ,ldet_sigma double precision NOT NULL
  )
;

