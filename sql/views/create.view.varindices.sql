--DROP VIEW varindices;

CREATE VIEW varindices AS
  SELECT xtrsrc_id
        ,ds_id
	,datapoints
	,wm_ra
	,wm_decl
	,wm_ra_err
	,wm_decl_err
	,SQRT(datapoints * 
	      (avg_i_peak_sq - (avg_i_peak * avg_i_peak)) 
	      / (datapoints - 1)
	     ) / avg_i_peak AS V_nu 
        ,(datapoints / (datapoints - 1)) *
	 (avg_weighted_i_peak_sq 
	  - (avg_weighted_i_peak * avg_weighted_i_peak) / avg_weight_peak
	 ) AS eta_nu
    FROM runningcatalog
;

/**
 * The factors determining the variability indices in the running catalog 
 * table are updated with every image. This causes rounding errors in the
 * final variability indices values. 
 * A more accurate query, not time-tested, which may be slower, calculates 
 * the indices based on all the source associations and is given by:
 *
SELECT ax2.xtrsrc_id
      ,count(*) as datapoints
      ,sqrt(count(*)
           * (avg(x2.i_peak * x2.i_peak) - avg(x2.i_peak) * avg(x2.i_peak))
           / (count(*) - 1)
           )
       / avg(x2.i_peak) as V_nu
      ,count(*) * (avg(x2.i_peak * x2.i_peak / (x2.i_peak_err * x2.i_peak_err)) 
                  - (avg(x2.i_peak / (x2.i_peak_err * x2.i_peak_err))
                     * avg(x2.i_peak / (x2.i_peak_err * x2.i_peak_err))
                     / avg(1 / (x2.i_peak_err * x2.i_peak_err))
		    )
                  )
                / (count(*) - 1) as eta_nu
  FROM assocxtrsources ax2
      ,extractedsources x1
      ,extractedsources x2
      ,images im1
 WHERE ax2.xtrsrc_id = x1.xtrsrcid
   AND ax2.assoc_xtrsrc_id = x2.xtrsrcid
   AND x1.image_id = im1.imageid
GROUP BY ax2.xtrsrc_id
HAVING COUNT(*) > 1
ORDER BY eta_nu
;
 *
 */
