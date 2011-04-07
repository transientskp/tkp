DROP FUNCTION IF EXISTS insertImage;

DELIMITER //

/**
 * This function inserts a row in the image table,
 * and returns the value of the id under which it is known from now on.
 * If under the ds_id already an image exists the seq_nr will be incremented,
 * if not it will be initialised to 1.
 *
 * Note I: To be able to create a function that modifies data 
 * (by insertion) we have to set the global bin log var:
 * mysql> SET GLOBAL log_bin_trust_function_creators = 1;
 *
 * Note II: The params in comment should be specified soon.
 * This means this function inserts deafult values so long.
 *
 */
CREATE FUNCTION insertImage(ids_id INT
                           /*,itau INT
                           ,iband INT
                           ,itau_time DOUBLE
                           ,ifreq_eff DOUBLE*/
                           ,itaustart_ts TIMESTAMP
                           ,iurl VARCHAR(120)
                           ) RETURNS INT
MODIFIES SQL DATA
BEGIN

  DECLARE iseq_nr INT;

  DECLARE itau INT DEFAULT 1;
  DECLARE iband INT DEFAULT 1;
  DECLARE itau_time DOUBLE DEFAULT 1.001;
  DECLARE ifreq_eff DOUBLE DEFAULT 30100000;

  /* TODO:
   * make sure the right timestamp gets inserted 
   * it is a bigint
   */

  SELECT IFNULL(MAX(seq_nr), 0)
    INTO iseq_nr
    FROM images
   WHERE ds_id = ids_id
     AND tau = itau
     AND band = iband
  ;

  SET iseq_nr = iseq_nr + 1;

  INSERT INTO images
    (ds_id
    ,tau
    ,band
    ,seq_nr
    ,tau_time
    ,freq_eff
    ,taustart_ts
    ,url
    ) 
  VALUES
    (ids_id
    ,itau
    ,iband
    ,iseq_nr
    ,itau_time
    ,ifreq_eff
    ,itaustart_ts
    ,iurl
    )
  ;

  RETURN LAST_INSERT_ID();

END;
//

DELIMITER ;
