/* These alters should be merged into the create.database.sql file*/
/**
 * Added column to taken into account local rms of source.
 * This differs slightly from i_int_err and i_peak_err,
 * because they were correct with the Condon formula.
 */
ALTER TABLE extractedsources ADD COLUMN local_rms DOUBLE DEFAULT NULL AFTER decl_err;
