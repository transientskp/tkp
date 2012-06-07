--DROP PROCEDURE SourcesInRegion;

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
CREATE PROCEDURE SourcesInRegion(iimage_id INT
                                ,idirname VARCHAR(128)
                                ,icolor VARCHAR(16)
                                /*,OUT oregion_file VARCHAR(64)
                                ,OUT oregion_sql VARCHAR(1024)*/
                                ) 

BEGIN
  DECLARE image_url VARCHAR(120);
  DECLARE oregion_file VARCHAR(64);

  SELECT url
    INTO image_url
    FROM images
   WHERE imageid = iimage_id
  ;

  SET oregion_file = CONCAT(idirname, DATE_FORMAT(NOW(), '%Y%m%d-%H%i'), 'xtr', iimage_id, ".reg");
  
  COPY 
  SELECT t.line
    FROM (SELECT '# Region file format: DS9 version 4.0' AS line
           UNION
          SELECT CONCAT('# Filename: ', image_url) AS line
           UNION
          SELECT 'global color=green font=\"helvetica 10 normal\" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source' AS line
           UNION
          SELECT 'fk5' AS line
           UNION
          SELECT CONCAT('box(', 
                 CONCAT(ra, CONCAT(',', 
                 CONCAT(decl, CONCAT(',', 
                 CONCAT(ra_err/1800, CONCAT(',', 
                 CONCAT(decl_err/1800, CONCAT(') #color=', 
                 CONCAT(icolor, CONCAT(' text={', 
                 CONCAT(xtrsrcid, '}')))))))))))) AS line
            FROM extractedsources
           WHERE image_id = iimage_id
         ) t
    INTO oregionfile
  DELIMITERS ';'
            ,'\n'
            ,''
  ;

END;

