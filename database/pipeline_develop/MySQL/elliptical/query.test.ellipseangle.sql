/*SET @ra1 = 0;
SET @decl1 = 0;
SET @ra_err1 = 4/3600;
SET @decl_err1 = 3/3600;

SET @ra2 = @ra1 - 3/3600;
SET @decl2 = @decl1 + 4/3600;
SET @ra_err2 = 5/3600;
SET @decl_err2 = 2.5/3600;
*/
SET @ra1 = 30;
SET @decl1 = 89.89;
SET @ra_err1 = 4/3600;
SET @decl_err1 = 3/3600;

SET @ra2 = 29.56593681925041;
SET @decl2 = @decl1 + 4/3600;
SET @ra_err2 = 5/3600;
SET @decl_err2 = 2.5/3600;

SELECT '' as 'source 1:',@ra1,ra2hms(@ra1),@decl1,decl2dms(@decl1);
SELECT '' as 'source 2:',@ra2,ra2hms(@ra2),@decl2,decl2dms(@decl2);

SET @u1 = COS(RADIANS(@decl1))*COS(RADIANS(@ra1));
SET @u2 = COS(RADIANS(@decl1))*SIN(RADIANS(@ra1));
SET @u3 = SIN(RADIANS(@decl1));

SET @n1 = -SIN(RADIANS(@decl1))*COS(RADIANS(@ra1));
SET @n2 = -SIN(RADIANS(@decl1))*SIN(RADIANS(@ra1));
SET @n3 = COS(RADIANS(@decl1));

SET @w1 = SIN(RADIANS(@ra1));
SET @w2 = -COS(RADIANS(@ra1));
SET @w3 = 0;

SET @v1 = COS(RADIANS(@decl2))*COS(RADIANS(@ra2));
SET @v2 = COS(RADIANS(@decl2))*SIN(RADIANS(@ra2));
SET @v3 = SIN(RADIANS(@decl2));

/* north is the northward vector at source 2 */
SET @north1 = -SIN(RADIANS(@decl2))*COS(RADIANS(@ra2));
SET @north2 = -SIN(RADIANS(@decl2))*SIN(RADIANS(@ra2));
SET @north3 = COS(RADIANS(@decl2));

SET @distance_cos = 3600*DEGREES(ACOS(dotProduct(@u1,@u2,@u3,@v1,@v2,@v3)));
SET @distance_sin = 3600 * DEGREES(2 * ASIN(getVectorLength(@v1 - @u1, @v2 - @u2, @v3 - @u3) / 2));

SELECT @distance_cos,@distance_sin;

SET @w1_in_n2 = dotProduct(@w1,@w2,@w3,@north1,@north2,@north3);
SET @zeta2 = ACOS(@w1_in_n2);
SET @phi2 = @zeta2 - PI()/2;

SELECT @w1_in_n2, @zeta2, @phi2, DEGREES(@phi2);

SET @n1_in_n2 = dotProduct(@n1,@n2,@n3,@north1,@north2,@north3);
SET @zeta2_n = ACOS(@n1_in_n2);
SET @phi2_n = @zeta2_n;

SELECT @n1_in_n2, @zeta2_n, @phi2_n, DEGREES(@phi2_n);

