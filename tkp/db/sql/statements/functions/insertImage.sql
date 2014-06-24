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
 * Note III: Two subroutines are called, getBand and getSkyRgn.
 * These return:
 *  - A matching band_id. Bands are always 1 MHz wide and centred on the
 *    effective frequency rounded to the nearest MHz (see #4801).
 *  - A matching skyregion_id, given the field centre and extraction radius.
 *
 */
CREATE FUNCTION insertImage(idataset INT
                           ,itau_time DOUBLE PRECISION
                           ,ifreq_eff DOUBLE PRECISION
                           ,ifreq_bw DOUBLE PRECISION
                           ,itaustart_ts TIMESTAMP
                           ,irb_smaj DOUBLE PRECISION
                           ,irb_smin DOUBLE PRECISION
                           ,irb_pa DOUBLE PRECISION
                           ,ideltax DOUBLE PRECISION
                           ,ideltay DOUBLE PRECISION
                           ,iurl VARCHAR(1024)
                           ,icentre_ra DOUBLE PRECISION
                           ,icentre_decl DOUBLE PRECISION
                           ,ixtr_radius DOUBLE PRECISION
                           ,irms_qc DOUBLE PRECISION
                           ,irms_min DOUBLE PRECISION
                           ,irms_max DOUBLE PRECISION
                           ,idetection_thresh DOUBLE PRECISION
                           ,ianalysis_thresh DOUBLE PRECISION
                           ) RETURNS INT


{% ifdb postgresql %}
AS $$
  DECLARE iimageid INT;
  DECLARE oimageid INT;
  DECLARE iband SMALLINT;
  DECLARE itau INT;
  DECLARE iskyrgn INT;

BEGIN
  iband := getBand(1e6 * FLOOR(ifreq_eff/1e6 + 0.5), 1e6);
  iskyrgn := getSkyRgn(idataset, icentre_ra, icentre_decl, ixtr_radius);

  INSERT INTO image
    (dataset
    ,band
    ,tau_time
    ,freq_eff
    ,freq_bw
    ,taustart_ts
    ,skyrgn
    ,rb_smaj
    ,rb_smin
    ,rb_pa
    ,deltax
    ,deltay
    ,url
    ,rms_qc
    ,rms_min
    ,rms_max
    ,detection_thresh
    ,analysis_thresh
    )
  VALUES
    (idataset
    ,iband
    ,itau_time
    ,ifreq_eff
    ,ifreq_bw
    ,itaustart_ts
    ,iskyrgn
    ,irb_smaj
    ,irb_smin
    ,irb_pa
    ,ideltax
    ,ideltay
    ,iurl
    ,irms_qc
    ,irms_min
    ,irms_max
    ,idetection_thresh
    ,ianalysis_thresh
    )
    RETURNING id INTO oimageid
  ;

  RETURN oimageid;

END;

$$ LANGUAGE plpgsql;
{% endifdb %}


{% ifdb monetdb %}
BEGIN

  DECLARE iimageid INT;
  DECLARE oimageid INT;
  DECLARE iband SMALLINT;
  DECLARE itau INT;
  DECLARE iskyrgn INT;

  SET iband = getBand(1e6 * FLOOR(ifreq_eff/1e6 + 0.5), 1e6);
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
    ,rb_smaj
    ,rb_smin
    ,rb_pa
    ,deltax
    ,deltay
    ,url
    ,rms_qc
    ,rms_min
    ,rms_max
    ,detection_thresh
    ,analysis_thresh
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
    ,irb_smaj
    ,irb_smin
    ,irb_pa
    ,ideltax
    ,ideltay
    ,iurl
    ,irms_qc
    ,irms_min
    ,irms_max
    ,idetection_thresh
    ,ianalysis_thresh
    )
  ;

  SET oimageid = iimageid;
  RETURN oimageid;

END;
{% endifdb %}
