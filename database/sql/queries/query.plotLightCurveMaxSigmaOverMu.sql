DECLARE ids_id INT;
SET ids_id = 22;

SELECT t.xtrsrc_id 
      ,t.sigma_over_mu 
  FROM (SELECT ax2.xtrsrc_id 
              ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int))/ (count(*)-1)) /avg(x2.i_int) as sigma_over_mu 
          FROM assocxtrsources ax2 
              ,extractedsources x1 
              ,extractedsources x2 
              ,images im1 
         WHERE ax2.xtrsrc_id = x1.xtrsrcid 
           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
           AND x1.image_id = im1.imageid 
           AND im1.ds_id = ids_id
        GROUP BY ax2.xtrsrc_id 
       ) t 
 WHERE t.sigma_over_mu = (SELECT MAX(t0.sigma_over_mu) 
                            FROM (SELECT sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int)) / (count(*) - 1)) / avg(x2.i_int) AS sigma_over_mu 
                                    FROM assocxtrsources ax2 
                                        ,extractedsources x1 
                                        ,extractedsources x2 
                                        ,images im1 
                                   WHERE ax2.xtrsrc_id = x1.xtrsrcid 
                                     AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
                                     AND x1.image_id = im1.imageid 
                                     AND im1.ds_id = ids_id
                                  GROUP BY ax2.xtrsrc_id 
                                 ) t0 
                         )
;
