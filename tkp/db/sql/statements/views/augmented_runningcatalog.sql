-- this view is used in Banana to compute columns that are impossible to
-- create with the django orm

CREATE VIEW augmented_runningcatalog
    AS SELECT
        -- and finally construct the final table
        r.*,
        a.v_int v_int,
        a.eta_int eta_int,
        (e2.f_int / i.rms_max) as sigma_max,
        (e2.f_int / i.rms_min) as sigma_min
    FROM
        -- second get the peak flux per runcat and band
        (SELECT
            a.runcat as runcat_id,
            max(e.f_int) as max_flux
        FROM
            -- first get the maximum timestamps per runcat and band
            (SELECT
                a.runcat runcat_id,
                i.band band,
                max(i.taustart_ts) moment
            FROM
                assocxtrsource a
                    JOIN extractedsource as e ON a.xtrsrc = e.id
                    JOIN image as i ON e.image = i.id
            GROUP BY
                runcat_id, band
            ) as m -- m for moment
        JOIN assocxtrsource a ON a.runcat = m.runcat_id
        JOIN extractedsource as e ON a.xtrsrc = e.id
        JOIN image as i ON e.image = i.id AND i.band = m.band AND m.moment = i.taustart_ts
        GROUP BY
           runcat
        ) as p -- p for peak flux

    JOIN assocxtrsource a ON a.runcat = p.runcat_id
    JOIN extractedsource as e ON a.xtrsrc = e.id and e.f_int = p.max_flux
    JOIN runningcatalog as r ON r.id = p.runcat_id
    LEFT OUTER JOIN newsource as n on n.runcat = r.id

    -- we need to join these again to calculate sigma
    LEFT JOIN extractedsource as e2 ON e2.id = n.trigger_xtrsrc
    LEFT JOIN image as i ON i.id = n.previous_limits_image;