--DROP FUNCTION insertImage;

/**
 * This function inserts a row in the image table,
 * and returns the value of the id under which it is known.
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
                           ,itau_time DOUBLE
                           ,ifreq_eff DOUBLE
                           ,ifreq_bw DOUBLE
                           ,itaustart_ts TIMESTAMP
                           ,ibeam_maj DOUBLE
                           ,ibeam_min DOUBLE
                           ,ibeam_pa DOUBLE
                           ,iurl VARCHAR(1024)
                           ,icentre_ra DOUBLE
                           ,icentre_decl DOUBLE
                           ,ixtr_radius DOUBLE
                           ) RETURNS INT
BEGIN

  DECLARE iimageid INT;
  DECLARE oimageid INT;
  DECLARE iband SMALLINT;
  DECLARE itau INT;
  DECLARE iskyrgn INT;

  SET iband = getBand(ifreq_eff, ifreq_bw);
  SET iskyrgn = getSkyRgn(idataset, icentre_ra, icentre_decl, ixtr_radius);
  
  SELECT NEXT VALUE FOR seq_image INTO iimageid;

  INSERT INTO image
    (id
    ,dataset
    ,band
    ,tau_time
    ,freq_eff
    ,freq_bw
    ,taustart_ts
    ,skyrgn
    ,bmaj_syn
    ,bmin_syn
    ,bpa_syn
    ,url
    ) 
  VALUES
    (iimageid
    ,idataset
    ,iband
    ,itau_time
    ,ifreq_eff
    ,ifreq_bw
    ,itaustart_ts
    ,iskyrgn
    ,ibeam_maj 
    ,ibeam_min 
    ,ibeam_pa 
    ,iurl
    )
  ;

  SET oimageid = iimageid;
  RETURN oimageid;

END;
