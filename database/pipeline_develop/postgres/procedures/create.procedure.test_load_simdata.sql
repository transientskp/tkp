DROP PROCEDURE IF EXISTS test_load_simdata;

DELIMITER //

CREATE PROCEDURE test_load_simdata()
BEGIN

  DECLARE ifile_id INT DEFAULT 1;
  DECLARE itau INT DEFAULT 1;
  DECLARE iband INT DEFAULT 1;
  DECLARE iseq_nr INT DEFAULT 1;
  DECLARE itau_time INT DEFAULT 1;
  DECLARE ifreq_eff double precision;
  DECLARE itaustart_timestamp0 BIGINT DEFAULT 20081217135700000;
  DECLARE itaustart_timestamp BIGINT;
  DECLARE it INT DEFAULT 1;
  DECLARE itimestamp INT;

  DECLARE isrc INT DEFAULT 1;
  DECLARE nsrc INT DEFAULT 1;
  DECLARE ira0 double precision DEFAULT 20;
  DECLARE idecl0 double precision DEFAULT 20;
  DECLARE ira_err0 double precision DEFAULT 0.05;
  DECLARE idecl_err0 double precision DEFAULT 0.05;
  DECLARE ira double precision;
  DECLARE idecl double precision;
  DECLARE ira_err double precision;
  DECLARE idecl_err double precision;
  DECLARE idet_sigma double precision;
  DECLARE ix double precision;
  DECLARE iy double precision;
  DECLARE iz double precision;
  DECLARE ixy double precision;
  DECLARE izoneheight double precision DEFAULT 1;
  DECLARE iI_peak double precision;
  DECLARE iI_peak_err double precision;
  DECLARE iI_int double precision;
  DECLARE iI_int_err double precision;

  DELETE FROM zoneheight;
  
  DELETE FROM associatedsources;
  DELETE FROM extractedsources;
  DELETE FROM files;
  DELETE FROM frequencybands WHERE freqbandid IN (1,2,3);
  DELETE FROM datasets;

  INSERT INTO zoneheight VALUES (1);
  INSERT INTO datasets (dsid,dstype,taustart_timestamp,dsinname) VALUES (1,1,itaustart_timestamp0,'assoc_test');

  INSERT INTO frequencybands (freqbandid,freq_low,freq_high) VALUES (1, 28000000,32000000);
  INSERT INTO frequencybands (freqbandid,freq_low,freq_high) VALUES (2, 43000000,47000000);
  INSERT INTO frequencybands (freqbandid,freq_low,freq_high) VALUES (3, 68000000,72000000);

  WHILE (itau < 4) DO
    SET iband = 1;
    WHILE (iband < 4) DO
      SET iseq_nr = 1;
      IF itau = 3 THEN 
        SET itau_time = 5;
      ELSE 
        SET itau_time = itau;
      END IF;
      WHILE (itau_time * iseq_nr < 16) DO
        SET itimestamp = itau_time * iseq_nr * 1000;
        SET itaustart_timestamp = itaustart_timestamp0 + itimestamp;
        IF (iband = 1) THEN 
          SET ifreq_eff = 30000000;
        END IF; 
        IF (iband = 2) THEN 
          SET ifreq_eff = 45000000;
        END IF;
        IF (iband = 3) THEN 
          SET ifreq_eff = 70000000;
        END IF;
        INSERT INTO files 
          (fileid
          ,ds_id
          ,tau
          ,band
          ,seq_nr
          ,tau_time
          ,freq_eff
          ,taustart_timestamp) 
        VALUES 
          (ifile_id
          ,1
          ,itau
          ,iband
          ,iseq_nr
          ,itau_time
          ,ifreq_eff
          ,itaustart_timestamp
          )
        ;
        /* And now we fill the extractedsources table
           with 3 sources per file */
        SET nsrc = 1;
        WHILE (nsrc < 4) DO
          SET ira = ira0 + nsrc * 10;
          SET idecl = idecl0 - nsrc * 5;
          SET ira_err = ira_err0 * LOG10(1+ifile_id);
          SET idecl_err = idecl_err0 * LOG10(1+ifile_id);
          SET ixy = COS(RADIANS(idecl));
          SET ix = ixy * COS(RADIANS(ira));
          SET iy = ixy * SIN(RADIANS(ira));
          SET iz = SIN(RADIANS(idecl));
          SET iI_peak = 0.1;
          SET iI_peak_err = 0.01;
          SET iI_int = 0.2;
          SET iI_int_err = 0.01;
          INSERT INTO extractedsources
            (xtrsrcid
            ,file_id
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
            (isrc
            ,ifile_id
            ,FLOOR(idecl/izoneheight)
            ,ira
            ,idecl
            ,ira_err
            ,idecl_err
            ,ix
            ,iy
            ,iz
            ,2
            ,iI_peak
            ,iI_peak_err
            ,iI_int
            ,iI_int_err
            )
          ;
          SET isrc = isrc + 1;
          SET nsrc = nsrc + 1;
        END WHILE;
        SET iseq_nr = iseq_nr + 1;
        SET ifile_id = ifile_id + 1;
      END WHILE;
      SET iband = iband + 1;
    END WHILE;
    SET itau = itau + 1;
  END WHILE;

END;
//

DELIMITER ;

