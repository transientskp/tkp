DROP PROCEDURE IF EXISTS InsertSrc;

DELIMITER //

/*+------------------------------------------------------------------+
 *| This procedure                                                   |
 *| (1) adds an extracted source to the extractedsources table.      |
 *| (2) tries to associate the source with sources previously        |
 *|     detected for this data set (same ds_id)                      |
 *| (3) also tries to associate the source with cataloged sources    |
 *| (4) If found, an association will be added to the                |
 *|     associatedsources table.                                     |
 *+------------------------------------------------------------------+
 *| Input params:                                                    |
 *|   iimage_id  : the image_id from which this source was extracted |
 *|   ira        : RA of extracted source (in degrees)               |
 *|   idecl      : dec of extracted source (in degrees)              |
 *|   ira_err    : 1 sigma error on RA (in degrees)                  |
 *|   idecl_err  : 1 sigma error on dec (in degrees)                 |
 *|   iI_peak    : Peak flux of extracted source (in Jansky)         |
 *|   iI_peak_err: Error on peak flux of extracted source (in Jansky)|
 *|   iI_int     : Integrated flux of extracted source (in Jansky)   |
 *|   iI_int_err : Error on int. flux of extracted source (in Jansky)|
 *|   idet_sigma : The detection level of the extracted source       |
 *|                (in sigma)                                        |
 *+------------------------------------------------------------------+
 *| Used variables:                                                  |
 *| itheta: this is the radius (in degrees) of the circular area     |
 *|         centered at (ra,decl) of the current (input) source. All |
 *|         sources found within this area will be inspected for     |
 *|         association.                                             |
 *|         The difficult part is how to determine what is the best  |
 *|         value for itheta. Will it depend on the source density,  |
 *|         which depends on int.time, freq, or is it sufficient to  |
 *|         simply set it to a default value of f.ex. 1 (degree)?    |
 *|         For now, we default it to 1 (degree).                    |
 *|                                                                  |
 *+------------------------------------------------------------------+
 *| TODO: Also insert margin records                                 |
 *+------------------------------------------------------------------+
 *|                       Bart Scheers                               |
 *|                        2009-02-18                                |
 *+------------------------------------------------------------------+
 *| 2009-02-18                                                       |
 *| Based on AssociateSource() from create.database.sql              |
 *+------------------------------------------------------------------+
 *| Open Questions:                                                  |
 *|                                                                  |
 *| Sanity check on transaction isolation level                      |
 *| my.cnf: set innodb_lock_wait_timeoutation <> 50sec default.      |
 *+------------------------------------------------------------------+
 */
CREATE PROCEDURE InsertSrc(IN iimage_id INT
                         ,IN ira DOUBLE
                         ,IN idecl DOUBLE
                         ,IN ira_err DOUBLE
                         ,IN idecl_err DOUBLE
                         ,IN iI_peak DOUBLE
                         ,IN iI_peak_err DOUBLE
                         ,IN iI_int DOUBLE
                         ,IN iI_int_err DOUBLE
                         ,IN idet_sigma DOUBLE
                         )
BEGIN

  DECLARE izone INT;
  DECLARE ix DOUBLE;
  DECLARE iy DOUBLE;
  DECLARE iz DOUBLE;
  DECLARE ixy DOUBLE;

  DECLARE izoneheight DOUBLE;
  DECLARE itheta DOUBLE DEFAULT 1;
  DECLARE sin_itheta DOUBLE;
  DECLARE ialpha DOUBLE;

  DECLARE ixtrsrcid INT DEFAULT NULL;
  DECLARE iassoc_xtrsrcid INT DEFAULT NULL;
  DECLARE nassoc_xtrsrcid INT DEFAULT 0;
  DECLARE iassoc_catsrcid INT DEFAULT NULL;
  DECLARE nassoc_catsrcid INT DEFAULT 0;
  DECLARE ifirst_xtrsrcid INT;

  DECLARE found BOOLEAN DEFAULT FALSE;

  SELECT zoneheight
    INTO izoneheight
    FROM zoneheight
  ;

  SET izone = FLOOR(idecl/izoneheight);
  SET ixy = COS(RADIANS(idecl));
  SET ix = ixy * COS(RADIANS(ira));
  SET iy = ixy * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

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
    ,(ira_err * 3600) + 1.5
    ,(idecl_err * 3600) + 1.5
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
 
END;
//

DELIMITER ;

