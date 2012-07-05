--DROP VIEW assocsvarindices;
/**
 * The factors determining the variability indices in the running catalog 
 * table are updated after every image is processed. These updates cause 
 * rounding errors in the final variability indices values. Therefore
 * view varindices (which runs over the runningcatalog table) is not 
 * accurate enough.
 * A more accurate query, not time-tested, which may be slower, calculates 
 * the indices based on all the source associations and is given by:
 * NOTE: Due to a bug avg(x)*avg(x) is not calculated correctly. Therefore
 * we had to create a subselect.
 */
CREATE VIEW assocsvarindices AS
  SELECT xtrsrc_id
        ,ds_id
        ,datapoints
	,wm_ra
	,wm_decl
        ,wm_ra_err
        ,wm_decl_err
        ,SQRT(datapoints
             * (avg_i_peak_sq - avg_i_peak * avg_i_peak)
             / (datapoints - 1)
             )  
         / avg_i_peak as v_nu
        ,datapoints * (avg_w_I_peak_sq - (avg_w_I_peak*avg_w_I_peak/avg_w_peak))
	 / (datapoints - 1) as eta_nu
    FROM (SELECT ax2.xtrsrc_id
		,ds_id
		,count(*) as datapoints
		,avg(x2.ra / (x2.ra_err * x2.ra_err)) /
		 avg(1 / (x2.ra_err * x2.ra_err)) as wm_ra
		,avg(x2.decl / (x2.decl_err * x2.decl_err)) /
		 avg(1 / (x2.decl_err * x2.decl_err)) as wm_decl
		,SQRT(1 / avg(1 / (x2.ra_err * x2.ra_err))) as wm_ra_err
		,SQRT(1 / avg(1 / (x2.decl_err * x2.decl_err))) as wm_decl_err
		,avg(x2.i_peak) as avg_i_peak
		,avg(x2.i_peak * x2.i_peak) as avg_i_peak_sq
		,avg(x2.i_peak * x2.i_peak / (x2.i_peak_err * x2.i_peak_err)) as avg_w_I_peak_sq
		,avg(x2.i_peak / (x2.i_peak_err * x2.i_peak_err)) as avg_w_I_peak
		,avg(1 / (x2.i_peak_err * x2.i_peak_err)) as avg_w_peak
	    FROM assocxtrsources ax2
		,extractedsources x1
		,extractedsources x2
		,images im1
	   WHERE ax2.xtrsrc_id = x1.xtrsrcid
	     AND ax2.assoc_xtrsrc_id = x2.xtrsrcid
	     AND x1.image_id = im1.imageid
	  GROUP BY im1.ds_id
		  ,ax2.xtrsrc_id
	  HAVING COUNT(*) > 1
         ) t
;

/*
 * The view should look like this:
CREATE VIEW assocsvarindices AS
  SELECT ax2.xtrsrc_id
        ,ds_id
        ,count(*) as datapoints
        ,avg(x2.ra / (x2.ra_err * x2.ra_err)) /
         avg(1 / (x2.ra_err * x2.ra_err)) as wm_ra
        ,avg(x2.decl / (x2.decl_err * x2.decl_err)) /
         avg(1 / (x2.decl_err * x2.decl_err)) as wm_decl
        ,SQRT(1 / avg(1 / (x2.ra_err * x2.ra_err))) as wm_ra_err
        ,SQRT(1 / avg(1 / (x2.decl_err * x2.decl_err))) as wm_decl_err
        ,sqrt(count(*)
             * (avg(x2.i_peak * x2.i_peak) - avg(x2.i_peak) * avg(x2.i_peak))
             / (count(*) - 1)
             )
         / avg(x2.i_peak) as v_nu
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
  GROUP BY im1.ds_id
          ,ax2.xtrsrc_id
  HAVING COUNT(*) > 1
order by eta_nu desc limit 10;
 *
 */
