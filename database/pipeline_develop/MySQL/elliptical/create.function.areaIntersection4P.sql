DROP FUNCTION IF EXISTS areaIntersection4P;

DELIMITER //

CREATE FUNCTION areaIntersection4P(ie1_a DOUBLE
                                  ,ie1_b DOUBLE
                                  ,iQ0_x DOUBLE
                                  ,iQ0_y DOUBLE
                                  ,iQ1_x DOUBLE
                                  ,iQ1_y DOUBLE
                                  ,iQ2_x DOUBLE
                                  ,iQ2_y DOUBLE
                                  ,iQ3_x DOUBLE
                                  ,iQ3_y DOUBLE
                                  ,ie2_h DOUBLE
                                  ,ie2_k DOUBLE
                                  ,ie2_a DOUBLE
                                  ,ie2_b DOUBLE
                                  ,ie2_phi DOUBLE
                                  ) RETURNS DOUBLE
DETERMINISTIC
BEGIN

  DECLARE c1_angle_0, c1_angle_1, c1_angle_2, c1_angle_3 DOUBLE;
  DECLARE c1_theta_0, c1_theta_1, c1_theta_2, c1_theta_3 DOUBLE;
  DECLARE P0_x, P0_y, P1_x, P1_y, P2_x, P2_y, P3_x, P3_y DOUBLE;
  DECLARE e1_theta_0, e1_theta_1, e1_theta_2, e1_theta_3 DOUBLE;
  DECLARE e2_theta_0, e2_theta_1, e2_theta_2, e2_theta_3 DOUBLE;
  DECLARE e2_a_m_x, e2_a_m_y, e2_b_m_x, e2_b_m_y DOUBLE;
  DECLARE e2_P0_vec_x, e2_P0_vec_y, e2_P1_vec_x, e2_P1_vec_y DOUBLE;
  DECLARE e2_P2_vec_x, e2_P2_vec_y, e2_P3_vec_x, e2_P3_vec_y DOUBLE;
  DECLARE e2_P0_proj_x, e2_P0_proj_y, e2_P1_proj_x, e2_P1_proj_y DOUBLE;
  DECLARE e2_P2_proj_x, e2_P2_proj_y, e2_P3_proj_x, e2_P3_proj_y DOUBLE;
  DECLARE c2_beta_0, c2_beta_1, c2_beta_2, c2_beta_3 DOUBLE;
  DECLARE c2_theta_0, c2_theta_1, c2_theta_2, c2_theta_3 DOUBLE;
  DECLARE e_area1, e_area2, e_area3, e_area4, e_area, e_triangles DOUBLE;

  DECLARE oc1_angle_0, oc1_angle_1, oc1_angle_2, oc1_angle_3 DOUBLE;
  DECLARE oc1_theta_0, oc1_theta_1, oc1_theta_2, oc1_theta_3 DOUBLE;
  DECLARE oP0_x, oP0_y, oP1_x, oP1_y, oP2_x, oP2_y, oP3_x, oP3_y DOUBLE;
  DECLARE oe1_theta_0, oe1_theta_1, oe1_theta_2, oe1_theta_3 DOUBLE;
  DECLARE oe2_theta_0, oe2_theta_1, oe2_theta_2, oe2_theta_3 DOUBLE;
  DECLARE oe2_a_m_x, oe2_a_m_y, oe2_b_m_x, oe2_b_m_y DOUBLE;
  DECLARE oe2_P0_vec_x, oe2_P0_vec_y, oe2_P1_vec_x, oe2_P1_vec_y DOUBLE;
  DECLARE oe2_P2_vec_x, oe2_P2_vec_y, oe2_P3_vec_x, oe2_P3_vec_y DOUBLE;
  DECLARE oe2_P0_proj_x, oe2_P0_proj_y, oe2_P1_proj_x, oe2_P1_proj_y DOUBLE;
  DECLARE oe2_P2_proj_x, oe2_P2_proj_y, oe2_P3_proj_x, oe2_P3_proj_y DOUBLE;
  DECLARE oc2_beta_0, oc2_beta_1, oc2_beta_2, oc2_beta_3 DOUBLE;
  DECLARE oc2_theta_0, oc2_theta_1, oc2_theta_2, oc2_theta_3 DOUBLE;
  DECLARE oe_area1, oe_area2, oe_area3, oe_area4, oe_area, oe_triangles DOUBLE;

  SET c1_angle_0 = ATAN((ie1_a * iQ0_y) / (ie1_b * iQ0_x));
  IF iQ0_x < 0 THEN 
    IF iQ0_y < 0 THEN
      SET c1_angle_0 = -PI() + c1_angle_0;
    ELSE 
      SET c1_angle_0 = PI() + c1_angle_0;
    END IF;
  END IF;
  SET oc1_angle_0 = c1_angle_0;
  
  SET c1_angle_1 = ATAN((ie1_a * iQ1_y) / (ie1_b * iQ1_x));
  IF iQ1_x < 0 THEN
    IF iQ1_y < 0 THEN
      SET c1_angle_1 = -PI() + c1_angle_1;
    ELSE
      SET c1_angle_1 = PI() + c1_angle_1;
    END IF;
  END IF;
  SET oc1_angle_1 = c1_angle_1;
  
  SET c1_angle_2 = ATAN((ie1_a * iQ2_y) / (ie1_b * iQ2_x));
  IF iQ2_x < 0 THEN
    IF iQ2_y < 0 THEN
      SET c1_angle_2 = -PI() + c1_angle_2;
    ELSE
      SET c1_angle_2 = PI() + c1_angle_2;
    END IF;
  END IF;
  SET oc1_angle_2 = c1_angle_2;
  
  SET c1_angle_3 = ATAN((ie1_a * iQ3_y) / (ie1_b * iQ3_x));
  IF iQ3_x < 0 THEN
    IF iQ3_y < 0 THEN
      SET c1_angle_3 = -PI() + c1_angle_3;
    ELSE
      SET c1_angle_3 = PI() + c1_angle_3;
    END IF;
  END IF;
  SET oc1_angle_3 = c1_angle_3;
  
  CALL pTestSortAngles(c1_angle_0
                      ,c1_angle_1
                      ,c1_angle_2
                      ,c1_angle_3
                      ,iQ0_x
                      ,iQ0_y
                      ,iQ1_x
                      ,iQ1_y
                      ,iQ2_x
                      ,iQ2_y
                      ,iQ3_x
                      ,iQ3_y
                      ,c1_theta_0
                      ,c1_theta_1
                      ,c1_theta_2
                      ,c1_theta_3
                      ,P0_x
                      ,P0_y
                      ,P1_x
                      ,P1_y
                      ,P2_x
                      ,P2_y
                      ,P3_x
                      ,P3_y
                      );
  
  SET oc1_theta_0 = c1_theta_0;
  SET oc1_theta_1 = c1_theta_1;
  SET oc1_theta_2 = c1_theta_2;
  SET oc1_theta_3 = c1_theta_3;
  SET oP0_x = P0_x;
  SET oP0_y = P0_y;
  SET oP1_x = P1_x;
  SET oP1_y = P1_y;
  SET oP2_x = P2_x;
  SET oP2_y = P2_y;
  SET oP3_x = P3_x;
  SET oP3_y = P3_y;

  SET e1_theta_0 = ATAN(P0_y / P0_x);
  IF P0_x < 0 THEN
    IF P0_y < 0 THEN
      SET e1_theta_0 = -PI() + e1_theta_0;
    ELSE
      SET e1_theta_0 = PI() + e1_theta_0;
    END IF;
  END IF;
  SET oe1_theta_0 = e1_theta_0;
  
  SET e1_theta_1 = ATAN(P1_y / P1_x);
  IF P1_x < 0 THEN
    IF P1_y < 0 THEN
      SET e1_theta_1 = -PI() + e1_theta_1;
    ELSE
      SET e1_theta_1 = PI() + e1_theta_1;
    END IF;
  END IF;
  SET oe1_theta_1 = e1_theta_1;

  SET e1_theta_2 = ATAN(P2_y / P2_x);
  IF P2_x < 0 THEN
    IF P2_y < 0 THEN
      SET e1_theta_2 = -PI() + e1_theta_2;
    ELSE
      SET e1_theta_2 = PI() + e1_theta_2;
    END IF;
  END IF;
  SET oe1_theta_2 = e1_theta_2;

  SET e1_theta_3 = ATAN(P3_y / P3_x);
  IF P3_x < 0 THEN
    IF P3_y < 0 THEN
      SET e1_theta_3 = -PI() + e1_theta_3;
    ELSE
      SET e1_theta_3 = PI() + e1_theta_3;
    END IF;
  END IF;
  SET oe1_theta_3 = e1_theta_3;

  IF ABS(TAN(ie2_phi)) < 1E+10 THEN
    SET e2_a_m_x = 1;
    SET e2_a_m_y = TAN(ie2_phi);
    SET e2_b_m_x = -TAN(ie2_phi);
    SET e2_b_m_y = 1;
  ELSE
    SET e2_a_m_x = 0;
    SET e2_a_m_y = 1;
    SET e2_b_m_x = -1;
    SET e2_b_m_y = 0;
  END IF;
  SET oe2_a_m_x = e2_a_m_x;
  SET oe2_a_m_y = e2_a_m_y;
  SET oe2_b_m_x = e2_b_m_x;
  SET oe2_b_m_y = e2_b_m_y;
  
  SET e2_P0_vec_x = P0_x - ie2_h;
  SET e2_P0_vec_y = P0_y - ie2_k;
  SET oe2_P0_vec_x = e2_P0_vec_x;
  SET oe2_P0_vec_y = e2_P0_vec_y;
  SET e2_P0_proj_x =   (e2_P0_vec_x * e2_a_m_x + e2_P0_vec_y * e2_a_m_y)
                     / SQRT(e2_a_m_x * e2_a_m_x + e2_a_m_y * e2_a_m_y);
  SET e2_P0_proj_y =   (e2_P0_vec_x * e2_b_m_x + e2_P0_vec_y * e2_b_m_y)
                     / SQRT(e2_b_m_x * e2_b_m_x + e2_b_m_y * e2_b_m_y);
  SET oe2_P0_proj_x = e2_P0_proj_x;
  SET oe2_P0_proj_y = e2_P0_proj_y;
  SET c2_beta_0 = ATAN( (ie2_a * (e2_P0_vec_x * e2_b_m_x + e2_P0_vec_y * e2_b_m_y))
                      / (ie2_b * (e2_P0_vec_x * e2_a_m_x + e2_P0_vec_y * e2_a_m_y))
                      );
  SET oc2_beta_0 = c2_beta_0;
  SET e2_theta_0 = ATAN(e2_P0_proj_y / e2_P0_proj_x);
  IF e2_P0_proj_x < 0 THEN
    IF e2_P0_proj_y < 0 THEN
      SET c2_beta_0 = -PI() + c2_beta_0;
      SET e2_theta_0 = -PI() + e2_theta_0;
    ELSE
      SET c2_beta_0 = PI() + c2_beta_0;
      SET e2_theta_0 = PI() + e2_theta_0;
    END IF;
  END IF;
  SET c2_theta_0 = c2_beta_0;
  SET oc2_theta_0 = c2_theta_0;
  SET oe2_theta_0 = e2_theta_0;

  SET e2_P1_vec_x = P1_x - ie2_h;
  SET e2_P1_vec_y = P1_y - ie2_k;
  SET oe2_P1_vec_x = e2_P1_vec_x;
  SET oe2_P1_vec_y = e2_P1_vec_y;
  SET e2_P1_proj_x =   (e2_P1_vec_x * e2_a_m_x + e2_P1_vec_y * e2_a_m_y)
                     / SQRT(e2_a_m_x * e2_a_m_x + e2_a_m_y * e2_a_m_y);
  SET e2_P1_proj_y =   (e2_P1_vec_x * e2_b_m_x + e2_P1_vec_y * e2_b_m_y)
                     / SQRT(e2_b_m_x * e2_b_m_x + e2_b_m_y * e2_b_m_y);
  SET oe2_P1_proj_x = e2_P1_proj_x;
  SET oe2_P1_proj_y = e2_P1_proj_y;
  SET c2_beta_1 = ATAN( (ie2_a * (e2_P1_vec_x * e2_b_m_x + e2_P1_vec_y * e2_b_m_y))
                      / (ie2_b * (e2_P1_vec_x * e2_a_m_x + e2_P1_vec_y * e2_a_m_y))
                      );
  SET oc2_beta_1 = c2_beta_1;
  SET e2_theta_1 = ATAN(e2_P1_proj_y / e2_P1_proj_x);
  IF e2_P1_proj_x < 0 THEN
    IF e2_P1_proj_y < 0 THEN
      SET c2_beta_1 = -PI() + c2_beta_1;
      SET e2_theta_1 = -PI() + e2_theta_1;
    ELSE
      SET c2_beta_1 = PI() + c2_beta_1;
      SET e2_theta_1 = PI() + e2_theta_1;
    END IF;
  END IF;
  SET c2_theta_1 = c2_beta_1;
  SET oc2_theta_1 = c2_theta_1;
  SET oe2_theta_1 = e2_theta_1;

  SET e2_P2_vec_x = P2_x - ie2_h;
  SET e2_P2_vec_y = P2_y - ie2_k;
  SET oe2_P2_vec_x = e2_P2_vec_x;
  SET oe2_P2_vec_y = e2_P2_vec_y;
  SET e2_P2_proj_x =   (e2_P2_vec_x * e2_a_m_x + e2_P2_vec_y * e2_a_m_y)
                     / SQRT(e2_a_m_x * e2_a_m_x + e2_a_m_y * e2_a_m_y);
  SET e2_P2_proj_y =   (e2_P2_vec_x * e2_b_m_x + e2_P2_vec_y * e2_b_m_y)
                     / SQRT(e2_b_m_x * e2_b_m_x + e2_b_m_y * e2_b_m_y);
  SET oe2_P2_proj_x = e2_P2_proj_x;
  SET oe2_P2_proj_y = e2_P2_proj_y;
  SET c2_beta_2 = ATAN( (ie2_a * (e2_P2_vec_x * e2_b_m_x + e2_P2_vec_y * e2_b_m_y))
                      / (ie2_b * (e2_P2_vec_x * e2_a_m_x + e2_P2_vec_y * e2_a_m_y))
                      );
  SET oc2_beta_2 = c2_beta_2;
  SET e2_theta_2 = ATAN(e2_P2_proj_y / e2_P2_proj_x);
  IF e2_P2_proj_x < 0 THEN
    IF e2_P2_proj_y < 0 THEN
      SET c2_beta_2 = -PI() + c2_beta_2;
      SET e2_theta_2 = -PI() + e2_theta_2;
    ELSE
      SET c2_beta_2 = PI() + c2_beta_2;
      SET e2_theta_2 = PI() + e2_theta_2;
    END IF;
  END IF;
  SET c2_theta_2 = c2_beta_2;
  SET oc2_theta_2 = c2_theta_2;
  SET oe2_theta_2 = e2_theta_2;

  SET e2_P3_vec_x = P3_x - ie2_h;
  SET e2_P3_vec_y = P3_y - ie2_k;
  SET oe2_P3_vec_x = e2_P3_vec_x;
  SET oe2_P3_vec_y = e2_P3_vec_y;
  SET e2_P3_proj_x =   (e2_P3_vec_x * e2_a_m_x + e2_P3_vec_y * e2_a_m_y)
                     / SQRT(e2_a_m_x * e2_a_m_x + e2_a_m_y * e2_a_m_y);
  SET e2_P3_proj_y =   (e2_P3_vec_x * e2_b_m_x + e2_P3_vec_y * e2_b_m_y)
                     / SQRT(e2_b_m_x * e2_b_m_x + e2_b_m_y * e2_b_m_y);
  SET oe2_P3_proj_x = e2_P3_proj_x;
  SET oe2_P3_proj_y = e2_P3_proj_y;
  SET c2_beta_3 = ATAN( (ie2_a * (e2_P3_vec_x * e2_b_m_x + e2_P3_vec_y * e2_b_m_y))
                      / (ie2_b * (e2_P3_vec_x * e2_a_m_x + e2_P3_vec_y * e2_a_m_y))
                      );
  SET oc2_beta_3 = c2_beta_3;
  SET e2_theta_3 = ATAN(e2_P3_proj_y / e2_P3_proj_x);
  IF e2_P3_proj_x < 0 THEN
    IF e2_P3_proj_y < 0 THEN
      SET c2_beta_3 = -PI() + c2_beta_3;
      SET e2_theta_3 = -PI() + e2_theta_3;
    ELSE
      SET c2_beta_3 = PI() + c2_beta_3;
      SET e2_theta_3 = PI() + e2_theta_3;
    END IF;
  END IF;
  SET c2_theta_3 = c2_beta_3;
  SET oc2_theta_3 = c2_theta_3;
  SET oe2_theta_3 = e2_theta_3;

  SET e_area1 = areaLineEllipticalArc(ie1_a,ie1_b,e1_theta_1,e1_theta_2,c1_theta_1,c1_theta_2);
  SET e_area2 = areaLineEllipticalArc(ie1_a,ie1_b,e1_theta_3,e1_theta_0,c1_theta_3,c1_theta_0);
  SET e_area3 = areaLineEllipticalArc(ie2_a,ie2_b,e2_theta_0,e2_theta_1,c2_theta_0,c2_theta_1);
  SET e_area4 = areaLineEllipticalArc(ie2_a,ie2_b,e2_theta_2,e2_theta_3,c2_theta_2,c2_theta_3);
  
  SET e_area =  e_area1 + e_area2 + e_area3 + e_area4;
  SET oe_area1 = e_area1;
  SET oe_area2 = e_area2;
  SET oe_area3 = e_area3;
  SET oe_area4 = e_area4;
  SET oe_area = e_area;
  
  SET e_triangles =   ABS((P2_x - P0_x) * (P1_y - P0_y) - (P1_x - P0_x) * (P2_y - P0_y)) / 2
                    + ABS((P0_x - P2_x) * (P3_y - P2_y) - (P3_x - P2_x) * (P0_y - P2_y)) / 2;
  SET oe_triangles = e_triangles;
  
  RETURN e_area + e_triangles;

END;
//

