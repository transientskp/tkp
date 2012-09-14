select t.xtrsrc_id,t.assoc_xtrsrc_id,t.assoc_distance_arcsec,t.i_int,t.i_int_err,t.i_int_avg,sqrt(t.cnt/(t.cnt-1))*(t.i_int - t.i_int_avg)/t.i_int_err as delta from (select ax.xtrsrc_id,ax.assoc_xtrsrc_id,ax.assoc_distance_arcsec,i_int,i_int_err,t0.cnt,t0.i_int_avg  from assocxtrsources ax,extractedsources ,images,(select t1.xtrsrc_id,count(*) as cnt,avg(t1.i_int) as i_int_avg from (select ax0.xtrsrc_id,ax0.assoc_xtrsrc_id,ax0.assoc_distance_arcsec,x0.i_int,x0.i_int_err from assocxtrsources ax0,extractedsources x0,images im0 where x0.xtrsrcid = ax0.assoc_xtrsrc_id and im0.imageid = x0.image_id and ax0.xtrsrc_id = 35) t1 group by t1.xtrsrc_id) t0  where xtrsrcid = assoc_xtrsrc_id and imageid = image_id and ax.xtrsrc_id = 35) t;

/**/
select t.xtrsrc_id,t.assoc_xtrsrc_id,t.assoc_distance_arcsec,t.i_int,t.i_int_err,t.i_int_avg from (select ax.xtrsrc_id,ax.assoc_xtrsrc_id,ax.assoc_distance_arcsec,i_int,i_int_err,t0.i_int_avg  from assocxtrsources ax,extractedsources ,images,(select t1.xtrsrc_id,avg(t1.i_int) as i_int_avg from (select ax0.xtrsrc_id,ax0.assoc_xtrsrc_id,ax0.assoc_distance_arcsec,x0.i_int,x0.i_int_err from assocxtrsources ax0,extractedsources x0,images im0 where x0.xtrsrcid = ax0.assoc_xtrsrc_id and im0.imageid = x0.image_id and ax0.xtrsrc_id = 35) t1 group by t1.xtrsrc_id) t0  where xtrsrcid = assoc_xtrsrc_id and imageid = image_id and ax.xtrsrc_id = 35) t;

select t.xtrsrc_id
      ,t.assoc_xtrsrc_id,t.assoc_distance_arcsec,t.i_int,t.i_int_err,t.i_int_avg from (select ax.xtrsrc_id,ax.assoc_xtrsrc_id,ax.assoc_distance_arcsec,i_int,i_int_err,t0.i_int_avg  from assocxtrsources ax,extractedsources ,images,(select t1.xtrsrc_id,avg(t1.i_int) as i_int_avg from (select ax0.xtrsrc_id,ax0.assoc_xtrsrc_id,ax0.assoc_distance_arcsec,x0.i_int,x0.i_int_err from assocxtrsources ax0,extractedsources x0,images im0 where x0.xtrsrcid = ax0.assoc_xtrsrc_id and im0.imageid = x0.image_id and ax0.xtrsrc_id = 35) t1 group by t1.xtrsrc_id) t0  where xtrsrcid = assoc_xtrsrc_id and imageid = image_id and ax.xtrsrc_id = 35) t;

--------------


/* This query makes an overview of the data being processed.
 * The number of occurences in the time sequence is printed, together with the number
 * of sources that occurred that many times. Also the averages are printed.*/
select t.cnt,count(*),avg(t.dist_avg),avg(t.r_avg),avg(t.lr_avg),avg(t.quot_avg) from (select ax.xtrsrc_id      ,count(*) as cnt     ,avg(ax.assoc_distance_arcsec) as dist_avg      ,avg(ax.assoc_r) as r_avg      ,avg(ax.assoc_lr) as lr_avg      ,avg(i_int_avg/i_int) as quot_avg,avg(i_int) as flux_avg,sqrt(count(*)*(avg(i_int*i_int) - avg(i_int)*avg(i_int))/(count(*)-1)) as flux_std,sqrt(count(*)*(avg(i_int*i_int) - avg(i_int)*avg(i_int))/(count(*)-1))/avg(i_int) as sigma_mu  from assocxtrsources ax      ,assoccatsources ac      ,extractedsources      ,catalogedsources      ,images where ax.xtrsrc_id = ac.xtrsrc_id and ax.assoc_lr > -10 and ac.assoc_lr > -10 and xtrsrcid = assoc_xtrsrc_id and assoc_catsrc_id = catsrcid  and imageid = image_id group by ax.xtrsrc_id ) t group by t.cnt order by t.cnt;

/*This query selects the associated sources and some averaged values*/
select t.xtrsrc_id,t.cnt,t.dist_avg,t.r_avg,t.lr_avg,t.quot_avg from (select ax.xtrsrc_id      ,count(*) as cnt     ,avg(ax.assoc_distance_arcsec) as dist_avg      ,avg(ax.assoc_r) as r_avg      ,avg(ax.assoc_lr) as lr_avg      ,avg(i_int_avg/i_int) as quot_avg,avg(i_int) as flux_avg,sqrt(count(*)*(avg(i_int*i_int) - avg(i_int)*avg(i_int))/(count(*)-1)) as flux_std,sqrt(count(*)*(avg(i_int*i_int) - avg(i_int)*avg(i_int))/(count(*)-1))/avg(i_int) as sigma_mu  from assocxtrsources ax      ,assoccatsources ac      ,extractedsources      ,catalogedsources      ,images where ax.xtrsrc_id = ac.xtrsrc_id and xtrsrcid = assoc_xtrsrc_id and assoc_catsrc_id = catsrcid  and imageid = image_id group by ax.xtrsrc_id ) t order by t.quot_avg;

select t.* from (select ax.xtrsrc_id      ,count(*) as cnt     ,avg(ax.assoc_distance_arcsec) as dist_avg      ,avg(ax.assoc_r) as r_avg      ,avg(ax.assoc_lr) as lr_avg      ,avg(i_int_avg/i_int) as quot_avg,avg(i_int) as flux_avg,sqrt(count(*)*(avg(i_int*i_int) - avg(i_int)*avg(i_int))/(count(*)-1)) as flux_std,sqrt(count(*)*(avg(i_int*i_int) - avg(i_int)*avg(i_int))/(count(*)-1))/avg(i_int) as sigma_mu  from assocxtrsources ax      ,assoccatsources ac      ,extractedsources      ,catalogedsources      ,images where ax.xtrsrc_id = ac.xtrsrc_id and xtrsrcid = assoc_xtrsrc_id and assoc_catsrc_id = catsrcid  and imageid = image_id group by ax.xtrsrc_id having count(*) = 8) t order by t.sigma_mu 
;

/**/
select ax.xtrsrc_id,count(*),avg(ax.assoc_distance_arcsec) as dist_avg,avg(ax.assoc_r) as r_avg,avg(ax.assoc_lr) as lr_avg,avg(i_int_avg/i_int) as quot_avg from assocxtrsources ax,assoccatsources ac,extractedsources,catalogedsources,images where ax.xtrsrc_id = ac.xtrsrc_id and xtrsrcid = assoc_xtrsrc_id and assoc_catsrc_id = catsrcid and imageid = image_id group by ax.xtrsrc_id order by ax.xtrsrc_id limit 12
;

select ax.xtrsrc_id
      ,count(*)
      ,avg(ax.assoc_distance_arcsec) as dist_avg
      ,avg(ax.assoc_r) as r_avg
      ,avg(ax.assoc_lr) as lr_avg
      ,avg(i_int_avg/i_int) as quot_avg 
  from assocxtrsources ax
      ,assoccatsources ac
      ,extractedsources
      ,catalogedsources
      ,images 
 where ax.xtrsrc_id = ac.xtrsrc_id
   and xtrsrcid = assoc_xtrsrc_id
   and assoc_catsrc_id = catsrcid
   and imageid = image_id
group by ax.xtrsrc_id
order by ax.xtrsrc_id
limit 12
;

select xtrsrc_id
      ,avg(assoc_r) 
  from assocxtrsources
      ,extractedsources
      ,images 
 where xtrsrcid = assoc_xtrsrc_id 
   and imageid = image_id 
group by xtrsrc_id 
;

--------------------------------------

/* this query selects all the measurements for source 11,
 * computes the flux ratio of these with the associated catalog source
 */
select ax.xtrsrc_id
      ,assoc_xtrsrc_id
      ,ax.assoc_distance_arcsec
      ,ax.assoc_r
      ,ax.assoc_lr
      ,i_int_avg/i_int as quot 
  from assocxtrsources ax
      ,assoccatsources ac
      ,extractedsources
      ,catalogedsources
      ,images 
 where ax.xtrsrc_id = ac.xtrsrc_id 
   and xtrsrcid = assoc_xtrsrc_id 
   and assoc_catsrc_id = catsrcid 
   and imageid = image_id 
   and ax.xtrsrc_id = 11 
order by ax.xtrsrc_id
        ,assoc_xtrsrc_id 
limit 12
;




select ac.*
      ,i_int_avg/i_int 
  from assoccatsources ac
      ,extractedsources
      ,catalogedsources 
 where xtrsrc_id = xtrsrcid 
   and assoc_catsrc_id = catsrcid 
   and xtrsrc_id in (select assoc_xtrsrc_id 
                       from assocxtrsources
                           ,extractedsources
                           ,images 
                      where xtrsrcid = assoc_xtrsrc_id 
                        and imageid = image_id 
                        and xtrsrc_id = 3
                    )
;


select avg(i_int_avg/i_int) 
  from assoccatsources ac
      ,extractedsources
      ,catalogedsources 
 where xtrsrc_id = xtrsrcid 
   and assoc_catsrc_id = catsrcid 
   and xtrsrc_id in (select assoc_xtrsrc_id 
                       from assocxtrsources
                           ,extractedsources
                           ,images 
                      where xtrsrcid = assoc_xtrsrc_id 
                        and imageid = image_id 
                        and xtrsrc_id = 5
                    )
;

