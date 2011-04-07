COPY 
SELECT t.line
  FROM (SELECT CAST('#(Name, Type, Ra, Dec, I, Q, U, V, MajorAxis, MinorAxis, Orientation, ReferenceFrequency, SpectralIndexDegree, SpectralIndex:0, SpectralIndex:1) = format' AS VARCHAR(300)) as line
        UNION
        SELECT CAST(CONCAT(t0.catsrcname, CONCAT(',', 
                    CONCAT(t0.src_type, CONCAT(',', 
                    CONCAT(t0.ra, CONCAT(',', 
                    CONCAT(t0.decl, CONCAT(',', 
                    CONCAT(t0.i, CONCAT(',', 
                    CONCAT(t0.q, CONCAT(',', 
                    CONCAT(t0.u, CONCAT(',', 
                    CONCAT(t0.v, CONCAT(',', 
                    CONCAT(t0.MajorAxis, CONCAT(',', 
                    CONCAT(t0.MinorAxis, CONCAT(',', 
                    CONCAT(t0.Orientation, CONCAT(',', 
                    CONCAT(t0.ReferenceFrequency, CONCAT(',', 
                    CONCAT(t0.SpectralIndexDegree, CONCAT(',', 
                    CONCAT(t0.SpectralIndex_0, CONCAT(',', t0.SpectralIndex_1))
                    )))))))))))))))))))))))))) AS VARCHAR(300)) AS line
          FROM (SELECT CAST(TRIM(c1.catsrcname) AS VARCHAR(20)) as catsrcname
                      ,CAST('POINT' AS VARCHAR(20)) as src_type
                      ,CAST(c1.ra AS VARCHAR(20))  as ra
                      ,CAST(c1.decl AS VARCHAR(20)) as decl
                      ,CAST(c1.i_int_avg AS VARCHAR(20)) as i
                      ,CAST(0 AS VARCHAR(20)) as q
                      ,CAST(0 AS VARCHAR(20)) as u
                      ,CAST(0 AS VARCHAR(20)) as v
                      ,case when c1.major is null
                            then cast('' as VARCHAR(20))
                            else cast(c1.major as varchar(20))
                       end as MajorAxis
                      ,case when c1.minor is null
                            then cast('' as VARCHAR(20))
                            else cast(c1.minor as varchar(20))
                       end as MinorAxis
                      ,case when c1.pa is null
                            then cast('' as VARCHAR(20))
                            else cast(c1.pa as varchar(20))
                       end as Orientation
                      ,CAST(c1.freq_eff AS VARCHAR(20)) as ReferenceFrequency
                      ,CASE WHEN si.spindx_degree IS NULL
                            THEN CAST('' AS VARCHAR(20))
                            ELSE CAST(si.spindx_degree AS VARCHAR(20))
                       END as SpectralIndexDegree
                      ,CASE WHEN si.spindx_degree IS NULL 
                            THEN CASE WHEN si.c0 IS NULL
                                      THEN CAST(0 as varchar(20))
                                      ELSE CAST(si.c0 as varchar(20))
                                 END
                            ELSE CASE WHEN si.c0 IS NULL
                                      THEN CAST('' as varchar(20))
                                      ELSE CAST(si.c0 as varchar(20))
                                 END
                       end as SpectralIndex_0
                      ,case when si.c1 is null 
                            then cast('' as varchar(20))
                            else cast(si.c1 as varchar(20))
                       end as SpectralIndex_1
                  FROM catalogedsources c1
                       LEFT OUTER JOIN spectralindices si ON c1.catsrcid = si.catsrc_id
                 WHERE c1.cat_id = 3
                   AND c1.ra BETWEEN 120 AND 125
                   AND c1.decl BETWEEN 75 AND 80
                   AND c1.i_int_avg > 0.1
               ) t0
       ) t
INTO '/scratch/bscheers/databases/dumps/lsmtest.txt'
DELIMITERS ','
          ,'\n'
          ,''
;


















COPY 
SELECT t.line
  FROM (SELECT CAST('(Name, Type, Ra, Dec, I, Q, U, V, MajorAxis, MinorAxis, Orientation, ReferenceFrequency, SpectralIndexDegree, SpectralIndex:0, SpectralIndex:1) = format' AS VARCHAR(300)) as line
        UNION
        SELECT CAST(CONCAT(t0.catsrcname, CONCAT(',', 
                    CONCAT(t0.src_type, CONCAT(',', 
                    CONCAT(t0.ra, CONCAT(',', 
                    CONCAT(t0.decl, CONCAT(',', 
                    CONCAT(t0.i, CONCAT(',', 
                    CONCAT(t0.q, CONCAT(',', 
                    CONCAT(t0.u, CONCAT(',', 
                    CONCAT(t0.v, CONCAT(',', 
                    CONCAT(t0.MajorAxis, CONCAT(',', 
                    CONCAT(t0.MinorAxis, CONCAT(',', 
                    CONCAT(t0.Orientation, CONCAT(',', 
                    CONCAT(t0.ReferenceFrequency, CONCAT(',', 
                    CONCAT(t0.SpectralIndexDegree, CONCAT(',', 
                    CONCAT(t0.SpectralIndex_0, CONCAT(',', t0.SpectralIndex_1)))))))))))))))))))))))))))) AS VARCHAR(300)) AS line
          FROM (SELECT c1.catsrcname
                      ,'POINT' as src_type
                      ,c1.ra
                      ,c1.decl
                      ,c1.i_int_avg as i
                      ,0 as q
                      ,0 as u
                      ,0 as v
                      ,case when c1.major is null
                            then cast('' as VARCHAR(10))
                            else cast(c1.major as varchar(10))
                       end as MajorAxis
                      ,case when c1.minor is null
                            then cast('' as VARCHAR(10))
                            else cast(c1.minor as varchar(10))
                       end as MinorAxis
                      ,case when c1.pa is null
                            then cast('' as VARCHAR(10))
                            else cast(c1.pa as varchar(10))
                       end as Orientation
                      ,c1.freq_eff as ReferenceFrequency
                      ,si.spindx_degree as SpectralIndexDegree
                      ,case when si.c0 is null
                            then cast('' as varchar(10))
                            else cast(si.c0 as varchar(10))
                       end as SpectralIndex_0
                      ,case when si.c1 is null 
                            then cast('' as varchar(10))
                            else cast(si.c1 as varchar(10))
                       end as SpectralIndex_1
                  FROM catalogedsources c1
                      ,spectralindices si
                 WHERE c1.cat_id = 4
                   AND c1.catsrcid = si.catsrc_id
                   AND ra BETWEEN 50.5 AND 55.5
                   AND decl BETWEEN 52 AND 57
               ) t0
       ) t
/*INTO '/scratch/bscheers/databases/dumps/lsmtest.txt'*/
INTO '/home/scheers/dumps/lsmtest.txt'
DELIMITERS ','
          ,'\n'
          ,''
;





