USE pipeline;

/**
 * Because a stored procedure can not contain LOAD statements,
 * we have to create it here.
 * To test the source extraction algorithms we created fits files
 * in which sources where inserted with true position and flux.
 * These generated fits files all have a source in the middle, 
 * but a different (random) flux.
 * Every fits file gets his own cat_id 
 * (see MySQL.pipeline.procedure.CreateTrueCatalogues.sql).
 * AIPS's task SAD was run on the files. The highest peak flux source
 * was put in the list.
 * We load these sources first in the catalogues table, after which 
 * we run a procedure to put them in extractedsources and 
 * associate them to the "True Catalog".
 */
LOAD DATA INFILE 'SAD_370_sources.txt'
INTO TABLE cataloguesources 
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
  (@orig_catsrcid
  ,@i_peak_avg
  ,@i_peak_avg_err
  ,@i_int_avg
  ,@i_int_avg_err
  ,@ra
  ,@decl
  ,@ra_err
  ,@decl_err
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ,@dummy
  ) 
SET 
   orig_catsrcid = @orig_catsrcid
  ,cat_id = 4
  ,band = 1
  ,zone = FLOOR(@decl)
  ,freq_eff = 330000000
  ,ra = @ra
  ,decl = @decl
  ,ra_err = @ra_err
  ,decl_err = @decl_err
  ,x = COS(RADIANS(@decl)) * COS(RADIANS(@ra))
  ,y = COS(RADIANS(@decl)) * SIN(RADIANS(@ra))
  ,z = SIN(RADIANS(@decl))
  ,i_peak_avg = @i_peak_avg
  ,i_peak_avg_err = @i_peak_avg_err
  ,i_int_avg = @i_int_avg
  ,i_int_avg_err = @i_int_avg_err
;

DROP PROCEDURE IF EXISTS SAD2FPOS0370;

DELIMITER //

CREATE PROCEDURE SAD2FPOS0370()

BEGIN

  DECLARE iseq_nr INT DEFAULT 1;
  DECLARE ifreq_eff DOUBLE;
  DECLARE ira DOUBLE;
  DECLARE idecl DOUBLE;
  DECLARE ira_err DOUBLE;
  DECLARE idecl_err DOUBLE;
  DECLARE iI_peak DOUBLE;
  DECLARE iI_peak_err DOUBLE;
  DECLARE iI_int DOUBLE;
  DECLARE iI_int_err DOUBLE;
  /* this is the ra and dec increment (deg) in wenss map WN55074 */
  DECLARE iassoc_angle DOUBLE /*DEFAULT 0.00585937*/;
  DECLARE icat_id INT;

  DECLARE done INT DEFAULT 0;
  DECLARE cur1 CURSOR FOR
    SELECT freq_eff
          ,ra
          ,decl
          ,ra_err
          ,decl_err
          ,I_peak_avg
          ,I_peak_avg_err
          ,I_int_avg
          ,I_int_avg_err
     FROM cataloguesources
    WHERE cat_id = 4;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

  OPEN cur1;

  REPEAT
    FETCH cur1
     INTO ifreq_eff
         ,ira
         ,idecl
         ,ira_err
         ,idecl_err
         ,iI_peak
         ,iI_peak_err
         ,iI_int
         ,iI_int_err
    ;
    IF NOT done THEN
      CALL AssociateSource(1
                          ,iseq_nr
                          ,26
                          ,ifreq_eff
                          ,ira
                          ,idecl
                          ,ira_err
                          ,idecl_err
                          ,iI_peak
                          ,iI_peak_err
                          ,iI_int
                          ,iI_int_err
                          ,ira_err
                          ,iseq_nr + 100
                          );
    END IF;
    iseq_nr = iseq_nr + 1;
  UNTIL done END REPEAT;

  CLOSE cur1;
END;
//

DELIMITER ;

/*+-------------------------------------------------------------------+
 *|                                                                   |
 *|                           THE END                                 |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 */

