USE pipeline_test;

DROP PROCEDURE IF EXISTS test_load_catdata;

DELIMITER //

CREATE PROCEDURE test_load_catdata()
BEGIN
  DECLARE icat_id INT DEFAULT 1;
  DECLARE iorig_catsrcid INT;
  DECLARE iband INT;
  DECLARE ifreq_eff double precision;

  DECLARE nsrc INT;
  DECLARE ira0 double precision DEFAULT 20;
  DECLARE idecl0 double precision DEFAULT 20;
  DECLARE ira_err0 double precision DEFAULT 0.05;
  DECLARE idecl_err0 double precision DEFAULT 0.05;
  DECLARE ira double precision;
  DECLARE idecl double precision;
  DECLARE ira_err double precision;
  DECLARE idecl_err double precision;
  DECLARE ix double precision;
  DECLARE iy double precision;
  DECLARE iz double precision;
  DECLARE ixy double precision;
  DECLARE izoneheight double precision DEFAULT 1;

  DELETE FROM associatedcatsources;
  DELETE FROM cataloguedsources;
  DELETE FROM catalogues;
  DELETE FROM frequencybands WHERE freqbandid IN (11,12,13,14);

  INSERT INTO catalogues (catid, catname, fullname) VALUES (1, 'WENSS', 'Test Catalogue 1');
  INSERT INTO catalogues (catid, catname, fullname) VALUES (2, 'VLSS', 'Test Catalogue 2');
  INSERT INTO catalogues (catid, catname, fullname) VALUES (3, 'NVSS', 'Test Catalogue 3');
  INSERT INTO catalogues (catid, catname, fullname) VALUES (4, '8C', 'Test Catalogue 4');

  INSERT INTO frequencybands (freqbandid,freq_low,freq_high) VALUES (11, 324000000,326000000);
  INSERT INTO frequencybands (freqbandid,freq_low,freq_high) VALUES (12, 73000000,75000000);
  INSERT INTO frequencybands (freqbandid,freq_low,freq_high) VALUES (13, 1399000000,1401000000);
  INSERT INTO frequencybands (freqbandid,freq_low,freq_high) VALUES (14, 37000000,39000000);


  WHILE (icat_id < 5) DO
    IF icat_id = 1 THEN 
      SET ifreq_eff = 325000000;
    END IF;
    IF icat_id = 2 THEN 
      SET ifreq_eff = 74000000;
    END IF;
    IF icat_id = 3 THEN 
      SET ifreq_eff = 1400000000;
    END IF;
    IF icat_id = 4 THEN 
      SET ifreq_eff = 38000000;
    END IF;
    /* Yes, this is tricky..., but quick*/
    SET iband = icat_id + 10;
    SET nsrc = 1;
    WHILE (nsrc < 5) DO
      SET iorig_catsrcid = nsrc;
      SET ira = ira0 + nsrc * 10;
      SET idecl = idecl0 - nsrc * 5;
      SET ira_err = ira_err0 * icat_id;
      SET idecl_err = idecl_err0 * icat_id;
      SET ixy = COS(RADIANS(idecl));
      SET ix = ixy * COS(RADIANS(ira));
      SET iy = ixy * SIN(RADIANS(ira));
      SET iz = SIN(RADIANS(idecl));
      INSERT INTO cataloguedsources
        (cat_id
        ,orig_catsrcid
        ,band
        ,freq_eff
        ,zone
        ,ra
        ,decl
        ,ra_err
        ,decl_err
        ,x
        ,y
        ,z
        ) 
      VALUES
        (icat_id
        ,iorig_catsrcid
        ,iband
        ,ifreq_eff
        ,FLOOR(idecl/izoneheight)
        ,ira
        ,idecl
        ,ira_err
        ,idecl_err
        ,ix
        ,iy
        ,iz
        ) 
      ;
      SET nsrc = nsrc + 1;
    END WHILE;
    SET icat_id = icat_id + 1;
    
  END WHILE;

END;
//

DELIMITER ;

