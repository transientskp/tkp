select es.class_id as assoc
      ,assoc_xtrsrcid
      ,assoc_catsrcid
      ,es.ra
      ,es.decl
      ,I_peak
      ,I_peak_avg
      ,i_peak_avg_err
      ,abs(I_peak-I_peak_avg)/i_peak_avg_err as peak
  from extractedsources es
      ,cataloguesources cs 
 where assoc_catsrcid = catsrcid 
   and cat_id = 2 
   and ds_id = 2 
   and assoc_catsrcid is not null 
   and es.class_id = 1000 
order by 9 desc 
limit 40
;
