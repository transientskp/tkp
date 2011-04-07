package org.lofar.pipeline;

import java.io.*;
import java.sql.*;
import java.text.*;
import java.util.*;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;

import edu.jhu.htm.core.*;
import edu.jhu.htm.geometry.*;
import edu.jhu.skiplist.*;

import org.w3c.dom.Document;
import org.w3c.dom.*;

import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

import VOTableUtil.*;
import org.lofar.data.*;
import org.lofar.data.pipeline.*;
import org.lofar.services.*;
import org.lofar.util.DatabaseManager;

/** 
 *  This program loads the data of all sources found and STDOUTed by SExtractor
 *  HtmIds for these sources will be calculated 
 */

/**
 * TODO: Input needed (from SExtractor) for frequency, stokes, logtime, observation, beam
 */
public class TestInsertMySQLPipelineArea {
	
	// The run-specific variables //
	//private static final String lofarTable = "lofarcat";
	//private static final String writeDir = "files/sources/sexruns/lofar_transients/";
	//private static final String thisRunComment = "; see file:///home/bscheers/test/lofar.html; LOFAR @ 75MHz; HTM-level=20";
	private static Format formatter = new SimpleDateFormat("yyyy-MM-dd-HH:mm:ss:SSS");
	protected static String insertObservation = "INSERT INTO observation  " +
                                                "(OBSID         " +
                                                ",TIME_S        " +
                                                ",TIME_E        " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";
	protected static String insertResolution = "INSERT INTO resolution  " +
                                                "(RESID         " +
                                                ",MAJOR         " +
                                                ",MINOR         " +
                                                ",PA            " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";

	protected static String maxFileId = "SELECT MAX(fileid) FROM files;";
	protected static String insertFiles = "INSERT INTO files  " +
                                                "(FILEID        " +
                                                ",FILETYPE      " +
                                                ",FILEIN        " +
                                                ",FILEOUT       " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";
	protected static String insertBeams = "INSERT INTO beams  " +
                                                "(BEAMID        " +
                                                ",OBSID         " +
                                                ",RESID         " +
                                                ",FILEID        " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";
	protected static String maxIntegrationStartId = "SELECT MAX(integrtime_sid) FROM integrationstarttimes;";
	protected static String insertIntegrationStartTimes = "INSERT INTO integrationstarttimes  " +
                                                //"(INTEGRTIME_SID" +
                                                "(INTEGRTIME_S  " +
                                                ")              " +
                                        "VALUES                 " +
                                                //"(?             " +
                                                "(?             " +
                                                ");";
	protected static String maxIntegrId = "SELECT MAX(integrid) FROM integrationtimes;";
	protected static String insertIntegrationTimes = "INSERT INTO integrationtimes  " +
                                                "(INTEGRID      " +
                                                ",INTEGRTIME_SID" +
                                                ",FILEID        " +
                                                ",DURATION      " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";
	protected static String insertFrequencyBand = "INSERT INTO frequencyband  " +
                                                "(FREQID        " +
                                                ",FREQ_S        " +
                                                ",FREQ_E        " +
                                                ",FREQ_EFF      " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";
	protected static String insertExtractedSources = "INSERT INTO extractedsources_1s" +
                                                "(              " +
						//" XTRSRCID      " +
                                                " BEAMID        " +
                                                ",FREQID        " +
                                                ",INTEGRID      " +
                                                ",HTMID         " +
                                                ",RA            " +
                                                ",DECL          " +
                                                ",RA_ERR        " +
                                                ",DECL_ERR      " +
                                                ",I             " +
                                                ",Q             " +
                                                ",U             " +
                                                ",V             " +
                                                ",I_ERR         " +
                                                ",Q_ERR         " +
                                                ",U_ERR         " +
                                                ",V_ERR         " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(		" +
						//" ?             " +
                                                " ?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";


	/**
	 * main handles one votable file that consists of several extracted sources, 
	 * (Before beam, observation and frequencyband data is stored by an init
	 * (TODO: "observation, beams, resolution, frequencyband" tables)
	 * This method stores image meta data like the name of the file and integration
	 * start times and durations.
	 */
        public static void main(String[] args) throws IOException {
	
		long start = System.currentTimeMillis();
		long end = 0, total = 0;
		long startHTM = 0, endHTM = 0, totalHTM = 0;
		long startDB = 0, endDB = 0, totalDB = 0;
		long startDBcon = 0, endDBcon = 0, totalDBcon = 0;
		long startDBins = 0, endDBins = 0, totalDBins = 0;
		long startDBsel = 0, endDBsel = 0, totalDBsel = 0;
		long startDBcls = 0, endDBcls = 0, totalDBcls = 0;
		long startStream = 0, endStream = 0, totalStream = 0, startIO = 0, endIO = 0, totalIO = 0;
		float subtotals = 0, totals = 0, totalHTMs = 0;
		float totalDBs = 0, totalDBscon = 0, totalDBsins = 0, totalDBssel = 0, totalDBscls = 0;
		float totalStreams = 0, totalIOs = 0;
		int obsNumber = 0;
		String logFile = args[0];

		double ra = 0, dec = 0, flux_max = 0, flux_iso = 0, flux_isocor = 0, flux_aper = 0, flux_auto = 0, flux_quotient = 0;
		double dra = 0, ddec = 0, frms_max = 0, frms_iso = 0, frms_isocor = 0, frms_aper = 0, frms_auto = 0;
		double iso_areaf_image = 0;
		long htmid = 0L, htmIdNumber = 0L;
		int rangeLevel = 20;
		int lofarLevel = 10;
		
		try {
			
			startDB = System.currentTimeMillis();
			startDBcon = startDB;
	                Connection con = DatabaseManager.getConnection("mysql");
			//boolean b = con.isClosed();
			//System.out.println("Connection is closed: " + b);
			endDBcon = System.currentTimeMillis();
			totalDBcon = endDBcon - startDBcon;
			Statement st = con.createStatement();

			PreparedStatement pstmtMaxFilId = con.prepareStatement(maxFileId);
			PreparedStatement pstmtMaxIntSTId = con.prepareStatement(maxIntegrationStartId);
			PreparedStatement pstmtMaxIntTId = con.prepareStatement(maxIntegrId);

			PreparedStatement pstmtFil = con.prepareStatement(insertFiles);
			PreparedStatement pstmtIntT = con.prepareStatement(insertIntegrationTimes);
			PreparedStatement pstmtIntST = con.prepareStatement(insertIntegrationStartTimes);

			PreparedStatement pstmtXtrSrc = con.prepareStatement(insertExtractedSources);

			// For now it is very easy because all the images have
			// the same RESOLUTION: RESID (BMAJ, BMIN, BPA) and
			// at the same FREQUENCYBAND: FREQID (FREQ_S, FREQ_E, FREQ_EFF) and
			// in the same OBSERVATION: OBSID (TIME_S, TIME_E)
			// TODO: do this in other (bv InitObs) class

			// Store File data, Integration Start Time data, and Integration data
			/*startDBsel = System.currentTimeMillis();
			int obsId = selectObsId(pstmtMaxObsId);
			int fileId = selectFileId(pstmtMaxFilId);
			int startTimeId = selectStartId(pstmtMaxIntSTId);
			int integrId = selectIntegrId(pstmtMaxIntTId);
			endDBsel = System.currentTimeMillis();
			totalDBsel = totalDBsel + (endDBsel - startDBsel);

			startDBins = System.currentTimeMillis();
			
			initObs();

			doFiles(pstmtFil, fileId, resource.getName());
			doIntegrationStartTimes(pstmtIntST, startTimeId, date);
			// TODO: how do we know what the integration duration is?
			short duration = 1;// = 1 second
			doIntegrationTimes(pstmtIntT, integrId, startTimeId, fileId, duration);
			//System.out.println("fileId: " + fileId + "; startTimeId: " + startTimeId + "; integrId: " + integrId);
			*/
			endDB = System.currentTimeMillis();
			endDBins = endDB;
			totalDBins = totalDBins + (endDBins - startDBins);
			totalDB = totalDB + (endDB - startDB);

			// Every row (i) corresponds to a detected source
			//startIO = System.currentTimeMillis();
			//for (int i = 0; i < table.getData().getTabledata().getTrCount(); i++) {

			FitsFile f = new FitsFile();
		        f.setId(10);
                	f.setType(2);
	                f.setIn("in");
        	        f.setOut("out");	

			setFKeyCheck(st, 0);
			System.out.println("Check false");
			insertFiles(pstmtFil, f);
			setFKeyCheck(st, 1);
			System.out.println("Check true");
			

			startDB = System.currentTimeMillis();
			//con.close();
			endDB = System.currentTimeMillis();
			totalDBcls = endDB - startDB;
			totalDB = totalDB + totalDBcls;

                        totalHTMs = totalHTM / 1000f;
                        totalDBscon = totalDBcon / 1000f;
                        totalDBssel = totalDBsel / 1000f;
                        totalDBsins = totalDBins / 1000f;
                        totalDBscls = totalDBcls / 1000f;
                        totalDBs = totalDB / 1000f;
                        totalStreams = totalStream / 1000f;
                        //totalIOs = totalIO / 1000f;
                        subtotals = totalStreams + totalHTMs + totalDBs;// + totalIOs;
                        end = System.currentTimeMillis();
                        total = total + (end - start);
                        totals = total / 1000f;
                        System.out.println("+-------------------------------------+");
                        System.out.println("|                                     |");
                        System.out.println("| PROCESSING TIMES                    |");
                        System.out.println("| InputStream: " + totalStreams   + " s");
                        System.out.println("| HTM        : " + totalHTMs      + " s");
                        System.out.println("| DB con     : " + totalDBscon    + " s");
                        System.out.println("| DB sel     : " + totalDBssel    + " s");
                        System.out.println("| DB ins     : " + totalDBsins    + " s");
                        System.out.println("| DB close   : " + totalDBscls    + " s");
                        System.out.println("| DB tot     : " + totalDBs       + " s");
                        //System.out.println("| IO         : " + totalIOs       + " s");
                        System.out.println("|              -------                |");
                        System.out.println("|              " + subtotals      + " s");
                        System.out.println("|                                     |");
                        System.out.println("| TOTAL      : " + totals         + " s");
                        System.out.println("|                                     |");
                        System.out.println("+-------------------------------------+");
        		/*BufferedWriter out = new BufferedWriter(new FileWriter(logFile, true));
                        out.write(obsNumber + ";" + totalStreams + ";" + totalHTMs + ";" + 
				totalDBscon + ";" + totalDBssel + ";" + totalDBsins + ";" + totalDBscls + ";" + totalDBs + ";" + 
				subtotals + ";" + totals + "\n");
                        out.close();*/

		} catch (SQLException sqle) {
			System.err.println("SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("SQLException: " + sqle.getMessage());
			System.exit(1);
		/*} catch (HTMException e) {
                        System.err.println(e.getMessage());
			System.exit(1);
                } catch (IOException e) {
                        System.err.println("-------------------------------------------------------");
                        System.err.println("- IOException @ writeProcTimes");
                        System.err.println("- IOException Message: " + e.getMessage());
                        System.err.println("-------------------------------------------------------");
                        System.exit(1);*/
		}
	}

        public static void insertFiles(PreparedStatement pstmt, FitsFile f) throws SQLException {
                int i = 1;
                try {
                        pstmt.setInt(i++, f.getId());
                        pstmt.setInt(i++, f.getType());
                        pstmt.setString(i++, f.getIn());
                        pstmt.setString(i++, f.getOut());
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- FitsFile Properties: " + f.getId() + "; " + f.getType() + "; " + f.getIn() + "; " + f.getOut());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertIntegrationStartTimes(PreparedStatement pstmt, long startTime) throws SQLException {
                int i = 1;
                try {
                        //pstmt.setInt(i++, id);
                        pstmt.setLong(i++, startTime);
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- IntegrationStartTime Properties: " + startTime);
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertIntegrationTimes(PreparedStatement pstmt, int integrId, int startId, int fileId, short duration) throws SQLException {
                int i = 1;
                try {
                        pstmt.setInt(i++, integrId);
                        pstmt.setInt(i++, startId);
                        pstmt.setInt(i++, fileId);
                        pstmt.setShort(i++, duration);
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- IntegrationtTime Properties: " + integrId + "; " + startId + "; " + fileId + "; " + duration);
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertXtrSrc(PreparedStatement pstmt, ExtractedSource src) throws SQLException {
		int i = 1;
                try {
                        //pstmt.setInt(1, src.getXtrSrcid());
                        pstmt.setInt(i++, src.getBeamId());
                        pstmt.setInt(i++, src.getFreqId());
                        pstmt.setInt(i++, src.getIntegrId());
                        pstmt.setLong(i++, src.getHtmId());
                        pstmt.setDouble(i++, src.getRA());
                        pstmt.setDouble(i++, src.getDec());
                        pstmt.setDouble(i++, src.getRaErr());
                        pstmt.setDouble(i++, src.getDecErr());
                        pstmt.setDouble(i++, src.getStokesI());
                        pstmt.setDouble(i++, src.getStokesQ());
                        pstmt.setDouble(i++, src.getStokesU());
                        pstmt.setDouble(i++, src.getStokesV());
                        pstmt.setDouble(i++, src.getStokesIErr());
                        pstmt.setDouble(i++, src.getStokesQErr());
                        pstmt.setDouble(i++, src.getStokesUErr());
                        pstmt.setDouble(i++, src.getStokesVErr());
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- ExtractedSource Properties: " + src.getProps());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        private static int selectFileId(PreparedStatement ps) throws SQLException {
		int fileMaxId = 0;
                try {
                        ResultSet rs = ps.executeQuery();
                        while (rs.next()) {
                                fileMaxId = rs.getInt(1);
                        }
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ selectMaxFileId()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

                return fileMaxId + 1;
        }

        private static int selectIntegrId(PreparedStatement ps) throws SQLException {
                int integrId = 0;
                try {
                        ResultSet rs = ps.executeQuery();
                        while (rs.next()) {
                                integrId = rs.getInt(1);
                        }
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ selectMaxIntegrId()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

                return integrId + 1;
        }

        private static int selectStartId(PreparedStatement ps) throws SQLException {
                int startId = 0;
                try {
                        ResultSet rs = ps.executeQuery();
                        while (rs.next()) {
                                startId = rs.getInt(1);
                        }
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ selectMaxStartId()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

                return startId + 1;
        }
 
	private static void doFiles(PreparedStatement ps, int fileId, String inname) throws SQLException {
		FitsFile f = new FitsFile();
		f.setId(fileId);
		f.setType(2);
		f.setIn(inname);
		f.setOut(null);//TODO: but for now is sufficient
		insertFiles(ps, f);
	}

        private static void doIntegrationStartTimes(PreparedStatement ps, int startId, java.util.Date d) throws SQLException {
                insertIntegrationStartTimes(ps, d.getTime());
        }

        private static void doIntegrationTimes(PreparedStatement ps, int integrId, int startId, int fileId, short duration) throws SQLException {
		insertIntegrationTimes(ps, integrId, startId, fileId, duration);
        }

	public static void insertObservation(PreparedStatement pstmt, Observation obs) throws SQLException {
                int i = 1;
                try {
                        pstmt.setInt(i++, obs.getObsId());
                        pstmt.setLong(i++, obs.getTimeStart());
                        pstmt.setLong(i++, obs.getTimeEnd());
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertObservation");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
                        System.exit(1);
                }
        }

	public static void insertFrequencyBand(PreparedStatement pstmt, FrequencyBand fb) throws SQLException {
                int i = 1;
                double freqStart = fb.getFreqStart();
                double freqEnd = fb.getFreqEnd();
                double freqEff = fb.getFreqEff();
                try {
                        pstmt.setInt(i++, fb.getFreqId());
                        //for (int j = 0; j < freqBandStart.length; j++) {
                                pstmt.setDouble(i++, freqStart);
                                pstmt.setDouble(i++, freqEnd);
                        //}
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertFrequencyBands");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
                        System.exit(1);
                }
        }

	private static void setFKeyCheck(Statement st, int check) throws SQLException {
		int done = 0;
		String query = "SET FOREIGN_KEY_CHECKS = " + check + ";";
                try {
			st.executeUpdate(query);
			done++;
			System.out.println("Done: " + query);
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ selectMaxStartId()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

        }

}
