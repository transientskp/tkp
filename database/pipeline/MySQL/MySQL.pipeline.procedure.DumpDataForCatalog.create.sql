USE pipeline;

DROP PROCEDURE DumpData;

DELIMITER //

/**
 * This procedure will create the outfiles,
 * that can are ready to be loeaded into the catalog database
 * For this, we will get the data from 
 *  - observations
 *  - datasets
 *  - frequencybands
 *  - extractedsources
 *
 * This data will be loaded into the catalogue database
 * in the tables
 *  - measurements
 *  - sources TODO: is this still the proper design?
 *  - frequencybands
 *  - effectivefrequencies
 */
CREATE PROCEDURE DumpData(IN itau INT)

BEGIN

  /**
   * First, we select the observation data
   * then the dataset data
   */
  SELECT tau
        ,band
        ,assoc_xtrsrcid
    INTO OUTFILE '/home/bscheers/databases/outfiles/measurements.txt'
  FIELDS TERMINATED BY ',' 
  LINES TERMINATED BY '\n'
    FROM extractedsources;

  /**
   * observation ids
   */
  SELECT * 
    FROM observations o
        ,(SELECT dsid 
            FROM datasets ds
                ,(SELECT ds_id 
                    FROM extractedsources 
                  GROUP BY assoc_xtrsrcid) es 
           WHERE ds.dsid = es.ds_id 
          GROUP BY ds.dsid) dso 
   WHERE o.obsid = dso.dsid 
  GROUP BY o.obsid;

  /**
   * dataset ids 
   */
  SELECT * 
    INTO OUTFILE '/home/bscheers/databases/outfiles/datasets.txt'
  FIELDS TERMINATED BY ','
  LINES TERMINATED BY '\n'
    FROM datasets ds
        ,(SELECT ds_id 
            FROM extractedsources 
          GROUP BY assoc_xtrsrcid) es 
   WHERE ds.dsid = es.ds_id 
  GROUP BY es.ds_id;

  /**
   * The frequencybands:
   */

  /**
   * The sources
   */

  /**
   * The measurements corresponging to the sources
   */

  SELECT es1.xtrsrcid
        ,es1.assoc_xtrsrcid
        ,es1.I 
    FROM extractedsources es1
        ,(SELECT assoc_xtrsrcid 
            FROM extractedsources 
          GROUP BY assoc_xtrsrcid) es2 
   WHERE es1.assoc_xtrsrcid = es2.assoc_xtrsrcid 
  ORDER BY es1.assoc_xtrsrcid
          ,es1.xtrsrcid
  ;


END;
//

DELIMITER ;

/*
 * The End.
 */

