/* 
 * Here we select the source that has the maximum value of sigma over mu
 */
SELECT t.xtrsrc_id
  FROM (SELECT ax2.xtrsrc_id
              ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int)) 
                   / (count(*)-1))
               /avg(x2.i_int) as sigma_over_mu
          FROM assocxtrsources ax2
              ,extractedsources x1
              ,extractedsources x2
              ,images im1
         WHERE ax2.xtrsrc_id = x1.xtrsrcid
           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid
           AND x1.image_id = im1.imageid
           AND im1.ds_id = 7
        GROUP BY ax2.xtrsrc_id 
       ) t
 WHERE t.sigma_over_mu = (SELECT MAX(t0.sigma_over_mu)
                            FROM (SELECT sqrt(count(*) 
                                             * (avg(x2.i_int * x2.i_int) 
                                               - avg(x2.i_int) * avg(x2.i_int)
                                               ) / (count(*) - 1)
                                             )
                                             / avg(x2.i_int) AS sigma_over_mu
                                    FROM assocxtrsources ax2
                                        ,extractedsources x1
                                        ,extractedsources x2
                                        ,images im1
                                   WHERE ax2.xtrsrc_id = x1.xtrsrcid
                                     AND ax2.assoc_xtrsrc_id = x2.xtrsrcid
                                     AND x1.image_id = im1.imageid
                                     AND im1.ds_id = 7
                                  GROUP BY ax2.xtrsrc_id 
                                 ) t0
                         )
;

SELECT t.xtrsrc_id
  FROM (SELECT ax2.xtrsrc_id
              ,count(*) as datapoints
              ,1000 * min(x2.i_int) as min_i_int_mJy
              ,1000 * avg(x2.i_int) as avg_i_int_mJy
              ,1000 * max(x2.i_int) as max_i_int_mJy
              ,sqrt(count(*) * (avg(x2.i_int * x2.i_int) - avg(x2.i_int) * avg(x2.i_int)) 
                   / (count(*)-1))
               /avg(x2.i_int) as sigma_over_mu
          FROM assocxtrsources ax2
              ,extractedsources x1
              ,extractedsources x2
              ,images im1
         WHERE ax2.xtrsrc_id = x1.xtrsrcid
           AND ax2.assoc_xtrsrc_id = x2.xtrsrcid
           AND x1.image_id = im1.imageid
           AND im1.ds_id = 7
        GROUP BY ax2.xtrsrc_id 
       ) t
 WHERE t.sigma_over_mu = (SELECT MAX(t0.sigma_over_mu)
                            FROM (SELECT sqrt(count(*) 
                                             * (avg(x2.i_int * x2.i_int) 
                                               - avg(x2.i_int) * avg(x2.i_int)
                                               ) / (count(*) - 1)
                                             )
                                             / avg(x2.i_int) AS sigma_over_mu
                                    FROM assocxtrsources ax2
                                        ,extractedsources x1
                                        ,extractedsources x2
                                        ,images im1
                                   WHERE ax2.xtrsrc_id = x1.xtrsrcid
                                     AND ax2.assoc_xtrsrc_id = x2.xtrsrcid
                                     AND x1.image_id = im1.imageid
                                     AND im1.ds_id = 7
                                  GROUP BY ax2.xtrsrc_id 
                                 ) t0
                         )
;

