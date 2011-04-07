SET SCHEMA "pipeline";

CREATE PROCEDURE AssociateSource(itau INT
                                ,iband INT
                                ,iseq_nr INT
                                ,ids_id INT
                                ,ifreq_eff DOUBLE
                                ,ira DOUBLE
                                ,idecl DOUBLE
                                ,ira_err DOUBLE
                                ,idecl_err DOUBLE
                                ,iI_peak DOUBLE
                                ,iI_peak_err DOUBLE
                                )
BEGIN

  DECLARE ix DOUBLE;
  DECLARE iy DOUBLE;
  DECLARE iz DOUBLE;
  DECLARE ixy DOUBLE;

  DECLARE izoneheight DOUBLE;
  DECLARE itheta DOUBLE;
  DECLARE ialpha DOUBLE;

  DECLARE iassoc_xtrsrcid INT;
  DECLARE nassoc_xtrsrcid INT;
  DECLARE iassoc_catsrcid INT;
  DECLARE nassoc_catsrcid INT;
  DECLARE iclass_id INT;

  SET ixy = COS(RADIANS(idecl));
  SET ix = ixy * COS(RADIANS(ira));
  SET iy = ixy * SIN(RADIANS(ira));
  SET iz = SIN(RADIANS(idecl));

  SELECT zoneheight INTO izoneheight FROM zoneheight;
  SELECT CASE WHEN ira_err > idecl_err THEN ira_err ELSE idecl_err END INTO itheta;
  SET ialpha = alpha(itheta, idecl);

    SELECT catsrcid
          ,COUNT(catsrcid)
      INTO iassoc_catsrcid
          ,nassoc_catsrcid
      FROM cataloguesources
    ;

END;

