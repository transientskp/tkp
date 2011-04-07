DROP PROCEDURE IF EXISTS SourceInRegion;

DELIMITER //

/**
 * This procedure creates a FITS regions file
 * INPUT:
 *  iimage_id   : the image_id that was processed by the TKP pipeline
 *  idirname    : the name of the directory in which the region file will
 *                be written [abs.path name with traing "/"]
 *  icolor      : the color in which the circles will be represented
 * OUTPUT       :
 *  oregion_file: the region file name 
 *                [YYYYMMDDHHMMSS.iimage_id.reg]
 *  orregion_sql: the SQL that is being executed
 *                to generate the region file
 *  
 */
CREATE PROCEDURE SourceInRegion(IN ixtrsrcid INT
                               ,IN idirname VARCHAR(128)
                               ,IN icolor VARCHAR(16)
                               ,OUT oregion_file VARCHAR(64)
                               ,OUT oregion_sql VARCHAR(1024)
                               ) 

BEGIN
  DECLARE image_url VARCHAR(120);

  SELECT url
    INTO image_url
    FROM images
        ,extractedsources
   WHERE imageid = iimage_id
     AND xtrsrcid = ixtrsrcid
  ;

  SET oregion_file = CONCAT(idirname, DATE_FORMAT(NOW(), '%Y%m%d-%H%i'), 'src', ixtrsrcid, ".reg");
  
  SET oregion_sql = CONCAT("SELECT '# Region file format: DS9 version 4.0'"
                          ," UNION"
                          ," SELECT \'# Filename: "
                          ,image_url
                          ,"\'"
                          ," UNION"
                          ," SELECT 'global color=green font=\"helvetica 10 normal\" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source'"
                          ," UNION"
                          ," SELECT 'fk5'"
                          ," UNION"
                          ," SELECT CONCAT(\'box(\', ra, \',\', decl, \',\', ra_err/1800, \',\', decl_err/1800, \') #color="
                          ,icolor
                          ,", text={\', xtrsrcid,\'}\')"
                          ," INTO OUTFILE "
                          ,"'"
                          ,oregion_file
                          ,"'"
                          ," FIELDS TERMINATED BY \';\'"
                          ," LINES TERMINATED BY \'\\n\'"
                          ," FROM extractedsources"
                          ," WHERE xtrsrcid = "
                          ,ixtrsrcid
                          );

  SET @region_sql = oregion_sql;

  PREPARE stmt1 FROM @region_sql;
  EXECUTE stmt1;
  DEALLOCATE PREPARE stmt1;

END;
//

DELIMITER ;
