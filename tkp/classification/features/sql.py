lightcurve = """\
    SELECT im.taustart_ts
          ,im.tau_time
          ,ex.f_peak
          ,ex.f_peak_err
          ,ex.id
      FROM extractedsource ex
          ,assocxtrsource ax
          ,image im
     WHERE ax.runcat = %s
       AND ax.xtrsrc = ex.id
       AND ex.image = im.id
       AND stokes = 1
    ORDER BY im.taustart_ts
"""
