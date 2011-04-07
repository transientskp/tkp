/**
 * This table based on definitions in 
 * Helmboldt et al. (2008) ApJSS, 174:313
 * param_N:         Number of frequencies with measured flux densities
 * F74:             VLSS 74 MHz flux density
 * alpha_gt_300:    Slope of power-law fit at {nu} > 300 MHz
 * F_ext:           Extrapolated 74 MHz flux density using alp>300
 * param_A:         Equation 1 "A" parameter value (1)
 * param_B:         Equation 1 "B" parameter value (1)
 * param_C:         Equation 1 "C" parameter value (1)
 * param_D:         Equation 1 "D" parameter value (1)
 * param_rms_diff:  The rms difference between observed and 
 *                  fitted Y values (2)
 * ---------------------------------------------------------------------
 * Note (1):    Derived using a fit to the data for all sources with 
 *              Num {>=} 8; for sources where a simple linear fit gives 
 *              a quantitatively better fit (see text), 
 *              only the A and B parameters are listed.
 * Note (2):    Equal to log F_{nu}_; see equation (1) and text.
 * ---------------------------------------------------------------------
 */
CREATE TABLE spectralparameters (
  spectral_paramsid INT NOT NULL AUTO_INCREMENT,
  param_N INT NOT NULL,
  F74 DOUBLE NULL,
  alpha_gt_300 DOUBLE NULL,
  F_ext DOUBLE NULL,
  param_A DOUBLE NULL,
  param_B DOUBLE NULL,
  param_C DOUBLE NULL,
  param_D DOUBLE NULL,
  param_rms_diff DOUBLE NULL,
  PRIMARY KEY (spectral_paramsid),
  INDEX (param_N),
  INDEX (alpha_gt_300),
  INDEX (F_ext),
  INDEX (param_rms_diff)
) ENGINE=InnoDB;
