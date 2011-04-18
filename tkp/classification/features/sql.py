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
