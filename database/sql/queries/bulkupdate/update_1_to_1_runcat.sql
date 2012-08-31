UPDATE runningcatalog
   SET datapoints = (SELECT datapoints
					   FROM temprunningcatalog 
					  WHERE temprunningcatalog.runcat = runningcatalog.id
					)
      ,zone = (SELECT zone
       			 FROM temprunningcatalog 
				WHERE temprunningcatalog.runcat = runningcatalog.id
			  )
      ,wm_ra = (SELECT wm_ra
                  FROM temprunningcatalog 
				 WHERE temprunningcatalog.runcat = runningcatalog.id
			   )
      ,wm_decl = (SELECT wm_decl
					FROM temprunningcatalog 
				   WHERE temprunningcatalog.runcat = runningcatalog.id
				 )
      ,wm_ra_err = (SELECT wm_ra_err
					  FROM temprunningcatalog 
					 WHERE temprunningcatalog.runcat = runningcatalog.id
				   )
      ,wm_decl_err = (SELECT wm_decl_err
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog.id
					)
      ,avg_wra = (SELECT avg_wra
					FROM temprunningcatalog
                   WHERE temprunningcatalog.runcat = runningcatalog.id
                 )
      ,avg_wdecl = (SELECT avg_wdecl
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog.id
					)
      ,avg_weight_ra = (SELECT avg_weight_ra
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog.id
					)
      ,avg_weight_decl = (SELECT avg_weight_decl
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog.id
					)
      ,x = (SELECT x
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog.id
					)
      ,y = (SELECT y
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog.id
					)
      ,z = (SELECT z
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog.id
					)
 WHERE EXISTS (SELECT runcat
					FROM temprunningcatalog 
					WHERE temprunningcatalog.runcat = runningcatalog.id
					)
