SET SCHEMA pipeline;

DROP PROCEDURE InitObservation;

/**
 * This procedure initialises the pipeline database after it is created
 * successfully.
 */
CREATE PROCEDURE InitObservation(izoneheight DOUBLE
                                ,itheta DOUBLE
                                )
BEGIN

  /* We build 1 degree broad zones */
  /*CALL BuildZones(izoneheight, itheta);*/

  /* For testing, we insert some tables (after deleting old data) */
  DELETE FROM frequencybands;
  DELETE FROM datasets;
  DELETE FROM resolutions;
  DELETE FROM observations;

  INSERT INTO observations 
    (obsid
    ,time_s
    ,description
    ) VALUES 
    (1
    ,20080403140303000
    ,'test images'
    )
  ;

  INSERT INTO resolutions 
    (resid
    ,major
    ,minor
    ,pa
    ) VALUES 
    (1
    ,1
    ,1
    ,1)
  ;

  INSERT INTO datasets 
    (dsid
    ,obs_id
    ,res_id
    ,dstype
    ,taustart_timestamp
    ,dsinname
    ) VALUES 
    (1
    ,1
    ,1
    ,1
    ,20080403140303000
    ,'random***'
    )
  ;

  INSERT INTO frequencybands 
    (freqbandid
    ,freq_low
    ,freq_high
    ) VALUES 
    (1
    ,30000000
    ,40000000
    )
  ;

END;

