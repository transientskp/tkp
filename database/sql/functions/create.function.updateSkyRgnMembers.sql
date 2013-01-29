--DROP FUNCTION updateSkyRgnMembers;

CREATE FUNCTION updateSkyRgnMembers(isky_rgn_id INTEGER) RETURNS DOUBLE
BEGIN

  
  DECLARE inter, inter_sq DOUBLE;
  
  DELETE 
    FROM assocskyrgn
   WHERE assocskyrgn.skyrgn = isky_rgn_id
  ;
  
  SET inter = (SELECT  2.0*SIN(RADIANS(xtr_radius)/2.0)  
                    FROM skyregion 
                   WHERE id=isky_rgn_id);
  
  SET inter_sq = inter*inter;

  INSERT INTO assocskyrgn
  	(
  	runcat
  	,skyrgn
  	,distance_deg
  	) 
  SELECT rc.id as runcat
        ,sky.id as skyrgn
        ,DEGREES(2 * ASIN(SQRT( (rc.x - sky.x) * (rc.x - sky.x)
                       			+ (rc.y - sky.y) * (rc.y - sky.y)
                       			+ (rc.z - sky.z) * (rc.z - sky.z)
                      		  ) / 2 )
          		 )  
    FROM skyregion sky
    	,runningcatalog rc
   WHERE sky.id = isky_rgn_id
     AND rc.dataset = sky.dataset
   	 AND rc.wm_decl BETWEEN sky.centre_decl - sky.xtr_radius
                        AND sky.centre_decl + sky.xtr_radius
 	 AND (  (rc.x - sky.x) * (rc.x - sky.x)
            + (rc.y - sky.y) * (rc.y - sky.y)
            + (rc.z - sky.z) * (rc.z - sky.z)
         ) < inter_sq
  ;
  
  RETURN inter;

END;