/* This file lists all the queries that are executed within the 
 * pipeline database.
 */

(1) in ASSOCSRC()

  INSERT INTO extractedsources
    (image_id
    ,zone
    ,ra
    ,decl
    ,ra_err
    ,decl_err
    ,x
    ,y
    ,z
    ,det_sigma
    ,I_peak
    ,I_peak_err
    ,I_int
    ,I_int_err
    ) 
  VALUES
    (iimage_id
    ,izone
    ,ira
    ,idecl
    ,ira_err
    ,idecl_err
    ,ix
    ,iy
    ,iz
    ,idet_sigma
    ,iI_peak
    ,iI_peak_err
    ,iI_int
    ,iI_int_err
    )
  ;
 
(2)

  INSERT INTO assocxtrsrcids
    SELECT xtrsrcid AS assocxtrsrcid
           /*
           ,DEGREES(2 * ASIN(SQRT(POW(x - @x, 2) + 
                                  POW(y - @y, 2) + 
                                  POW(z - @z, 2)) / 2)) AS distance
           */
      FROM extractedsources
          ,images
     WHERE imageid = image_id
       AND ds_id = (SELECT ds_id 
                      FROM images 
                     WHERE imageid = iimage_id
                   )
       AND image_id < iimage_id
       AND zone BETWEEN FLOOR((idecl - itheta)/izoneheight)
                    AND FLOOR((idecl + itheta)/izoneheight)
       AND ra BETWEEN ira - ialpha
                  AND ira + ialpha
       AND decl BETWEEN idecl - itheta
                    AND idecl + itheta
       /*
       AND 4 * POW(SIN(RADIANS(itheta / 2)), 2) > 
           POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
       */
       AND sin_itheta > SIN(2 * ASIN(SQRT(POW(x - ix, 2) + 
                                          POW(y - iy, 2) + 
                                          POW(z - iz, 2)) / 2))
       AND doIntersectElls(ira,idecl,ira_err,idecl_err
                          ,ra,decl,ra_err,decl_err)
  ;

(3)

  SELECT COUNT(*) 
    INTO nassoc_xtrsrcid
    FROM assocxtrsrcids
  ;

(4)

    INSERT INTO associatedsources
      (xtrsrc_id
      ,src_type
      ,assoc_xtrsrcid
      )
      SELECT xtrsrc_id
            ,'X'
            ,ixtrsrcid
        FROM associatedsources
            ,assocxtrsrcids
            ,extractedsources 
     WHERE xtrsrc_id = xtrsrcid 
       AND assocxtrsrcid = assoc_xtrsrcid 
       AND zone BETWEEN FLOOR((idecl - itheta)/izoneheight)
                    AND FLOOR((idecl + itheta)/izoneheight)
       AND ra BETWEEN ira - ialpha
                  AND ira + ialpha
       AND decl BETWEEN idecl - itheta
                    AND idecl + itheta
       /*
       AND 4 * POW(SIN(RADIANS(itheta / 2)), 2) > 
               POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
       */
       AND sin_itheta > SIN(2 * ASIN(SQRT(POW(x - ix, 2) + 
                                          POW(y - iy, 2) + 
                                          POW(z - iz, 2)) / 2))
       AND doIntersectElls(ira,idecl,ira_err,idecl_err
                          ,ra,decl,ra_err,decl_err)
    GROUP BY xtrsrc_id
    ;
  
(5)

    INSERT INTO associatedsources
      (xtrsrc_id
      ,src_type
      ,assoc_xtrsrcid
      )
    VALUES 
      (ixtrsrcid
      ,'X'
      ,ixtrsrcid
      )
    ;

(6)

  INSERT INTO assoccatsrcids
    SELECT catsrcid AS assoccatsrcid
      FROM catalogedsources
     WHERE zone BETWEEN FLOOR((idecl - itheta)/izoneheight)
                    AND FLOOR((idecl + itheta)/izoneheight)
       AND ra BETWEEN ira - ialpha
                  AND ira + ialpha
       AND decl BETWEEN idecl - itheta
                    AND idecl + itheta
       AND 4 * POW(sin_itheta, 2) > 
           POW(x - ix, 2) + POW(y - iy, 2) + POW(z - iz, 2)
       AND doIntersectElls(ira,idecl,ira_err,idecl_err
                          ,ra,decl,ra_err,decl_err)
  ;

(7)

  SELECT COUNT(*) 
    INTO nassoc_catsrcid
    FROM assoccatsrcids
  ;

(8)
    INSERT INTO associatedsources
      (xtrsrc_id
      ,src_type
      ,assoc_catsrcid
      )
      SELECT ixtrsrcid
            ,'C'
            ,assoccatsrcid
        FROM assoccatsrcids
    ;
    
(9)

    INSERT INTO associatedsources
      (xtrsrc_id
      ,src_type
      )
    VALUES 
      (ixtrsrcid
      ,'C'
      )
    ;

