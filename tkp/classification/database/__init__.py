import datetime
import tkp.database.database
from ..manual.transient import Transient
from ..manual.utils import Position, DateTime


STATUS = dict(
    ACTIVE=0,
    CLASSIFIED=1,
    MONITOR=2
    )


class DBConnection(object):

    def __init__(self, *args, **kwargs):
        super(DBConnection, self).__init__(*args, **kwargs)
        self.connection = tkp.database.database.connection()
        self.keys = ('ax2.xtrsrc_id', 'datapoints', 'min_i_peak', 'avg_i_peak',
                     'max_i_peak', 'sig_i_peak', 'v_nu', 'eta_nu')
        self.sql_command = """\
SELECT ax2.xtrsrc_id 
      ,count(*) as datapoints 
      ,min(x2.i_peak) as min_i_peak 
      ,avg(x2.i_peak) as avg_i_peak 
      ,max(x2.i_peak) as max_i_peak 
         ,sqrt(count(*) 
           * (avg(x2.i_peak * x2.i_peak) - avg(x2.i_peak) * avg(x2.i_peak))
           / (count(*) - 1)
           )
       /avg(x2.i_peak) as v_nu 
      ,sqrt((avg(x2.i_peak * x2.i_peak)) - avg(x2.i_peak) * avg(x2.i_peak)) as sig_i_peak 
      ,count(*) * (avg((x2.i_peak / x2.i_peak_err) * (x2.i_peak / x2.i_peak_err)) 
                  - 2 * avg(x2.i_peak) * avg(x2.i_peak / (x2.i_peak_err * x2.i_peak_err)) 
                  + avg(x2.i_peak) * avg(x2.i_peak) * avg(1 / (x2.i_peak_err * x2.i_peak_err))
                  ) 
                / (count(*) - 1) as eta_nu
  FROM assocxtrsources ax2 
      ,extractedsources x1 
      ,extractedsources x2 
      ,images im1 
 WHERE ax2.xtrsrc_id = %s
   AND ax2.xtrsrc_id = x1.xtrsrcid 
   AND ax2.assoc_xtrsrc_id = x2.xtrsrcid 
   AND x1.image_id = im1.imageid 
GROUP BY ax2.xtrsrc_id 
HAVING COUNT(*) > 1 
ORDER BY eta_nu
        ,ax2.xtrsrc_id
;"""
        self.sql_command2 = """\
SELECT assoc_xtrsrc_id 
FROM assocxtrsources
WHERE xtrsrc_id = %s
;"""
        self.sql_command3 = """\
SELECT xtrsrcid, image_id, ra, decl, ra_err, decl_err, i_peak, i_peak_err, det_sigma,
       sqrt(ra_err*ra_err + decl_err*decl_err) as pos_err
FROM extractedsources 
WHERE xtrsrcid = %s
;"""
        self.sql_command4 = """\
SELECT tau, taustart_ts, freq_eff, url
FROM images
WHERE imageid = %s
;"""

    def query(self, source_id=None):
        if source_id is None:
            return []
        cursor = self.connection.cursor()
        cursor.execute(self.sql_command, (source_id,))
        keys =  [specs[0] for specs in cursor.description]
        results = cursor.fetchall()
        cursor.close()
        for i in range(len(results)):
            results[i] = dict(zip(keys, results[0]))
        return results

    def query_transient(self, source_id=None):
        if source_id is None:
            return None
        cursor = self.connection.cursor()
        cursor.execute(self.sql_command, (source_id,))
        results = cursor.fetchone()
        cursor.execute(self.sql_command2, (source_id,))
        results = cursor.fetchall()
        start_dates = []
        end_dates = []
        durations = []
        pos_error = 64800
        for assoc_id in results:
            cursor.execute(self.sql_command3, (assoc_id[0],))
            results2 = cursor.fetchone()
            ra = results2[2]
            dec = results2[3]
            pos_error = results2[-1]
            if results2[-1] < pos_error:
                ra = results2[2]
                dec = results2[3]
                pos_error = results2[-1]
            cursor.execute(self.sql_command4, (results2[1],))
            results3 = cursor.fetchone()
            start_dates.append(results3[1])
            durations.append(results3[0])
            end_dates.append(results3[1] + datetime.timedelta(0, durations[-1]))
        cursor.close()
        position = Position(ra, dec, pos_error/3600.)
        start_dates = sorted(start_dates)
        end_dates = sorted(end_dates)
        timezero = DateTime(
            start_dates[0].year, start_dates[0].month, start_dates[0].day, 
            start_dates[0].hour, start_dates[0].minute, start_dates[0].second, 
            error=1)
        duration = end_dates[-1] - start_dates[0]
        duration = duration.days + duration.seconds/86400.
        transient = Transient(id=source_id, duration=duration, variability=1,
                              database='', position=position, 
                              timezero=timezero,
                              shape='')
        return transient
