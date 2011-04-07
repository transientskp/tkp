DROP PROCEDURE IF EXISTS CollectForDump;

DELIMITER //


/* We cursor through the associatedsources table
 * order by xtrsrc_id, assoc_xtrsrcid
 */
CREATE PROCEDURE CollectForDump(IN ixtrsrc_id INT
                               ,IN iassoc_xtrsrcid INT
                               )
BEGIN

  DECLARE ixtrsrcid1 INT;
  DECLARE ixtrsrcid2 INT;

  DECLARE iinsert_src1 BOOLEAN DEFAULT FALSE;
  DECLARE iinsert_src2 BOOLEAN DEFAULT FALSE;

  DECLARE iavgsrcid INT;
  
  SET ixtrsrcid1 = ixtrsrc_id;
  SET ixtrsrcid2 = iassoc_xtrsrcid;

  /*
  SELECT CASE WHEN COUNT(*) = 0
              THEN TRUE
              ELSE FALSE
              END
    INTO iinsert_src1
    FROM aux_associatedsources
   WHERE xtrsrcid1 = ixtrsrcid1
      OR xtrsrcid2 = ixtrsrcid1
  ;
  
  IF ixtrsrcid2 <> ixtrsrcid1 THEN
    SELECT CASE WHEN COUNT(*) = 0
                THEN TRUE
                ELSE FALSE
                END
      INTO iinsert_src2
     FROM aux_associatedsources
    WHERE xtrsrcid1 = ixtrsrcid2
       OR xtrsrcid2 = ixtrsrcid2
    ;
  END IF;
  */

  /**
   * Now that we have the two sources we have to add some fields for 
   * saying how to insert them into the tables of the catalog database
   * The measurements table and the associatedsources table.
   * We append to flag columns, stating whether a source must be inserted
   * or not, this can be deduced by having count(*) > 1.
   * We have to be carefull not to insert duplicates.
   * And we should check whether their exist
   * previous associations in the catalog database.
   * 
   */

  /**
   * Is it allowed to execute select into outfile within procedure?
   * We might insert the data in a temp dump table instead.
   * 
   */

  /* FOr the first insert of the first occurrance we 
   * will get the avgd position of the associatedsources.
   * TODO: difference between X and C associations.
   */
  IF iinsert_src1 = TRUE THEN
    INSERT INTO averagedsources 
      (xtrsrc_id1
      ,ra
      ,decl
      ,ra_err
      ,decl_err
      ,I_peak
      ,I_peak_err
      ,I_int
      ,I_int_err
      )
      SELECT ixtrsrcid1
            ,AVG(e.ra)
            ,AVG(e.decl)
            ,AVG(e.ra_err)
            ,AVG(e.decl_err) 
            ,AVG(e.i_peak)
            ,AVG(e.i_peak_err)
            ,AVG(e.i_int)
            ,AVG(e.i_int_err)
      FROM associatedsources a
          ,extractedsources e
          ,images i 
     WHERE i.imageid = e.image_id  
       AND a.xtrsrc_id = e.xtrsrcid 
       AND a.xtrsrc_id = ixtrsrcid1
       AND a.src_type = 'X'
       /*AND ds_id = 1 */
       AND a.assoc_xtrsrcid IS NOT NULL 
    GROUP BY a.xtrsrc_id  
    /*ORDER BY xtrsrc_id*/
    ;
    SET iavgsrcid = LAST_INSERT_ID();
  ELSE
    SELECT avgsrcid
      INTO iavgsrcid
      FROM averagedsources
     WHERE xtrsrc_id1 = ixtrsrcid1
    ;
  END IF;


  /* We check the temp table to see
   * whether one of the two sources has already an occurance
   * in which case we don't have to insert it again
   * NOTE: This is the right place to find that out, 
   * no sooner or later.
   *
   * NOTE: But of course, if a source is flagged as not to be inserted
   * we do not have to insert all its values in aux_associatedsources,
   * we can set them to NULL.
   * 
   * NOTE: We should keep track of the averaged sources, some id that
   * is the same for the group by xtrsrcid1, and different for the next group.
   *
   * NOTE: avg src will only be inserted if insert_src1 is true
   */
  /*
  INSERT INTO aux_associatedsources 
    (xtrsrcid1
    ,insert_src1
    ,xtrsrcid2
    ,insert_src2
    ,avgsrc_id
    )
    VALUES 
    (ixtrsrcid1
    ,iinsert_src1
    ,ixtrsrcid2
    ,iinsert_src2
    ,iavgsrcid
    )
  ;
  */

  /* This must be sufficient.
   * In the catalog database src1 and src2 will be inserted to the 
   * measurements table.
   * These will give for each source an last_insert_id()
   * that will serve as ids for the catalog.associatedsources table.
   * This needs some further investigation, to check if the srcs can be 
   * associated with previous ones.
   */

  /* We want to avg the source position of all
   * the sources that were associated with each
   * other in the pipeline.associatedsources table.
   * This can be done either in the pipeline or catalog environment
   * (I think catalog is better.)
   */

END;
//

DELIMITER ;

