select ac1.*,x1.image_id,im1.band from assocxtrsources ac1,extractedsources x1,images im1 where image_id = imageid and assoc_xtrsrc_id = xtrsrcid and xtrsrc_id in (select xtrsrc_id from assocxtrsources ac1,extractedsources x1,images im1 where image_id = imageid and assoc_xtrsrc_id = xtrsrcid  and im1.band = 14 group by xtrsrc_id having count(*) = 10) and im1.band = 14 order by xtrsrc_id,assoc_xtrsrc_id;


