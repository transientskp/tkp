DROP PROCEDURE IF EXISTS DumpSrcs;

DELIMITER //

/*+-------------------------------------------------------------------+
 *| This script dumps the pipeline.aux_assoc.ociatedsources and          |
 *| -.averagedsources, together with -.extractedsources tables into   |
 *| an outfile that will serve assoc.input data for the catalog databassoc. |
 *| upload.                                                           |
 *|                                                                   |
 *+-------------------------------------------------------------------+
 *| Bart Scheers                                                      |
 *| 2008-09-24                                                        |
 *+-------------------------------------------------------------------+
 *| Open Questions:                                                   |
 *+-------------------------------------------------------------------+
 */
CREATE PROCEDURE DumpSrcs()
BEGIN

  SELECT assoc.xtrsrc_id
        /* TODO Here we can say something of the 
        type of association: time,freq., cat, xtr, ...
        'X' meaning here associated in time as well as in frequency
        */
        ,'X' AS assoc_type
        ,assoc.insert_src1
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN e1.ra
              ELSE NULL
         END AS ra
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN e1.decl
              ELSE NULL
         END AS decl
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN e1.ra_err
              ELSE NULL
         END AS ra_err
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN e1.decl_err
              ELSE NULL
         END AS decl_err
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN e1.i_peak
              ELSE NULL
         END AS i_peak
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN e1.i_peak_err
              ELSE NULL
         END AS i_peak_err
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN e1.i_int
              ELSE NULL
         END AS i_int
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN e1.i_int_err
              ELSE NULL
         END AS i_int_err
        ,assoc.assoc_xtrsrcid
        ,assoc.insert_src2
        ,CASE WHEN assoc.insert_src2 = TRUE
              THEN e2.ra
              ELSE NULL
         END AS ra
        ,CASE WHEN assoc.insert_src2 = TRUE
              THEN e2.decl
              ELSE NULL
         END AS decl
        ,CASE WHEN assoc.insert_src2 = TRUE
              THEN e2.ra_err
              ELSE NULL
         END AS ra_err
        ,CASE WHEN assoc.insert_src2 = TRUE
              THEN e2.decl_err
              ELSE NULL
         END AS decl_err
        ,CASE WHEN assoc.insert_src2 = TRUE
              THEN e2.i_peak
              ELSE NULL
         END AS i_peak
        ,CASE WHEN assoc.insert_src2 = TRUE
              THEN e2.i_peak_err
              ELSE NULL
         END AS i_peak_err
        ,CASE WHEN assoc.insert_src2 = TRUE
              THEN e2.i_int
              ELSE NULL
         END AS i_int
        ,CASE WHEN assoc.insert_src2 = TRUE
              THEN e2.i_int_err
              ELSE NULL
         END AS i_int_err
        ,av.avgsrcid
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN av.ra
              ELSE NULL
         END AS ra
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN av.decl
              ELSE NULL
         END AS decl
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN av.ra_err
              ELSE NULL
         END AS ra_err
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN av.decl_err
              ELSE NULL
         END AS decl_err
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN av.i_peak
              ELSE NULL
         END AS i_peak
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN av.i_peak_err
              ELSE NULL
         END AS i_peak_err
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN av.i_int
              ELSE NULL
         END AS i_int
        ,CASE WHEN assoc.insert_src1 = TRUE
              THEN av.i_int_err
              ELSE NULL
         END AS i_int_err
    INTO OUTFILE '/home/bscheers/databases/dumps/dump-X-srcs.csv'
         FIELDS TERMINATED BY ';'
         LINES TERMINATED BY '\n'
    FROM associatedsources assoc
        ,extractedsources e1
        ,extractedsources e2
        ,averagedsources av
   WHERE assoc.xtrsrc_id = e1.xtrsrcid
     AND assoc.assoc_xtrsrcid = e2.xtrsrcid
     AND assoc.xtrsrc_id = av.xtrsrc_id1
  ;

END;
//

DELIMITER ;
