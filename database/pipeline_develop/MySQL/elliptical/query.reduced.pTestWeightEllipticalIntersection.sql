SET @ie1_a = 3; SET @ie1_b = 2;

SET @ie2_h = -4; SET @ie2_k = 2; 
SET @ie2_a = 4; SET @ie2_b = 2; 
SET @ie2_phi = 70;

CALL pTestWeightEllipticalIntersection(@ie1_a
                                         ,@ie1_b
                                         ,@ie2_h
                                         ,@ie2_k
                                         ,@ie2_a
                                         ,@ie2_b
                                         ,@ie2_phi
                                         ,@e2_phi
                                         ,@distance
                                         ,@ready
                                         ,@doIntersect
                                         ,@e1_q1
                                         ,@e1_q3
                                         ,@e1_q6
                                         ,@e2_q1
                                         ,@e2_q2
                                         ,@e2_q3
                                         ,@e2_q4
                                         ,@e2_q5
                                         ,@e2_q6
                                         ,@alpha4
                                         ,@alpha3
                                         ,@alpha2
                                         ,@alpha1
                                         ,@alpha0
                                         ,@delta0
                                         ,@delta1
                                         ,@delta2
                                         ,@eta0
                                         ,@eta1
                                         ,@vartheta0
                                         ,@Nroots
                                         ,@y1_x1
                                         ,@y1_x2
                                         ,@y1
                                         ,@y2_x1
                                         ,@y2_x2
                                         ,@y2
                                         ,@y3_x1
                                         ,@y3_x2
                                         ,@y3
                                         ,@y4_x1
                                         ,@y4_x2
                                         ,@y4
                                         ,@nPoints
                                         ,@Q0_x
                                         ,@Q0_y
                                         ,@Q1_x
                                         ,@Q1_y
                                         ,@Q2_x
                                         ,@Q2_y
                                         ,@Q3_x
                                         ,@Q3_y
                                         ,@P0_x
                                         ,@P0_y
                                         ,@P1_x
                                         ,@P1_y
                                         ,@c1_angle_0
                                         ,@c1_angle_1
                                         ,@e1_theta_0
                                         ,@e1_theta_1
                                         ,@c1_theta_0
                                         ,@c1_theta_1
                                         ,@e2_a_m_x
                                         ,@e2_a_m_y
                                         ,@e2_b_m_x
                                         ,@e2_b_m_y
                                         ,@e2_P0_vec_x
                                         ,@e2_P0_vec_y
                                         ,@e2_P1_vec_x
                                         ,@e2_P1_vec_y
                                         ,@e2_P0_proj_x
                                         ,@e2_P0_proj_y
                                         ,@e2_P1_proj_x
                                         ,@e2_P1_proj_y
                                         ,@m
                                         ,@c
                                         ,@slope
                                         ,@c2_beta_0
                                         ,@c2_beta_1
                                         ,@e2_theta_0
                                         ,@e2_theta_1
                                         ,@c2_theta_0
                                         ,@c2_theta_1
                                         ,@geval
                                         ,@C1_above
                                         ,@C2_above
                                         ,@least_e_area
                                         ,@e_area
                                         ,@weight
                                         ); 

SELECT @ie1_a
      ,@ie1_b
      ,@ie2_h
      ,@ie2_k
      ,@ie2_a
      ,@ie2_b
      ,@ie2_phi
      ,@e2_phi
      ,@distance
      ,@ready
      ,@doIntersect
;

SELECT @e1_q1
      ,@e1_q3
      ,@e1_q6
      ,@e2_q1
      ,@e2_q2
      ,@e2_q3
      ,@e2_q4
      ,@e2_q5
      ,@e2_q6
      ,@alpha3
      ,@alpha2
      ,@alpha1
      ,@alpha0
;

/*
SELECT @delta0
      ,@delta1
      ,@delta2
      ,@eta0
      ,@eta1
      ,@vartheta0
      ,@Nroots
;

SELECT @y1_x1
      ,@y1_x2
      ,@y1
      ,@y2_x1
      ,@y2_x2
      ,@y2
      ,@y3_x1
      ,@y3_x2
      ,@y3
      ,@y4_x1
      ,@y4_x2
      ,@y4
;

SELECT @nPoints
      ,@Q0_x
      ,@Q0_y
      ,@Q1_x
      ,@Q1_y
      ,@Q2_x
      ,@Q2_y
      ,@Q3_x
      ,@Q3_y
      ,@P0_x
      ,@P0_y
      ,@P1_x
      ,@P1_y
;



SELECT @c1_angle_0
      ,DEGREES(@c1_angle_0)
      ,@c1_angle_1
      ,DEGREES(@c1_angle_1)
      ,@e1_theta_0
      ,DEGREES(@e1_theta_0)
      ,@e1_theta_1
      ,DEGREES(@e1_theta_1)
      ,@c1_theta_0
      ,DEGREES(@c1_theta_0)
      ,@c1_theta_1
      ,DEGREES(@c1_theta_1)
;

SELECT @e2_a_m_x
      ,@e2_a_m_y
      ,@e2_b_m_x
      ,@e2_b_m_y
      ,@e2_P0_vec_x
      ,@e2_P0_vec_y
      ,@e2_P1_vec_x
      ,@e2_P1_vec_y
      ,@e2_P0_proj_x
      ,@e2_P0_proj_y
      ,@e2_P1_proj_x
      ,@e2_P1_proj_y
      ,@m
      ,@c
      ,@slope
;

SELECT @c2_beta_0
      ,DEGREES(@c2_beta_0)
      ,@c2_beta_1
      ,DEGREES(@c2_beta_1)
      ,@e2_theta_0
      ,DEGREES(@e2_theta_0)
      ,@e2_theta_1
      ,DEGREES(@e2_theta_1)
      ,@c2_theta_0
      ,DEGREES(@c2_theta_0)
      ,@c2_theta_1
      ,DEGREES(@c2_theta_1)
;
*/

SELECT ROUND(@P0_x,2) AS 'P0_x'
      ,ROUND(@P0_y,2) AS 'P0_y'
      ,ROUND(@P1_x,2) AS 'P1_x'
      ,ROUND(@P1_y,2) AS 'P1_y'
      ,ROUND(DEGREES(@e1_theta_0),2) AS 'e1_theta_0'
      ,ROUND(DEGREES(@e1_theta_1),2) AS 'e1_theta_1'
      ,ROUND(DEGREES(@c1_theta_0),2) AS 'c1_theta_0'
      ,ROUND(DEGREES(@c1_theta_1),2) AS 'c1_theta_1'
      ,' ' 
      ,ROUND(@e2_P0_proj_x,2) AS 'P0_proj_x'
      ,ROUND(@e2_P0_proj_y,2) AS 'P0_proj_y'
      ,ROUND(@e2_P1_proj_x,2) AS 'P1_proj_x'
      ,ROUND(@e2_P1_proj_y,2) AS 'P1_proj_y'
      ,ROUND(DEGREES(@e2_theta_1),2) AS 'e2_theta_1'
      ,ROUND(DEGREES(@e2_theta_0),2) AS 'e2_theta_0'
      ,ROUND(DEGREES(@c2_theta_1),2) AS 'c2_theta_1'
      ,ROUND(DEGREES(@c2_theta_0),2) AS 'c2_theta_0'
;

SELECT @geval
      ,@C1_above
      ,@C2_above
      ,@least_e_area
      ,@e_area
      ,@weight
;

SELECT @ie1_a
      ,@ie1_b
      ,degrees(@e1_theta_0)
      ,degrees(@e1_theta_1)
      ,(@e1_theta_1 - @e1_theta_0)/pi()
      ,degrees(@c1_theta_0)
      ,degrees(@c1_theta_1)
      ,areaEllipticalSector(@ie1_a, @ie1_b, @e1_theta_0, @e1_theta_1) as sector1
      ,areaTriangleInEllipse(@ie1_a, @ie1_b, @c1_theta_0, @c1_theta_1) as triangle1
      ,areaLineEllipticalArc(@ie1_a, @ie1_b, @e1_theta_0,@e1_theta_1,@c1_theta_0, @c1_theta_1) as area1;

SELECT @ie2_a
      ,@ie2_b
      ,degrees(@e2_theta_0)
      ,degrees(@e2_theta_1)
      ,(@e2_theta_0 - @e2_theta_1)/pi()
      ,degrees(@c2_theta_0)
      ,degrees(@c2_theta_1)
      ,areaEllipticalSector(@ie2_a, @ie2_b, @e2_theta_1, @e2_theta_0) as sector2
      ,areaTriangleInEllipse(@ie2_a, @ie2_b, @c2_theta_1, @c2_theta_0) as triangle2
      ,areaLineEllipticalArc(@ie2_a,@ie2_b,@e2_theta_1,@e2_theta_0, @c2_theta_1, @c2_theta_0) as area2
;

CALL pTestAreaIntersection2P(@e2_phi
                            ,@slope
                            ,@C1_above
                            ,@C2_above
                            ,@ie1_a
                            ,@ie1_b
                            ,@e1_theta_0
                            ,@e1_theta_1
                            ,@c1_theta_0
                            ,@c1_theta_1
                            ,@ie2_a
                            ,@ie2_b
                            ,@e2_theta_1
                            ,@e2_theta_0
                            ,@c2_theta_1
                            ,@c2_theta_0
                            ,@geval_area
                            ,@proc_e1_area
                            ,@proc_e2_area
                            );

SELECT ROUND(DEGREES(@e2_phi),2) AS 'phi_2'
      ,@slope
      ,@C1_above
      ,@C2_above
      ,@ie1_a
      ,@ie1_b
      ,ROUND(DEGREES(@e1_theta_0),2) AS 'e1_theta_0'
      ,ROUND(DEGREES(@e1_theta_1),2) AS 'e1_theta_1'
      ,ROUND(DEGREES(@c1_theta_0),2) AS 'c1_theta_0'
      ,ROUND(DEGREES(@c1_theta_1),2) AS 'c1_theta_1'
      ,@ie2_a
      ,@ie2_b
      ,ROUND(DEGREES(@e2_theta_1),2) AS 'e2_theta_1'
      ,ROUND(DEGREES(@e2_theta_0),2) AS 'e2_theta_0'
      ,ROUND(DEGREES(@c2_theta_1),2) AS 'c2_theta_1'
      ,ROUND(DEGREES(@c2_theta_0),2) AS 'c2_theta_0'
      ,@geval_area
      ,@proc_e1_area
      ,@proc_e2_area
;

