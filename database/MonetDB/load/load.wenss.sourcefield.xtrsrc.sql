/*+-------------------------------------------------------------------+
 *| This script loads the pipeline.extractedsources table with the    |
 *| WENSS sources (which are selected from the catalogedsources table)|
 *+-------------------------------------------------------------------+
 *+-------------------------------------------------------------------+
 *+-------------------------------------------------------------------+
 */
SELECT insertdataset('wenss sources loaded in extractedsources');
INSERT INTO images (ds_id,tau,seq_nr,band,tau_time,freq_eff,taustart_ts,url) VALUES (2,1,1,13,1,325000000,NOW(),'wenss from extractedsources');
INSERT INTO images (ds_id,tau,seq_nr,band,tau_time,freq_eff,taustart_ts,url) VALUES (2,1,2,14,1,352000000,NOW(),'wenss from extractedsources');

INSERT INTO extractedsources
  (image_id
  ,zone
  ,ra
  ,decl
  ,ra_err
  ,decl_err
  ,x
  ,y
  ,z
  ,det_sigma
  ,i_peak
  ,i_peak_err
  ,i_int
  ,i_int_err
  )
  SELECT CASE WHEN band = 13 
              THEN 2
              ELSE 3
         END 
        ,zone
        ,ra
        ,decl
        ,ra_err
        ,decl_err
        ,x
        ,y
        ,z
        ,det_sigma
        ,i_peak_avg
        ,i_peak_avg_err
        ,i_int_avg
        ,i_int_avg_err
    FROM catalogedsources
   WHERE cat_id = 5
;

