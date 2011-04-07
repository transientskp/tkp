SET @catname = 'NVSS';
SET @theta = 1;
SET @xtrsrcid = 4;
SET @zoneheight = 1;
  
  SELECT COUNT(*)
    FROM extractedsources x1
        ,catalogedsources c1
        ,catalogs c0
   WHERE c1.cat_id = c0.catid
     AND c0.catname = @catname
     AND x1.xtrsrcid = @xtrsrcid
     AND c1.x * x1.x + c1.y * x1.y + c1.z * x1.z > COS(RADIANS(@theta))
     AND c1.zone BETWEEN FLOOR((x1.decl - @theta) / @zoneheight)
                     AND FLOOR((x1.decl + @theta) / @zoneheight)
     AND c1.ra BETWEEN x1.ra - alpha(@theta, x1.decl)
                   AND x1.ra + alpha(@theta, x1.decl)
     AND c1.decl BETWEEN x1.decl - @theta
                     AND x1.decl + @theta


