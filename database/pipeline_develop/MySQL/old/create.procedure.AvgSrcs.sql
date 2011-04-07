DROP PROCEDURE IF EXISTS AvgSrcs;

DELIMITER //


/* We cursor through the associatedsources table
 * order by xtrsrc_id, assoc_xtrsrcid
 */
CREATE PROCEDURE AvgSrcs(IN ids_id INT)
BEGIN

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
    SELECT a.xtrsrc_id
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
       AND a.src_type = 'X'
       AND i.ds_id = ids_id
       AND a.assoc_xtrsrcid IS NOT NULL 
    GROUP BY a.xtrsrc_id  
    /*ORDER BY xtrsrc_id*/
  ;

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

