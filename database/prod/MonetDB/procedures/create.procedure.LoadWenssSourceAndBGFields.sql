--DROP PROCEDURE LoadWenssSourceAndBGFields;
/*+-------------------------------------------------------------------+
 *| This procedure loads the WENSS sources into the extractedsources  |
 *| table.                                                            |
 *| In this way they can be treated as if they were detected in a     |
 *| regular way.                                                      |
 *| WENSS sources loaded with their original positions are in the     |
 *| so-called Source Field, whereas WENSS sources generated with an   |
 *| positional offset (W,NW,N,NE,E,SE,S,SW) are in a Background Field,|
 *| of which we have 8.                                               |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */
CREATE PROCEDURE LoadWenssSourceAndBGFields()
BEGIN

  DECLARE ods_id, oimageid_13, oimageid_14 INT;
  DECLARE ibgfield INT;
  DECLARE izoneheight, itheta DOUBLE;
  
  SET ods_id = insertDataset('wenss-nvss source field');
  SET oimageid_13 = insertBackgroundImage(ods_id,1,13,1,325000000,NOW(),'325MHz WENSS Src Field');
  SET oimageid_14 = insertBackgroundImage(ods_id,1,14,1,352000000,NOW(),'352MHz WENSS Src Field');
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
    ,i_peak
    ,i_peak_err
    ,i_int
    ,i_int_err
    )
    SELECT CASE WHEN band = 13 
                THEN oimageid_13
                ELSE oimageid_14
           END 
          ,zone
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,x
          ,y
          ,z
          ,det_sigma
          ,i_peak_avg
          ,i_peak_avg_err
          ,i_int_avg
          ,i_int_avg_err
      FROM catalogedsources
     WHERE cat_id = 5
  ;
  
  SET izoneheight = 1;
  SET itheta = 0.025;
  SET ibgfield = 1;
  
  WHILE ibgfield < 9 DO
    IF ibgfield = 1 THEN
      SET ods_id = insertDataset('wenss-nvss background fields W');
      SET oimageid_13 = insertBackgroundImage(ods_id,1,13,1,325000000,NOW(),'325MHz WENSS BG Field W');
      SET oimageid_14 = insertBackgroundImage(ods_id,1,14,1,352000000,NOW(),'352MHz WENSS BG Field W');
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
        ,i_peak
        ,i_peak_err
        ,i_int
        ,i_int_err
        )
        SELECT CASE WHEN band = 13 
                    THEN oimageid_13
                    ELSE oimageid_14
               END 
              ,CAST(FLOOR(decl/izoneheight) AS INTEGER)
              ,ra - alpha(2 * itheta, decl)
              ,decl
              ,ra_err
              ,decl_err
              ,COS(RADIANS(decl)) * COS(RADIANS(ra - alpha(2 * itheta, decl)))
              ,COS(RADIANS(decl)) * SIN(RADIANS(ra - alpha(2 * itheta, decl)))
              ,SIN(RADIANS(decl))
              ,det_sigma
              ,i_peak_avg
              ,i_peak_avg_err
              ,i_int_avg
              ,i_int_avg_err
          FROM catalogedsources
         WHERE cat_id = 5
      ;
    END IF;
    IF ibgfield = 2 THEN
      SET ods_id = insertDataset('wenss-nvss background fields NW');
      SET oimageid_13 = insertBackgroundImage(ods_id,1,13,1,325000000,NOW(),'325MHz WENSS BG Field NW');
      SET oimageid_14 = insertBackgroundImage(ods_id,1,14,1,352000000,NOW(),'352MHz WENSS BG Field NW');
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
        ,i_peak
        ,i_peak_err
        ,i_int
        ,i_int_err
        )
        SELECT CASE WHEN band = 13 
                    THEN oimageid_13
                    ELSE oimageid_14
               END 
              ,CAST(FLOOR((decl + 2 * itheta)/izoneheight) AS INTEGER)
              ,ra - alpha(2 * itheta, decl + 2 * itheta)
              ,decl + 2 * itheta
              ,ra_err
              ,decl_err
              ,COS(RADIANS(decl + 2 * itheta)) * COS(RADIANS(ra - alpha(2 * itheta, decl + 2 * itheta)))
              ,COS(RADIANS(decl + 2 * itheta)) * SIN(RADIANS(ra - alpha(2 * itheta, decl + 2 * itheta)))
              ,SIN(RADIANS(decl + 2 * itheta))
              ,det_sigma
              ,i_peak_avg
              ,i_peak_avg_err
              ,i_int_avg
              ,i_int_avg_err
          FROM catalogedsources
         WHERE cat_id = 5
      ;
    END IF;
    IF ibgfield = 3 THEN
      SET ods_id = insertDataset('wenss-nvss background fields N');
      SET oimageid_13 = insertBackgroundImage(ods_id,1,13,1,325000000,NOW(),'325MHz WENSS BG Field N');
      SET oimageid_14 = insertBackgroundImage(ods_id,1,14,1,352000000,NOW(),'352MHz WENSS BG Field N');
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
        ,i_peak
        ,i_peak_err
        ,i_int
        ,i_int_err
        )
        SELECT CASE WHEN band = 13 
                    THEN oimageid_13
                    ELSE oimageid_14
               END 
              ,CAST(FLOOR((decl + 2 * itheta)/izoneheight) AS INTEGER)
              ,ra 
              ,decl + 2 * itheta
              ,ra_err
              ,decl_err
              ,COS(RADIANS(decl + 2 * itheta)) * COS(RADIANS(ra))
              ,COS(RADIANS(decl + 2 * itheta)) * SIN(RADIANS(ra))
              ,SIN(RADIANS(decl + 2 * itheta))
              ,det_sigma
              ,i_peak_avg
              ,i_peak_avg_err
              ,i_int_avg
              ,i_int_avg_err
          FROM catalogedsources
         WHERE cat_id = 5
      ;
    END IF;
    IF ibgfield = 4 THEN
      SET ods_id = insertDataset('wenss-nvss background fields NE');
      SET oimageid_13 = insertBackgroundImage(ods_id,1,13,1,325000000,NOW(),'325MHz WENSS BG Field NE');
      SET oimageid_14 = insertBackgroundImage(ods_id,1,14,1,352000000,NOW(),'352MHz WENSS BG Field NE');
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
        ,i_peak
        ,i_peak_err
        ,i_int
        ,i_int_err
        )
        SELECT CASE WHEN band = 13 
                    THEN oimageid_13
                    ELSE oimageid_14
               END 
              ,CAST(FLOOR((decl + 2 * itheta)/izoneheight) AS INTEGER)
              ,ra + alpha(2 * itheta, decl + 2 * itheta)
              ,decl + 2 * itheta
              ,ra_err
              ,decl_err
              ,COS(RADIANS(decl + 2 * itheta)) * COS(RADIANS(ra + alpha(2 * itheta, decl + 2 * itheta)))
              ,COS(RADIANS(decl + 2 * itheta)) * SIN(RADIANS(ra + alpha(2 * itheta, decl + 2 * itheta)))
              ,SIN(RADIANS(decl + 2 * itheta))
              ,det_sigma
              ,i_peak_avg
              ,i_peak_avg_err
              ,i_int_avg
              ,i_int_avg_err
          FROM catalogedsources
         WHERE cat_id = 5
      ;
    END IF;
    IF ibgfield = 5 THEN
      SET ods_id = insertDataset('wenss-nvss background fields E');
      SET oimageid_13 = insertBackgroundImage(ods_id,1,13,1,325000000,NOW(),'325MHz WENSS BG Field E');
      SET oimageid_14 = insertBackgroundImage(ods_id,1,14,1,352000000,NOW(),'352MHz WENSS BG Field E');
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
        ,i_peak
        ,i_peak_err
        ,i_int
        ,i_int_err
        )
        SELECT CASE WHEN band = 13 
                    THEN oimageid_13
                    ELSE oimageid_14
               END 
              ,CAST(FLOOR(decl/izoneheight) AS INTEGER)
              ,ra + alpha(2 * itheta, decl)
              ,decl
              ,ra_err
              ,decl_err
              ,COS(RADIANS(decl)) * COS(RADIANS(ra + alpha(2 * itheta, decl)))
              ,COS(RADIANS(decl)) * SIN(RADIANS(ra + alpha(2 * itheta, decl)))
              ,SIN(RADIANS(decl))
              ,det_sigma
              ,i_peak_avg
              ,i_peak_avg_err
              ,i_int_avg
              ,i_int_avg_err
          FROM catalogedsources
         WHERE cat_id = 5
      ;
    END IF;
    IF ibgfield = 6 THEN
      SET ods_id = insertDataset('wenss-nvss background fields SE');
      SET oimageid_13 = insertBackgroundImage(ods_id,1,13,1,325000000,NOW(),'325MHz WENSS BG Field SE');
      SET oimageid_14 = insertBackgroundImage(ods_id,1,14,1,352000000,NOW(),'352MHz WENSS BG Field SE');
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
        ,i_peak
        ,i_peak_err
        ,i_int
        ,i_int_err
        )
        SELECT CASE WHEN band = 13 
                    THEN oimageid_13
                    ELSE oimageid_14
               END 
              ,CAST(FLOOR((decl - 2 * itheta)/izoneheight) AS INTEGER)
              ,ra + alpha(2 * itheta, decl - 2 * itheta)
              ,decl - 2 * itheta
              ,ra_err
              ,decl_err
              ,COS(RADIANS(decl - 2 * itheta)) * COS(RADIANS(ra + alpha(2 * itheta, decl - 2 * itheta)))
              ,COS(RADIANS(decl - 2 * itheta)) * SIN(RADIANS(ra + alpha(2 * itheta, decl - 2 * itheta)))
              ,SIN(RADIANS(decl - 2 * itheta))
              ,det_sigma
              ,i_peak_avg
              ,i_peak_avg_err
              ,i_int_avg
              ,i_int_avg_err
          FROM catalogedsources
         WHERE cat_id = 5
      ;
    END IF;
    IF ibgfield = 7 THEN
      SET ods_id = insertDataset('wenss-nvss background fields S');
      SET oimageid_13 = insertBackgroundImage(ods_id,1,13,1,325000000,NOW(),'325MHz WENSS BG Field S');
      SET oimageid_14 = insertBackgroundImage(ods_id,1,14,1,352000000,NOW(),'352MHz WENSS BG Field S');
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
        ,i_peak
        ,i_peak_err
        ,i_int
        ,i_int_err
        )
        SELECT CASE WHEN band = 13 
                    THEN oimageid_13
                    ELSE oimageid_14
               END 
              ,CAST(FLOOR((decl - 2 * itheta)/izoneheight) AS INTEGER)
              ,ra 
              ,decl - 2 * itheta
              ,ra_err
              ,decl_err
              ,COS(RADIANS(decl - 2 * itheta)) * COS(RADIANS(ra))
              ,COS(RADIANS(decl - 2 * itheta)) * SIN(RADIANS(ra))
              ,SIN(RADIANS(decl - 2 * itheta))
              ,det_sigma
              ,i_peak_avg
              ,i_peak_avg_err
              ,i_int_avg
              ,i_int_avg_err
          FROM catalogedsources
         WHERE cat_id = 5
      ;
    END IF;
    IF ibgfield = 8 THEN
      SET ods_id = insertDataset('wenss-nvss background fields SW');
      SET oimageid_13 = insertBackgroundImage(ods_id,1,13,1,325000000,NOW(),'325MHz WENSS BG Field SW');
      SET oimageid_14 = insertBackgroundImage(ods_id,1,14,1,352000000,NOW(),'352MHz WENSS BG Field SW');
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
        ,i_peak
        ,i_peak_err
        ,i_int
        ,i_int_err
        )
        SELECT CASE WHEN band = 13 
                    THEN oimageid_13
                    ELSE oimageid_14
               END 
              ,CAST(FLOOR((decl - 2 * itheta)/izoneheight) AS INTEGER)
              ,ra - alpha(2 * itheta, decl - 2 * itheta)
              ,decl - 2 * itheta
              ,ra_err
              ,decl_err
              ,COS(RADIANS(decl - 2 * itheta)) * COS(RADIANS(ra - alpha(2 * itheta, decl - 2 * itheta)))
              ,COS(RADIANS(decl - 2 * itheta)) * SIN(RADIANS(ra - alpha(2 * itheta, decl - 2 * itheta)))
              ,SIN(RADIANS(decl - 2 * itheta))
              ,det_sigma
              ,i_peak_avg
              ,i_peak_avg_err
              ,i_int_avg
              ,i_int_avg_err
          FROM catalogedsources
         WHERE cat_id = 5
      ;
    END IF;
    SET ibgfield = ibgfield + 1;
  END WHILE;

END;
