UPDATE runningcatalog_flux
   SET f_datapoints = (SELECT f_datapoints
					  FROM temprunningcatalog 
					  WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
					)
      ,avg_f_peak = (SELECT avg_f_peak
       			 FROM temprunningcatalog 
				WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
			  )
      ,avg_f_peak_sq = (SELECT avg_f_peak_sq
                  FROM temprunningcatalog 
				 WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
			   )
      ,avg_f_peak_weight = (SELECT avg_f_peak_weight
					FROM temprunningcatalog 
				   WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
				 )
      ,avg_weighted_f_peak = (SELECT avg_weighted_f_peak
					  FROM temprunningcatalog 
					 WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
				   )
      ,avg_weighted_f_peak_sq = (SELECT avg_weighted_f_peak_sq
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
					)
      ,avg_f_int = (SELECT avg_f_int
       			 FROM temprunningcatalog 
				WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
			  )
      ,avg_f_int_sq = (SELECT avg_f_int_sq
                  FROM temprunningcatalog 
				 WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
			   )
      ,avg_f_int_weight = (SELECT avg_f_int_weight
					FROM temprunningcatalog 
				   WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
				 )
      ,avg_weighted_f_int = (SELECT avg_weighted_f_int
					  FROM temprunningcatalog 
					 WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
				   )
      ,avg_weighted_f_int_sq = (SELECT avg_weighted_f_int_sq
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
					)
 WHERE EXISTS (SELECT runcat
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog_flux.runcat
                      AND temprunningcatalog.band = runningcatalog_flux.band
                      AND temprunningcatalog.stokes = runningcatalog_flux.stokes
					)
