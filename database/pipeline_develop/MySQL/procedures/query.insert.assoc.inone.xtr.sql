SET @image_id = 1;
SET @zoneheight = 1;
SET @theta = 1;

select x1.xtrsrcid
      ,x1.image_id
      ,a1.xtrsrc_id
      ,x2.xtrsrcid
      ,x2.image_id
      ,doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                         ,x2.ra,x2.decl,x2.ra_err,x2.decl_err
                         ) AS 'do_intersect' 
  from extractedsources x1
      ,images im1
      ,extractedsources x2 
       left outer join associatedsources a1 
       on a1.xtrsrc_id = x2.xtrsrcid
      ,images im2 
 where  x2.image_id = im2.imageid 
   and x1.image_id = @image_id 
   and im1.ds_id = (select im3.ds_id 
                      from images im3 
                     where im3.imageid = @image_id
                   ) 
   and im2.ds_id = im1.ds_id
;

stop
/* Query to select new sources in current image
 * i.e. no associations could be found in associatedsources.
 * 
 * All sources from image_id = 2 that do NOT intersect with sources 
 * from images with the same ds_id as image_id = 2 
 */
select x1.xtrsrcid
  from extractedsources x1
      ,associatedsources a1
      ,extractedsources x2
      ,images im2 
 where x1.image_id = @image_id 
   and a1.xtrsrc_id = x2.xtrsrcid 
   and x2.image_id = im2.imageid 
   and im2.ds_id = (select ds_id 
                      from images im3 
                     where imageid = @image_id
                   ) 
   and not doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                             ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)
   and x1.xtrsrcid not in (SELECT x3.xtrsrcid       
                             FROM extractedsources x3       
                                 ,images im4       
                                 ,associatedsources a2       
                                 ,extractedsources x4       
                                 ,images im5  
                            WHERE x3.image_id = @image_id    
                              AND x3.image_id = im4.imageid    
                              AND im4.ds_id = (SELECT im6.ds_id                       
                                                 FROM images im6                      
                                                WHERE im6.imageid = @image_id                    
                                              )    
                              AND a2.xtrsrc_id = x4.xtrsrcid    
                              AND x4.image_id = im5.imageid    
                              AND im5.ds_id = im4.ds_id    
                              AND x4.zone BETWEEN FLOOR((x3.decl - @theta) / @zoneheight) 
                                              AND FLOOR((x3.decl + @theta) / @zoneheight)   
                              AND x4.ra BETWEEN (x3.ra - alpha(@theta,x3.decl))
                                            AND (x3.ra + alpha(@theta,x3.decl))    
                              AND x4.decl BETWEEN x3.decl - @theta
                                              AND x3.decl + @theta 
                              AND doSourcesIntersect(x3.ra,x3.decl,x3.ra_err,x3.decl_err
                                                    ,x4.ra,x4.decl,x4.ra_err,x4.decl_err)
                          )
GROUP BY x1.xtrsrcid
;

/*sources from image_id = 2 that DO intersect with sources from image_id = 1 */
SELECT x1.xtrsrcid       
      ,x1.image_id       
      ,im1.ds_id       
      ,a1.xtrsrc_id       
      ,x2.xtrsrcid       
      ,doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                         ,x2.ra,x2.decl,x2.ra_err,x2.decl_err
                         ) AS 'do_intersect'   
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
   AND doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                         ,x2.ra,x2.decl,x2.ra_err,x2.decl_err)

;










select a1.xtrsrc_id 
  from associatedsources a1
      ,extractedsources x2
      ,images im2 
 where a1.xtrsrc_id = x2.xtrsrcid 
   and x2.image_id = im2.imageid 
   and im2.ds_id = (select ds_id 
                      from images im3 
                     where imageid = @image_id
                   )
;


SELECT x1.xtrsrcid
      ,x1.image_id
      ,im1.ds_id
      ,a1.xtrsrc_id
      ,x2.xtrsrcid 
      ,doSourcesIntersect(x1.ra,x1.decl,x1.ra_err,x1.decl_err
                         ,x2.ra,x2.decl,x2.ra_err,x2.decl_err
                         ) AS 'do_intersect'
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

;

/*SELECT x1.xtrsrcid
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
*/
/* to also select the extracted sources that do not have associations 
* we have to perform an outer join
*/
/*
delete from associatedsources;
alter table associatedsources auto_increment = 1;
delete from extractedsources;
alter table extractedsources auto_increment = 1;
delete from images;
alter table images auto_increment = 1;
delete from datasets;
alter table datasets auto_increment = 1;
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
