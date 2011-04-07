/*
SET @ie1_a = 3; SET @ie1_b = 2;

SET @ie2_h = 1; SET @ie2_k = 2; 
SET @ie2_a = 4; SET @ie2_b = 2; 
SET @ie2_phi = 30;
*/
SET @ie1_a = 4; SET @ie1_b = 3;

SET @ie2_h = 5.4785411173934; SET @ie2_k = 4.1767203682579e-06; 
SET @ie2_a = 5; SET @ie2_b = 2.5; 
SET @ie2_phi = 0;

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
                                         ,@doContain
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
                                         ,@e1_m_0
                                         ,@e1_m_1
                                         ,@e1_m_2
                                         ,@e2_m_0
                                         ,@e2_m_1
                                         ,@e2_m_2
                                         ,@R0_x
                                         ,@R0_y
                                         ,@R1_x
                                         ,@R1_y
                                         ,@R2_x
                                         ,@R2_y
                                         ,@R3_x
                                         ,@R3_y
                                         ,@P0_x
                                         ,@P0_y
                                         ,@P1_x
                                         ,@P1_y
                                         ,@P2_x
                                         ,@P2_y
                                         ,@P3_x
                                         ,@P3_y
                                         ,@c1_angle_0
                                         ,@c1_angle_1
                                         ,@c1_angle_2
                                         ,@c1_angle_3
                                         ,@c1_theta_0
                                         ,@c1_theta_1
                                         ,@c1_theta_2
                                         ,@c1_theta_3
                                         ,@e1_theta_0
                                         ,@e1_theta_1
                                         ,@e1_theta_2
                                         ,@e1_theta_3
                                         ,@e2_a_m_x
                                         ,@e2_a_m_y
                                         ,@e2_b_m_x
                                         ,@e2_b_m_y
                                         ,@e2_P0_vec_x
                                         ,@e2_P0_vec_y
                                         ,@e2_P1_vec_x
                                         ,@e2_P1_vec_y
                                         ,@e2_P2_vec_x
                                         ,@e2_P2_vec_y
                                         ,@e2_P3_vec_x
                                         ,@e2_P3_vec_y
                                         ,@e2_P0_proj_x
                                         ,@e2_P0_proj_y
                                         ,@e2_P1_proj_x
                                         ,@e2_P1_proj_y
                                         ,@e2_P2_proj_x
                                         ,@e2_P2_proj_y
                                         ,@e2_P3_proj_x
                                         ,@e2_P3_proj_y
                                         ,@m
                                         ,@c
                                         ,@slope
                                         ,@c2_beta_0
                                         ,@c2_beta_1
                                         ,@c2_beta_2
                                         ,@c2_beta_3
                                         ,@c2_theta_0
                                         ,@c2_theta_1
                                         ,@c2_theta_2
                                         ,@c2_theta_3
                                         ,@e2_theta_0
                                         ,@e2_theta_1
                                         ,@e2_theta_2
                                         ,@e2_theta_3
                                         ,@geval
                                         ,@C1_above
                                         ,@C2_above
                                         ,@least_e_area
                                         ,@e_area1
                                         ,@e_area2
                                         ,@e_area3
                                         ,@e_area4
                                         ,@e_area
                                         ,@e_triangles
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


SELECT @delta0
      ,@delta1
      ,@delta2
      ,@eta0
      ,@eta1
      ,@vartheta0
      ,@Nroots
      ,@doContain
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
      ,@e1_m_0
      ,@e1_m_1
      ,@e1_m_2
      ,@e2_m_0
      ,@e2_m_1
      ,@e2_m_2
;

SELECT @R0_x
      ,@R0_y
      ,@R1_x
      ,@R1_y
      ,@R2_x
      ,@R2_y
      ,@R3_x
      ,@R3_y
      ,@P0_x
      ,@P0_y
      ,@P1_x
      ,@P1_y
      ,@P2_x
      ,@P2_y
      ,@P3_x
      ,@P3_y
;

SELECT @c1_angle_0
      ,DEGREES(@c1_angle_0)
      ,@c1_angle_1
      ,DEGREES(@c1_angle_1)
      ,@c1_angle_2
      ,DEGREES(@c1_angle_2)
      ,@c1_angle_3
      ,DEGREES(@c1_angle_3)
;

SELECT @c1_theta_0
      ,DEGREES(@c1_theta_0)
      ,@c1_theta_1
      ,DEGREES(@c1_theta_1)
      ,@c1_theta_2
      ,DEGREES(@c1_theta_2)
      ,@c1_theta_3
      ,DEGREES(@c1_theta_3)
;

SELECT @e1_theta_0
      ,DEGREES(@e1_theta_0)
      ,@e1_theta_1
      ,DEGREES(@e1_theta_1)
      ,@e1_theta_2
      ,DEGREES(@e1_theta_2)
      ,@e1_theta_3
      ,DEGREES(@e1_theta_3)
;

SELECT @e2_a_m_x
      ,@e2_a_m_y
      ,@e2_b_m_x
      ,@e2_b_m_y
      ,@e2_P0_vec_x
      ,@e2_P0_vec_y
      ,@e2_P1_vec_x
      ,@e2_P1_vec_y
      ,@e2_P2_vec_x
      ,@e2_P2_vec_y
      ,@e2_P3_vec_x
      ,@e2_P3_vec_y
;

SELECT @e2_P0_proj_x
      ,@e2_P0_proj_y
      ,@e2_P1_proj_x
      ,@e2_P1_proj_y
      ,@e2_P2_proj_x
      ,@e2_P2_proj_y
      ,@e2_P3_proj_x
      ,@e2_P3_proj_y
      ,@m
      ,@c
      ,@slope
;

SELECT @c2_beta_0
      ,DEGREES(@c2_beta_0)
      ,@c2_beta_1
      ,DEGREES(@c2_beta_1)
      ,@c2_beta_2
      ,DEGREES(@c2_beta_2)
      ,@c2_beta_3
      ,DEGREES(@c2_beta_3)
;

SELECT @c2_theta_0
      ,DEGREES(@c2_theta_0)
      ,@c2_theta_1
      ,DEGREES(@c2_theta_1)
      ,@c2_theta_2
      ,DEGREES(@c2_theta_2)
      ,@c2_theta_3
      ,DEGREES(@c2_theta_3)
;

SELECT @e2_theta_0
      ,DEGREES(@e2_theta_0)
      ,@e2_theta_1
      ,DEGREES(@e2_theta_1)
      ,@e2_theta_2
      ,DEGREES(@e2_theta_2)
      ,@e2_theta_3
      ,DEGREES(@e2_theta_3)
;

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
      ,@e_area1
      ,@e_area2
      ,@e_area3
      ,@e_area4
      ,@e_area
      ,@e_triangles
      ,@weight
;


SET @x1_arg = (-@e1_q1 * @y1 * @y1 - @e1_q3) / @e1_q6;
SELECT @x1_arg;
SET @x1=sqrt(@x1_arg);
SET @x2=-@x1;
SET @abc_a = @e2_q6;SET @abc_b = @e2_q4 * @y1 + @e2_q5;SET @abc_c = @e2_q1 * @y1 * @y1 + @e2_q2 * @y1 + @e2_q3;
SELECT ABS(@abc_c + @abc_b * @x1 + @abc_a * @x1 * @x1);

SELECT areaLineEllipticalArc(@ie1_a,@ie1_b,@e1_theta_1,@e1_theta_2,@c1_theta_1,@c1_theta_2) AS 'E1: P1 -> P2'
      ,areaLineEllipticalArc(@ie1_a,@ie1_b,@e1_theta_3,@e1_theta_0,@c1_theta_3,@c1_theta_0) AS 'E1: P3 -> P0'
      ,areaLineEllipticalArc(@ie2_a,@ie2_b,@e2_theta_0,@e2_theta_1,@c2_theta_0,@c2_theta_1) AS 'E2: P0 -> P1'
      ,areaLineEllipticalArc(@ie2_a,@ie2_b,@e2_theta_2,@e2_theta_3,@c2_theta_2,@c2_theta_3) AS 'E2: P2 -> P3'
      ,areaLineEllipticalArc(@ie1_a,@ie1_b,@e1_theta_1,@e1_theta_2,@c1_theta_1,@c1_theta_2) 
      + areaLineEllipticalArc(@ie1_a,@ie1_b,@e1_theta_3,@e1_theta_0,@c1_theta_3,@c1_theta_0) 
      + areaLineEllipticalArc(@ie2_a,@ie2_b,@e2_theta_0,@e2_theta_1,@c2_theta_0,@c2_theta_1) 
      + areaLineEllipticalArc(@ie2_a,@ie2_b,@e2_theta_2,@e2_theta_3,@c2_theta_2,@c2_theta_3) AS area
;
      

/*
SELECT @ie1_a
      ,@ie1_b
      ,degrees(@e1_theta_0)
      ,degrees(@e1_theta_1)
      ,(@e1_theta_1 - @e1_theta_0)/pi()
      ,degrees(@c1_theta_0)
      ,degrees(@c1_theta_1)
      ,areaEllipticalSector(@ie1_a, @ie1_b, @e1_theta_0, @e1_theta_1) as sector1
      ,areaTriangleInEllipse(@ie1_a, @ie1_b, @c1_theta_0, @c1_theta_1) as triangle1
      ,areaLineEllipticalArc(@ie1_a, @ie1_b, @e1_theta_0,@e1_theta_1,@c1_theta_0, @c1_theta_1) as area1
      ,complementAreaLineEllipticalArc(@ie1_a, @ie1_b, @e1_theta_0,@e1_theta_1,@c1_theta_0, @c1_theta_1) as 'comp_area1'
;

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
      ,complementAreaLineEllipticalArc(@ie2_a,@ie2_b,@e2_theta_1,@e2_theta_0, @c2_theta_1, @c2_theta_0) as 'comp_area2'
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

SELECT getWeightEllipticalIntersection(@ie1_a
                                      ,@ie1_b
                                      ,@ie2_h
                                      ,@ie2_k
                                      ,@ie2_a
                                      ,@ie2_b
                                      ,@ie2_phi
                                      )
       AS weight
;
*/

