--DROP FUNCTION updateSkyRgnMembers;

/*
 * This function performs a simple distance-check against current members of the
 * runningcatalog to find sources that should be visible in the given skyregion,
 * and updates the assocskyrgn table accordingly.
 * 
 * Any previous entries in assocskyrgn relating to this skyregion are 
 * deleted first.
 * 
 * Note 1. We use the variable 'inter' to cache the extraction_radius as transformed
 * onto the unit sphere, so this does not have to be recalculated for every
 * comparison.
 * 
 * 
 * Note 2. (To Do:) This distance check could be made more efficient by 
 * restricting to a range of RA values, as we do with the Dec. 
 * However, this optimization is complicated by the meridian wrap-around issue. 
 * 
 */
CREATE FUNCTION updateSkyRgnMembers(isky_rgn_id INTEGER)
RETURNS DOUBLE PRECISION

{% ifdb postgresql %}
AS $$
  DECLARE inter DOUBLE PRECISION;
  DECLARE inter_sq DOUBLE PRECISION;
BEGIN
  DELETE
    FROM assocskyrgn
   WHERE assocskyrgn.skyrgn = isky_rgn_id
  ;

  inter := (SELECT  2.0 * SIN(RADIANS(xtr_radius) / 2.0)
                    FROM skyregion
                   WHERE id=isky_rgn_id);

  inter_sq := inter * inter;
{% endifdb %}


{% ifdb monetdb %}
BEGIN
  DECLARE inter DOUBLE PRECISION;
  DECLARE inter_sq DOUBLE PRECISION;

  DELETE
    FROM assocskyrgn
   WHERE assocskyrgn.skyrgn = isky_rgn_id
  ;

  SET inter = (SELECT  2.0*SIN(RADIANS(xtr_radius)/2.0)
                    FROM skyregion
                   WHERE id=isky_rgn_id);

  SET inter_sq = inter*inter;
{% endifdb %}


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

{% ifdb postgresql %}
$$ LANGUAGE plpgsql;
{% endifdb %}