lightcurve = """\
    SELECT
         im.taustart_ts
        ,im.tau_time
        ,ex.i_peak
        ,ex.i_peak_err
        ,ex.xtrsrcid
    FROM
        extractedsources ex
       ,assocxtrsources ax
       ,images im
    WHERE
        ax.xtrsrc_id = %s
      AND ex.xtrsrcid = ax.assoc_xtrsrc_id
      AND ex.image_id = im.imageid
    ORDER BY im.taustart_ts
"""

fluxincrease = """\
SELECT
     im1.taustart_ts
    ,im1.tau_time
    ,x1.i_peak
    ,x1.i_peak_err
 FROM
    extractedsources x1
   ,assocxtrsources ax1
   ,images im1
 WHERE
   ax1.xtrsrc_id = %s
   AND x1.xtrsrcid = ax1.assoc_xtrsrc_id
   AND x1.image_id = im1.imageid
 ORDER BY im1.taustart_ts DESC
 LIMIT 2
"""


status = """\
SELECT
  status, xtrsrc_id
FROM
  transients
WHERE
  xtrsrc_id = %s
"""
