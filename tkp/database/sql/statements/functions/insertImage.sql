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
 *  - A matching band_id, given the freq_eff and freq_bw
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
                           ) RETURNS INT


{% ifdb postgresql %}
AS $$
{% endifdb %}

{% ifdb monetdb %}
BEGIN
{% endifdb %}

  DECLARE iimageid INT;
  DECLARE oimageid INT;
  DECLARE iband SMALLINT;
  DECLARE itau INT;
  DECLARE iskyrgn INT;

{% ifdb postgresql %}
BEGIN
  iband := getBand(ifreq_eff, ifreq_bw);
  iskyrgn := getSkyRgn(idataset, icentre_ra, icentre_decl, ixtr_radius);
{% endifdb %}

{% ifdb monetdb %}
  SET iband = getBand(ifreq_eff, ifreq_bw);
  SET iskyrgn = getSkyRgn(idataset, icentre_ra, icentre_decl, ixtr_radius);
{% endifdb %}

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
    )
  ;

  RETURN lastval();

END;

{% ifdb postgresql %}
$$ LANGUAGE plpgsql;
{% endifdb %}