declare itheta,izoneheight,ira,idecl double;
declare icatname varchar(50);
set icatname = 'VLSS';
set itheta = 1;
set izoneheight = 1;
set ira = 217;
set idecl = 53;

SELECT catsrcid
      ,ra
      ,decl
      ,ra2hms(ra)
      ,decl2dms(decl)
      ,c1.freq_eff
      ,c1.i_int_avg
      ,3600 * DEGREES(2 * ASIN(SQRT( (c1.x - COS(radians(idecl)) * COS(radians(ira))) 
                                     * (c1.x - COS(radians(idecl)) * COS(radians(ira))) 
                                   + (c1.y - COS(radians(idecl)) * SIN(radians(ira)))
                                     * (c1.y - COS(radians(idecl)) * SIN(radians(ira)))
                                   + (c1.z - SIN(radians(idecl))) 
                                     * (c1.z - SIN(radians(idecl)))
                                   ) 
                              / 2
                              )
                     ) as dist_arcsec
  FROM catalogedsources c1
      ,catalogs c0
   WHERE c1.cat_id = c0.catid
     AND c0.catname = upper(icatname)
     AND c1.x * COS(RADIANS(idecl)) * COS(RADIANS(ira)) 
         + c1.y * COS(RADIANS(idecl)) * SIN(RADIANS(ira)) 
         + c1.z * SIN(RADIANS(idecl)) > COS(RADIANS(itheta))
     AND c1.zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                     AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
     AND c1.ra BETWEEN ira - alpha(itheta, idecl)
                   AND ira + alpha(itheta, idecl)
     AND c1.decl BETWEEN idecl - itheta
                     AND idecl + itheta
     AND c1.i_int_avg = (SELECT MAX(c1.i_int_avg)
                           FROM catalogedsources c1
                               ,catalogs c0
                          WHERE c1.cat_id = c0.catid
                            AND c0.catname = icatname
                            AND c1.x * COS(RADIANS(idecl)) * COS(RADIANS(ira)) 
                                + c1.y * COS(RADIANS(idecl)) * SIN(RADIANS(ira)) 
                                + c1.z * SIN(RADIANS(idecl)) > COS(RADIANS(itheta))
                            AND c1.zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                                            AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
                            AND c1.ra BETWEEN ira - alpha(itheta, idecl)
                                          AND ira + alpha(itheta, idecl)
                            AND c1.decl BETWEEN idecl - itheta
                                            AND idecl + itheta
                        )
  ;

