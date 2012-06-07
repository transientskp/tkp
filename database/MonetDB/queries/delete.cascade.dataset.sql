declare idsid_min,idsid_max int;
set idsid_min = 36;
set idsid_max = 36;

delete 
  from assocxtrsources 
 where xtrsrc_id in (select xtrsrc_id 
                       from assocxtrsources
                           ,extractedsources
                           ,images 
                      where xtrsrc_id = xtrsrcid 
                        and imageid = image_id 
                        /*and ds_id = ids_id*/
                        and ds_id between idsid_min and idsid_max
                    )
;

delete 
  from assoccatsources 
 where xtrsrc_id in (select xtrsrc_id 
                       from assoccatsources
                           ,extractedsources
                           ,images 
                      where xtrsrc_id = xtrsrcid 
                        and imageid = image_id 
                        /*and ds_id = ids_id*/
                        and ds_id between idsid_min and idsid_max
                    )
;

delete 
  from extractedsources 
 where xtrsrcid in (select xtrsrcid 
                      from extractedsources
                          ,images 
                     where imageid = image_id 
                        /*and ds_id = ids_id*/
                       and ds_id between idsid_min and idsid_max
                   )
;

delete 
  from images
 /*where ds_id = ids_id*/
 where ds_id between idsid_min and idsid_max
;

delete
  from datasets
 /*where dsid = ids_id*/
 where dsid between idsid_min and idsid_max
;

