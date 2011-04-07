SET @image_id = 1;
SET @zoneheight = 1;
SET @theta = 1;

SELECT x1.xtrsrcid
      ,x1.image_id
      ,im1.ds_id
      ,a1.xtrsrc_id
      ,x2.xtrsrcid
      ,x2.image_id
      ,im2.ds_id
  FROM extractedsources x1
      ,images im1
      ,associatedsources a1
      ,extractedsources x2
      ,images im2
 WHERE x1.image_id = @image_id
   AND x1.image_id = im1.imageid
   AND im1.ds_id = (SELECT im3.ds_id
                      FROM images im3
                     WHERE im3.imageid = @image_id
                   )
   AND a1.xtrsrc_id = x2.xtrsrcid
   AND x2.image_id = im2.imageid
   AND im2.ds_id = im1.ds_id
   AND x2.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                   AND FLOOR((x1.decl + @theta) / @zoneheight)
   AND x2.ra BETWEEN (x1.ra - alpha(@theta,x1.decl))
                 AND (x1.ra + alpha(@theta,x1.decl))
   AND x2.decl BETWEEN x1.decl - @theta
                   AND x1.decl + @theta
   AND doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
;

/* to also select the extracted sources that do not have associations 
* we have to perform an outer join
*/

/*
SELECT COUNT(*)
  FROM extractedsources x1
      ,images       
      ,datasets       
      ,extractedsources x2       
      ,associatedsources     
 WHERE x1.image_id = imageid    
   AND ds_id = dsid    
   AND dsid = (SELECT ds_id                  
                 FROM images                 
                WHERE imageid = @image_id               
              )    
   AND x1.image_id <> @image_id    
   AND x2.image_id = @image_id    
   AND xtrsrc_id = x2.xtrsrcid    
   AND dosourcesintersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
;

insert into associatedsources 
  (xtrsrc_id
  ,insert_src1
  ,assoc_type
  ,assoc_xtrsrc_id
  ,insert_src2
  ) 
  select xtrsrcid
        ,true
        ,'X'
        ,xtrsrcid
        ,false 
    from extractedsources 
   where image_id = @image_id
;

SELECT x1.xtrsrcid AS xtr
      ,x2.xtrsrcid AS assoc_xtr
  FROM extractedsources x1
      ,images       
      ,datasets       
      ,extractedsources x2       
 WHERE x1.image_id = imageid    
   AND ds_id = dsid    
   AND dsid = (SELECT ds_id                  
                 FROM images                 
                WHERE imageid = @image_id               
              )    
   AND x1.image_id <> @image_id    
   AND x2.image_id = @image_id    
   AND dosourcesintersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
;
*/
