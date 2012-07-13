--DROP FUNCTION insertImage;

/**
 * This function inserts a row in the image table,
 * and returns the value of the id under which it is known.
 * If the dataset name (dsinname) already exists, a new row is added
 * and the rerun value is incremented by 1. If not, it is set
 * to its default value 0.
 *
 * Note I: To be able to create a function that modifies data 
 * (by insertion) we have to set the global bin log var:
 * mysql> SET GLOBAL log_bin_trust_function_creators = 1;
 *
 * Note II: The params in comment should be specified soon.
 * This means this function inserts deafult values so long.
 *
 */
CREATE FUNCTION insertImage(idataset INT
                           /*,itau INT
                           ,itau_time DOUBLE*/
                           ,ifreq_eff DOUBLE
                           ,ifreq_bw DOUBLE
                           ,itaustart_ts TIMESTAMP
                           ,iurl VARCHAR(1024)
                           /*,beam_maj DOUBLE
                           ,beam_min DOUBLE
                           ,beam_pa DOUBLE*/
                           ) RETURNS INT
BEGIN

  DECLARE iimageid INT;
  DECLARE oimageid INT;
  DECLARE iband SMALLINT;
  DECLARE itau INT;
  DECLARE itau_time DOUBLE;

  SET iband = getBand(ifreq_eff);
  
  SELECT NEXT VALUE FOR seq_image INTO iimageid;

  INSERT INTO image
    (id
    ,dataset
    /*,tau*/
    ,band
    /*,tau_time*/
    ,freq_eff
    ,freq_bw
    ,taustart_ts
    ,url
    /*,beam_semimaj
    ,beam_semimin
    ,beam_pa*/
    ) 
  VALUES
    (iimageid
    ,idataset
    /*,itau*/
    ,iband
    /*,itau_time*/
    ,ifreq_eff
    ,ifreq_bw
    ,itaustart_ts
    ,iurl
    /*,beam_semimaj
    ,beam_semimin
    ,beam_pa*/
    )
  ;

  SET oimageid = iimageid;
  RETURN oimageid;

END;
