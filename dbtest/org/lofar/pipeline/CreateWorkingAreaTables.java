package org.lofar.pipeline;

import java.sql.*;

/**
 * This class creates all the tables in the working area.
 */
public class CreateWorkingAreaTables {
	
	private static final String createIntegrationStartTimes = 
			"CREATE TABLE integrationstarttimes " + 
			"(integrtime_sid INT      UNSIGNED NOT NULL, UNIQUE KEY (integrtime_sid) " + 
			",integrtime_s   CHAR(26)          NOT NULL " + 
			");";
	private static final String createFiles = 
			"CREATE TABLE files " + 
			"(fileid INT UNSIGNED NOT NULL AUTO_INCREMENT, UNIQUE KEY (fileid) " + 
			",filetype TINYINT UNSIGNED NOT NULL " + 
			",filein VARCHAR(100) NOT NULL " + 
			",fileout VARCHAR(100) " + 
			");";
	private static final String createExtractedSources = 
			"CREATE TABLE extractedsources " +
 			"(xtrsrcid INT UNSIGNED NOT NULL AUTO_INCREMENT, UNIQUE KEY (xtrsrcid) " + 
			",beamid INT UNSIGNED NOT NULL, INDEX beamid (beamid), FOREIGN KEY (beamid) REFERENCES beams (beamid) " +
			",freqid INT UNSIGNED NOT NULL, INDEX freqid (freqid), FOREIGN KEY (freqid) REFERENCES frequencyband (freqid) " +
			",integrid INT UNSIGNED NOT NULL, INDEX integrid (integrid), FOREIGN KEY (integrid) REFERENCES integrationtimes (integrid) " +
			", htmid bigint UNSIGNED NOT NULL " +
			", ra DOUBLE NOT NULL " +
			", decl DOUBLE NOT NULL " +
			", ra_err DOUBLE NOT NULL " +
			", decl_err DOUBLE NOT NULL " +
			", I DOUBLE NOT NULL " +
			", Q DOUBLE NOT NULL " +
			", U DOUBLE NOT NULL " +
			", V DOUBLE NOT NULL " +
			", I_err DOUBLE NOT NULL " +
			", Q_err DOUBLE NOT NULL " +
			", U_err DOUBLE NOT NULL " +
			", V_err DOUBLE NOT NULL " +
			");";
	private static final String createBeams = 
			"CREATE TABLE beams " +
			"(beamid INT UNSIGNED NOT NULL, UNIQUE KEY (beamid) " +
			",obsid INT UNSIGNED NOT NULL, INDEX obsid (obsid), FOREIGN KEY (obsid) REFERENCES observation (obsid) " +
			",resid INT UNSIGNED NOT NULL, INDEX resid (resid), FOREIGN KEY (resid) REFERENCES resolution (resid) " +
			");";
	private static final String createIntegrationTimes = 
			"CREATE TABLE integrationtimes " +
			"(integrid INT UNSIGNED NOT NULL, UNIQUE KEY (integrid) " +
			",integrtime_sid INT UNSIGNED NOT NULL, INDEX integrtime_sid (integrtime_sid), FOREIGN KEY (integrtime_sid) " + 
								"REFERENCES integrationstarttimes (integrtime_sid) " +
			",fileid INT UNSIGNED NOT NULL, INDEX fileid (fileid), FOREIGN KEY (fileid) REFERENCES files (fileid) " +
			",duration SMALLINT UNSIGNED NOT NULL " +
			");";
	private static final String createObservation = 
			"CREATE TABLE observation " + 
			"(obsid INT UNSIGNED NOT NULL, UNIQUE KEY (obsid) " +
			",time_s TIMESTAMP NOT NULL " +
			",time_e TIMESTAMP NULL " +
			");";
	private static final String createFrequencyBand = 
			"CREATE TABLE frequencyband " +
			"(freqid INT UNSIGNED NOT NULL, UNIQUE KEY (freqid) " +
			",freq_s DOUBLE NOT NULL " +
			",freq_e DOUBLE NOT NULL " +
			",freq_eff DOUBLE NULL " +
			");";
	private static final String createResolution = 
			"CREATE TABLE resolution " +
			"(resid INT UNSIGNED NOT NULL, UNIQUE KEY (resid) " +
			", major DOUBLE NOT NULL " +
			", minor DOUBLE NOT NULL " +
			", pa DOUBLE NOT NULL " +
			");";
 
	public static void createTable(String s) {
	}
	
	public static void dropTables() {
	}

}
