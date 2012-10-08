SELECT t1.runcat
      ,t1.dataset
      ,t1.band
      ,t1.f_datapoints
      ,t1.wm_ra
      ,t1.wm_decl
      ,t1.wm_ra_err
      ,t1.wm_decl_err
      ,t1.V_int_inter / t1.avg_f_int AS V_int
      ,t1.eta_int_inter / t1.avg_f_int_weight AS eta_int
      ,t1.trigger_xtrsrc
      ,CASE WHEN m0.runcat IS NULL
            THEN FALSE
            ELSE TRUE
       END AS monitored
      ,tr0.id 
  FROM (SELECT rf0.runcat
              ,im0.dataset
              ,im0.band
              ,f_datapoints
              ,wm_ra
              ,wm_decl
              ,wm_ra_err
              ,wm_decl_err
              ,avg_f_int
              ,avg_f_int_weight
              ,CASE WHEN rf0.f_datapoints = 1
                    THEN 0
                    ELSE SQRT(CAST(rf0.f_datapoints AS DOUBLE) * (avg_f_int_sq - avg_f_int * avg_f_int) 
                              / (CAST(rf0.f_datapoints AS DOUBLE) - 1.0)
                             )
               END AS V_int_inter
              ,CASE WHEN rf0.f_datapoints = 1
                    THEN 0
                    ELSE (CAST(rf0.f_datapoints AS DOUBLE) / (CAST(rf0.f_datapoints AS DOUBLE) - 1.0)) 
                          * (avg_f_int_weight * avg_weighted_f_int_sq - avg_weighted_f_int * avg_weighted_f_int)
               END AS eta_int_inter
              ,x0.id AS trigger_xtrsrc
          FROM runningcatalog rc0
              ,runningcatalog_flux rf0
              ,image im0
              ,assocxtrsource a0
              ,extractedsource x0
         WHERE im0.id = 3
           AND rc0.dataset = im0.dataset
           AND rc0.id = rf0.runcat
           AND rf0.band = im0.band
           AND a0.runcat = rc0.id
           AND x0.id = a0.xtrsrc
           AND x0.image = im0.id
       ) t1
       LEFT OUTER JOIN monitoringlist m0
       ON t1.runcat = m0.runcat
       LEFT OUTER JOIN transient tr0
       ON t1.runcat = tr0.runcat
       AND t1.band = tr0.band
 WHERE t1.V_int_inter / t1.avg_f_int > 0.1
   AND t1.eta_int_inter / t1.avg_f_int_weight > 1.0
;
