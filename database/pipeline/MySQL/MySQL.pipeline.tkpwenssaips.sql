USE pipeline;

select dsid2
      ,es2.xtrsrcid
      ,TKP_peak
      ,AIPS_peak
      ,cs2.i_peak_avg as WENSS_peak
      ,peak
  from 
(SELECT es1.xtrsrcid AS dsid2
      ,es1.assoc_catsrcid as assoc_cat
      ,es1.ra
      ,es1.decl
      ,es1.I_peak as TKP_peak
      ,cs1.I_peak_avg as AIPS_peak
      ,cs1.i_peak_avg_err
      ,abs(es1.I_peak - cs1.I_peak_avg) / cs1.i_peak_avg_err as peak
      /*,es2.assoc_catsrcid as WENSS_catid*/
  from extractedsources es1
      /*,extractedsources es2*/
      ,cataloguesources cs1 
      /*,cataloguesources cs2*/
 where es1.assoc_catsrcid = cs1.catsrcid 
   /*and cat_id = 2 */
   and es1.ds_id = 2 
   and es1.assoc_catsrcid is not null 
   and es1.class_id = 1000
   /*and es1.xtrsrcid + 11514 = es2.xtrsrcid*/
) t1
,extractedsources es2
,cataloguesources cs2
where dsid2 + 11514 = es2.xtrsrcid
  and cs2.catsrcid = es2.assoc_catsrcid
order by 6 desc
limit 10
;
