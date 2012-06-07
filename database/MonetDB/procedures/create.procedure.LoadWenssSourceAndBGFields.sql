--DROP PROCEDURE LoadWenssSourceAndBGFields;
/*+-------------------------------------------------------------------+
 *| This procedure loads the WENSS single point (src_type = 'S')      |
 *| sources into the extractedsources table.                          |
 *| In this way they can be treated as if they were detected in a     |
 *| regular way, and processed in the TKP pipeline.                   |
 *| WENSS sources loaded with their original positions are in the     |
 *| so-called Source Field, whereas WENSS sources generated with an   |
 *| positional offset (W,NW,N,NE,E,SE,S,SW) are in the eight          |
 *| Background Fields.                                                |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *| Bart Scheers, 2010-06-04                                          |
 *+-------------------------------------------------------------------+
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */
CREATE PROCEDURE LoadWenssSourceAndBGFields()
BEGIN

  DECLARE ods_id, oimageid_low, oimageid_high INT;
  DECLARE ibgfield INT;
  DECLARE izoneheight, itheta DOUBLE;
  
  SET ods_id = insertDataset('wenss-nvss source field');
  /* Important note:
   * We assume that the 325 and 352 MHz freqs of WENSS belong to the
   * same frequency band in frequencybands.
   * getBand(325000000) = getBand(352000000) in insertImage()
   */
  SET oimageid_low = insertImage(ods_id, 325000000, 10000000, NOW(), '325MHz WENSS Src Field');
  SET oimageid_high = insertImage(ods_id, 352000000, 10000000, NOW(), '352MHz WENSS Src Field');
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
    SELECT CASE WHEN freq_eff < 330000000 
                THEN oimageid_low
                ELSE oimageid_high
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
       AND src_type = 'S'
       AND decl BETWEEN 44 AND 64
  ;
  
  SET izoneheight = 1;
  SET itheta = 0.025;
  SET ibgfield = 1;
  
  WHILE ibgfield < 9 DO
    IF ibgfield = 1 THEN
      SET ods_id = insertDataset('wenss-nvss background fields W');
      SET oimageid_low = insertImage(ods_id, 325000000, 10000000, NOW(), '325MHz WENSS BG-W Field');
      SET oimageid_high = insertImage(ods_id, 352000000, 10000000, NOW(), '352MHz WENSS BG-W Field');
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
        SELECT CASE WHEN freq_eff < 330000000 
                    THEN oimageid_low
                    ELSE oimageid_high
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
           AND src_type = 'S'
           AND decl BETWEEN 44 AND 64
      ;
    END IF;
    IF ibgfield = 2 THEN
      SET ods_id = insertDataset('wenss-nvss background fields NW');
      SET oimageid_low = insertImage(ods_id, 325000000, 10000000, NOW(), '325MHz WENSS BG-NW Field');
      SET oimageid_high = insertImage(ods_id, 352000000, 10000000, NOW(), '352MHz WENSS BG-NW Field');
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
        SELECT CASE WHEN freq_eff < 330000000 
                    THEN oimageid_low
                    ELSE oimageid_high
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
           AND src_type = 'S'
           AND decl BETWEEN 44 AND 64
      ;
    END IF;
    IF ibgfield = 3 THEN
      SET ods_id = insertDataset('wenss-nvss background fields N');
      SET oimageid_low = insertImage(ods_id, 325000000, 10000000, NOW(), '325MHz WENSS BG-N Field');
      SET oimageid_high = insertImage(ods_id, 352000000, 10000000, NOW(), '352MHz WENSS BG-N Field');
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
        SELECT CASE WHEN freq_eff < 330000000 
                    THEN oimageid_low
                    ELSE oimageid_high
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
           AND src_type = 'S'
           AND decl BETWEEN 44 AND 64
      ;
    END IF;
    IF ibgfield = 4 THEN
      SET ods_id = insertDataset('wenss-nvss background fields NE');
      SET oimageid_low = insertImage(ods_id, 325000000, 10000000, NOW(), '325MHz WENSS BG-NE Field');
      SET oimageid_high = insertImage(ods_id, 352000000, 10000000, NOW(), '352MHz WENSS BG-NE Field');
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
        SELECT CASE WHEN freq_eff < 330000000 
                    THEN oimageid_low
                    ELSE oimageid_high
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
           AND src_type = 'S'
           AND decl BETWEEN 44 AND 64
      ;
    END IF;
    IF ibgfield = 5 THEN
      SET ods_id = insertDataset('wenss-nvss background fields E');
      SET oimageid_low = insertImage(ods_id, 325000000, 10000000, NOW(), '325MHz WENSS BG-E Field');
      SET oimageid_high = insertImage(ods_id, 352000000, 10000000, NOW(), '352MHz WENSS BG-E Field');
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
        SELECT CASE WHEN freq_eff < 330000000 
                    THEN oimageid_low
                    ELSE oimageid_high
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
           AND src_type = 'S'
           AND decl BETWEEN 44 AND 64
      ;
    END IF;
    IF ibgfield = 6 THEN
      SET ods_id = insertDataset('wenss-nvss background fields SE');
      SET oimageid_low = insertImage(ods_id, 325000000, 10000000, NOW(), '325MHz WENSS BG-SE Field');
      SET oimageid_high = insertImage(ods_id, 352000000, 10000000, NOW(), '352MHz WENSS BG-SE Field');
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
        SELECT CASE WHEN freq_eff < 330000000 
                    THEN oimageid_low
                    ELSE oimageid_high
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
           AND src_type = 'S'
           AND decl BETWEEN 44 AND 64
      ;
    END IF;
    IF ibgfield = 7 THEN
      SET ods_id = insertDataset('wenss-nvss background fields S');
      SET oimageid_low = insertImage(ods_id, 325000000, 10000000, NOW(), '325MHz WENSS BG-S Field');
      SET oimageid_high = insertImage(ods_id, 352000000, 10000000, NOW(), '352MHz WENSS BG-S Field');
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
        SELECT CASE WHEN freq_eff < 330000000 
                    THEN oimageid_low
                    ELSE oimageid_high
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
           AND src_type = 'S'
           AND decl BETWEEN 44 AND 64
      ;
    END IF;
    IF ibgfield = 8 THEN
      SET ods_id = insertDataset('wenss-nvss background fields SW');
      SET oimageid_low = insertImage(ods_id, 325000000, 10000000, NOW(), '325MHz WENSS BG-SW Field');
      SET oimageid_high = insertImage(ods_id, 352000000, 10000000, NOW(), '352MHz WENSS BG-SW Field');
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
        SELECT CASE WHEN freq_eff < 330000000 
                    THEN oimageid_low
                    ELSE oimageid_high
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
           AND src_type = 'S'
           AND decl BETWEEN 44 AND 64
      ;
    END IF;
    SET ibgfield = ibgfield + 1;
  END WHILE;

END;
