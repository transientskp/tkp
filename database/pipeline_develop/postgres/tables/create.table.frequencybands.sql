/**
 * This table contains the frequencies at which the extracted sources 
 * were detected. It might also be preloaded with the frequencies 
 * at which the stokes of the catalog sources were measured.
 */
CREATE TABLE frequencybands (
  freqbandid SERIAL PRIMARY KEY,
  freq_central double precision DEFAULT NULL,
  freq_low double precision DEFAULT NULL,
  freq_high double precision DEFAULT NULL
);
