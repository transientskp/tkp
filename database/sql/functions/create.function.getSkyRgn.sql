--DROP FUNCTION getSkyRgn;

/*
 * This function gets an id for a skyregion,
 * given a pair of central co-ordinates and a radius.
 * 
 * If no matching skyregion is found, a new one is inserted. 
 * In this case we also trigger execution of `updateSkyRgnMembers` for the new
 * skyregion - this performs a simple assocation with current members of the
 * runningcatalog to find sources that should be visible in the new skyregion,
 * and updates the assocskyrgn table accordingly.
 */

CREATE FUNCTION getSkyRgn(idataset INTEGER
                         ,icentre_ra DOUBLE
                         ,icentre_decl DOUBLE
                         ,ixtr_radius DOUBLE
                       ) RETURNS SMALLINT

BEGIN

  DECLARE nskyrgn INT;
  DECLARE oskyrgnid INT;
  DECLARE ox,oy,oz DOUBLE;


  SELECT COUNT(*)
    INTO nskyrgn
    FROM skyregion
   WHERE dataset = idataset
     AND centre_ra = icentre_ra
     AND centre_decl = icentre_decl
     AND xtr_radius = ixtr_radius 
  ;

  IF nskyrgn = 1 THEN
    SELECT id
      INTO oskyrgnid
      FROM skyregion
     WHERE dataset = idataset
	   AND centre_ra = icentre_ra
	   AND centre_decl = icentre_decl
	   AND xtr_radius = ixtr_radius 
    ;
  ELSE
    SELECT NEXT VALUE FOR seq_skyregion INTO oskyrgnid;

    SELECT cart.x,cart.y,cart.z 
      INTO ox,oy,oz
      FROM cartesian(icentre_ra,icentre_decl) cart
      ;

    INSERT INTO skyregion
      (id
      ,dataset
      ,centre_ra
      ,centre_decl
      ,xtr_radius
      ,x
      ,y
      ,z
      ) 
    VALUES
      (oskyrgnid
      ,idataset
      ,icentre_ra
      ,icentre_decl
      ,ixtr_radius
      ,ox
      ,oy
      ,oz
      )
    ;
    
  SELECT updateSkyRgnMembers(oskyrgnid)
  	INTO ox;
    
  END IF;

  RETURN oskyrgnid;

END;