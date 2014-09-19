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
 SELECT
    -- and finally construct the final table
    r.*,
    a.v_int,
    a.eta_int,
    n.id as newsource,
    e2.f_int / i.rms_max AS sigma_max,
    e2.f_int / i.rms_min AS sigma_min,
    MAX(e3.f_int) AS lightcurve_max,
    AVG(e3.f_int) AS lightcurve_avg
   FROM ( SELECT a_1.runcat AS runcat_id,
          -- second get the peak flux per runcat and band

            max(e_1.f_int) AS max_flux
           FROM ( SELECT max(a_2.id) AS assoc_id
                   -- first get the maximum timestamps per runcat and band
                   FROM assocxtrsource a_2
                     JOIN runningcatalog r_1 ON a_2.runcat = r_1.id
                     JOIN extractedsource e_2 ON a_2.xtrsrc = e_2.id
                     JOIN image i_2 ON e_2.image = i_2.id
                  GROUP BY r_1.id, i_2.band) m  -- m for moment
             JOIN assocxtrsource a_1 ON a_1.id = m.assoc_id
             JOIN extractedsource e_1 ON a_1.xtrsrc = e_1.id
             JOIN image i_1 ON e_1.image = i_1.id
          GROUP BY a_1.runcat) p  -- p for peak flux
     JOIN assocxtrsource a ON a.runcat = p.runcat_id
     JOIN extractedsource e ON a.xtrsrc = e.id AND e.f_int = p.max_flux
     JOIN runningcatalog r ON r.id = p.runcat_id
     LEFT JOIN newsource n ON n.runcat = r.id

     -- we need to join these again to calculate sigma
     LEFT JOIN extractedsource e2 ON e2.id = n.trigger_xtrsrc
     LEFT JOIN image i ON i.id = n.previous_limits_image

     -- and we need to join these again to calculate max and avg for lightcurve
     JOIN assocxtrsource a2 ON r.id = a2.runcat
     JOIN extractedsource e3 ON a2.xtrsrc = e3.id
   GROUP BY r.id, a.v_int, a.eta_int, n.id, e2.f_int, i.rms_max, e2.f_int, i.rms_min
