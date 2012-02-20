--DROP FUNCTION getCountLogLRbin_CatBG;

CREATE FUNCTION getCountLogLRbin_CatBG(iassoc_lr_min DOUBLE
                                      ,iassoc_lr_max DOUBLE
                                      ) RETURNS DOUBLE
BEGIN
  
  DECLARE nsources INT;

  SELECT COUNT(*)
    INTO nsources
    FROM assoccatsources 
        ,extractedsources
        ,catalogedsources c2
   WHERE xtrsrc_id = xtrsrcid
     AND image_id > 1
     AND assoc_catsrc_id = c2.catsrcid
     AND c2.cat_id = 3
     /* To pick the BG Fields that do not have a WENSS source */
     AND assoc_weight IS NULL
     AND assoc_lr BETWEEN iassoc_lr_min 
                      AND iassoc_lr_max
  ;

  RETURN nsources;

END;

