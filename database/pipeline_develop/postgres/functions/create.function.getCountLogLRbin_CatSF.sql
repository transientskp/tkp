--DROP FUNCTION getCountLogLRbin_CatSF;

CREATE FUNCTION getCountLogLRbin_CatSF(iassoc_lr_min double precision
                                      ,iassoc_lr_max double precision
                                      ) RETURNS double precision as $$
  DECLARE nsources INT;
BEGIN  

  SELECT COUNT(*)
    INTO nsources
    from assoccatsources
        ,extractedsources
        ,catalogedsources c2
   where xtrsrc_id = xtrsrcid
     and image_id = 1
     and assoc_catsrc_id = c2.catsrcid
     and c2.cat_id = 3
     and assoc_lr BETWEEN iassoc_lr_min
                      AND iassoc_lr_max
  ;

  RETURN nsources;

END;
$$ language plpgsql;
