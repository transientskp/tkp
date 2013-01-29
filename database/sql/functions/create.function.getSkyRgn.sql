--DROP FUNCTION getSkyRgn;

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