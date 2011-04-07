insert into observations (obsid,time_s,description) values (1,20080324152759000,"test selgenimages");
insert into resolutions (resid, major, minor, pa) values (1,1,1,1);
insert into datasets (dsid, obs_id, res_id, dstype, taustart_timestamp, dsinname) values (1,1,1,1,20080319161117000, 'random***');
insert into frequencybands (freqbandid, freq_low, freq_high) values (1,30000000,40000000);
insert into zoneheight (zoneheight) values (1);

/**
 * The incoming stream of datasets can be split as follows:
 *  - integration time (tau)
 *  - frequency band (band)
 *  - sequence number in which this dataset was processed (seq_nr)
 *  - xtrsrcid, the srcid of all the sources extracted from this image (tau, band, seq_nr)
 */

/**
 * General cases:
 *
 * (1)
 * +-----------+       +-----------+
 * |           |       |           |
 * |  *        |       |  *        |
 * |           |       |           | New
 * |           |       |      *    |
 * |           |       |           |
 * +-----------+       +-----------+
 * 
 * Above, a new source is detected in the next image.
 *
 * (2)
 * +-----------+       +-----------+
 * |           |       |           |
 * |  *        |       |           |
 * |           |       |           | Not detected
 * |      *    |       |      *    |
 * |           |       |           |
 * +-----------+       +-----------+
 *
 * (3)
 * +-----------+       +-----------+
 * |           |       |           |
 * |  *        |       |  *        |
 * |           |       |           |
 * |      *    |       |      o    | Variable >
 * |           |       |           |
 * +-----------+       +-----------+
 *
 * (4)
 * +-----------+       +-----------+
 * |           |       |           |
 * |  *        |       |  *        |
 * |           |       |           |
 * |      o    |       |      *    | Variable <
 * |           |       |           |
 * +-----------+       +-----------+
 *
 */


/**
 * All the sources extracted from subsequent images will be inspected for 
 * source association.
 * To do so, we compare the current seq_nr with the previous one (@seq_nr - 1), 
 * in order to see if the source already existed and was associated.
 * An inspection query for this will look like:
 * Note that the user-defined variables (those with prefix '@') are the properties
 * from the source under inspection in the current seq_nr image.
 */

-- User-defined variables can be selected as follows:
SELECT zoneheight INTO @zoneheight FROM zoneheight;
-- The query below actually does not exist because it is not yet inserted into the database,
-- but the user-defined variables come from the source extraction routine and
-- can be used in a similar way. We use it here for instruction
SELECT seq_nr,ra,decl,x,y,z,GREATEST(ra_err,decl_err) 
INTO @seq_nr,@ra,@decl,@x,@y,@z,@theta FROM extractedsources WHERE xtrsrcid = current source;
-- The alpha inflation
SET @alpha = alpha(@theta, @decl);

--Queries in Assocate:
-- (1a)
select count(*) FROM cataloguesources WHERE zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta)) and cat_id = 1;
--or (1b)
select min(degrees(acos(@x * x + @y * y + @z * z))) FROM cataloguesources WHERE zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta)) and cat_id = 1;
-- (2a)
SELECT catsrcid,degrees(acos(@x * x + @y * y + @z * z)) as distance FROM cataloguesources WHERE zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta)) and cat_id = 1 and degrees(acos(@x * x + @y * y + @z * z)) = (select min(degrees(acos(@x * x + @y * y + @z * z))) FROM cataloguesources WHERE zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta)) and cat_id = 1);
-- or (2b)
SELECT catsrcid FROM cataloguesources WHERE zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta)) and cat_id = 1 and degrees(acos(@x * x + @y * y + @z * z)) = (select min(degrees(acos(@x * x + @y * y + @z * z))) FROM cataloguesources WHERE zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta)) and cat_id = 1);

-- Associate with catalogue
SELECT catsrcid FROM cataloguesources WHERE zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta));

-- Association with extractedsources
SELECT assoc_xtrsrcid FROM extractedsources WHERE zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta)) AND seq_nr = @seq_nr - 1;

-- distance
SELECT catsrcid, ra, decl,description, case when @x * x + @y * y + @z * z < 1 then degrees(acos(@x * x + @y * y + @z * z)) else 0 end as distance FROM cataloguesources,classification WHERE class_id = classid and zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) AND FLOOR((@decl + @theta)/@zoneheight) AND ra BETWEEN @ra - @alpha AND @ra + @alpha AND decl BETWEEN @decl - @theta AND @decl + @theta AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta)) order by distance ;

SELECT seq_nr,xtrsrcid,assoc_xtrsrcid,case when @x * x + @y * y + @z * z < 1 then degrees(acos(@x * x + @y * y + @z * z)) else 0 end as distance,ra_err,decl_err,i_peak,i_int FROM extractedsources WHERE assoc_xtrsrcid = 12082 or assoc_xtrsrcid = 12302 order by 1;

-- get min distance
SELECT catsrcid
      ,degrees(acos(@x * x + @y * y + @z * z)) as distance
  FROM cataloguesources 
 WHERE zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) 
                AND FLOOR((@decl + @theta)/@zoneheight)
   AND ra BETWEEN @ra - @alpha 
              AND @ra + @alpha            
   AND decl BETWEEN @decl - @theta 
                AND @decl + @theta            
   AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta))            
   and cat_id = 1 
   and degrees(acos(@x * x + @y * y + @z * z)) = (select min(degrees(acos(@x * x + @y * y + @z * z)))
                                                    FROM cataloguesources                       
                                                   WHERE zone BETWEEN FLOOR((@decl - @theta)/@zoneheight) 
                                                                  AND FLOOR((@decl + @theta)/@zoneheight)
                                                     AND ra BETWEEN @ra - @alpha 
                                                                AND @ra + @alpha                         
                                                     AND decl BETWEEN @decl - @theta 
                                                                  AND @decl + @theta                         
                                                     AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta))
                                                     and cat_id = 1                     
                                                 )
;


/**
 * Of course, the queries above will be coded immediately in one SQL statement
 */

/**
 * This query should return the same source in the previous processed image, 
 * including the associated source id.
 */
SELECT seq_nr
      ,xtrsrcid
      ,CASE WHEN @x * x + @y * y + @z * z < 1 
            THEN DEGREES(ACOS(@x * x + @y * y + @z * z)) 
            ELSE 0 
            END AS distance
      ,ra
      ,decl 
      ,assoc_xtrsrcid
      ,assoc_catsrcid
  FROM zones z INNER JOIN extractedsources es 
    ON z.zone = es.zone 
 WHERE z.decl_min BETWEEN @decl - @theta - @zoneheight AND @decl + @theta 
   AND es.ra BETWEEN @ra - @alpha AND @ra + @alpha 
   AND es.decl BETWEEN @decl - @theta AND @decl + @theta 
   AND (@x * x + @y * y + @z * z) > COS(RADIANS(@theta))
   AND es.seq_nr = @seq_nr - 1
   AND es.assoc_xtrsrcid IS NOT NULL
;
