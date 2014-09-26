-- this view is used in Banana to compute columns that are impossible to
-- create with the django orm.
-- It Calculate sigma_min, sigma_max, v_int, eta_int and the max and avg
-- values for lightcurves, all foor all runningcatalogs

-- It starts by getting the extracted source from latest image for a runcat.
-- This is arbitrary, since you have multiple bands. We pick the band with the
-- max integrated flux. Now we have v_int and eta_int.
-- The flux is then devided by the RMS_max and RMS_min of the previous image
-- (stored in newsource.previous_limits_image) to obtain sigma_max and sigma_min.

CREATE VIEW augmented_runningcatalog AS
 SELECT r.id
    /* and finally construct the final table */
       ,r.wm_ra
       ,r.wm_decl
       ,r.wm_uncertainty_ew
       ,r.wm_uncertainty_ns
       ,r.xtrsrc
       ,r.dataset
       ,r.datapoints
       ,matched_assoc.v_int
       ,matched_assoc.eta_int
       ,newsrc_trigger.id as newsource
       ,newsrc_trigger.sigma_rms_max
       ,newsrc_trigger.sigma_rms_min
       ,MAX(e3.f_int) AS lightcurve_max
       ,AVG(e3.f_int) AS lightcurve_avg
    FROM ( /* Select peak flux per runcat at last timestep (over all bands) */
           SELECT a_1.runcat AS runcat_id
               ,MAX(e_1.f_int) AS max_flux
           FROM (SELECT MAX(a_2.id) AS assoc_id
                   FROM assocxtrsource a_2
                        JOIN runningcatalog r_1 ON a_2.runcat = r_1.id
                        JOIN extractedsource e_2 ON a_2.xtrsrc = e_2.id
                        JOIN image i_2 ON e_2.image = i_2.id
                 GROUP BY r_1.id, i_2.band
                ) last_ts_per_band /* maximum timestamps per runcat and band */
                JOIN assocxtrsource a_1 ON a_1.id = last_ts_per_band.assoc_id
                JOIN extractedsource e_1 ON a_1.xtrsrc = e_1.id
         GROUP BY a_1.runcat
        ) last_ts_fmax
        /* Pull out the matching var. indices. at last timestep,
          matched via runcat id, flux val: */
        JOIN assocxtrsource matched_assoc
             ON matched_assoc.runcat = last_ts_fmax.runcat_id
        JOIN extractedsource e
             ON matched_assoc.xtrsrc = e.id AND e.f_int = last_ts_fmax.max_flux
        JOIN runningcatalog r ON r.id = last_ts_fmax.runcat_id
        LEFT JOIN (
            /* Grab newsource /trigger details where possible */
            SELECT  n.id
                   ,n.runcat as rc_id
                   ,(e2.f_int/i.rms_min) as sigma_rms_min
                   ,(e2.f_int/i.rms_max) as sigma_rms_max
            FROM newsource n
            JOIN extractedsource e2 ON e2.id = n.trigger_xtrsrc
            JOIN image i ON i.id = n.previous_limits_image
          ) as newsrc_trigger
          ON newsrc_trigger.rc_id = r.id
        /* and we need to join these again to calculate max and avg for lightcurve */
        JOIN assocxtrsource a2 ON r.id = a2.runcat
        JOIN extractedsource e3 ON a2.xtrsrc = e3.id
        GROUP BY r.id
          ,r.wm_ra
          ,r.wm_decl
          ,r.wm_uncertainty_ew
          ,r.wm_uncertainty_ns
          ,r.xtrsrc
          ,r.dataset
          ,r.datapoints
          ,matched_assoc.v_int
          ,matched_assoc.eta_int
          ,newsrc_trigger.id
          ,newsrc_trigger.sigma_rms_max
          ,newsrc_trigger.sigma_rms_min

;