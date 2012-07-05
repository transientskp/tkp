package org.lofar.test.db;

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
import org.lofar.services.*;
import org.lofar.util.DatabaseManager;

/** 
 *  This program loads the data of all sources found and STDOUTed by SExtractor
 *  HtmIds for these sources will be calculated 
 */

/**
 * TODO: Input needed (from SExtractor) for frequency, stokes, logtime, observation, beam
 */
public class LoadExtractedSources {
	
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
                                                "(INTEGRTIME_SID" +
                                                ",INTEGRTIME_S  " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
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

		Votable v = new Votable();
		Votable vot = null;
		Resource resource = null;
		Table table = null;
		startStream = System.currentTimeMillis();
		java.util.Date date = new java.util.Date();

		try {
			vot = v.unmarshal(System.in);
			//System.out.println("resource count: " + vot.getResourceCount());
        		resource = vot.getResourceAt(0);
	        	table = resource.getTableAt(0);
			// PAY ATTENTION: choose 
			// First we have to extract the observation time of image
			// For now we use the number in the name of the fits file f.ex. random_sources0465.fits
			// so: TODO: Get a better way to register the obs time
			String fileName = resource.getName();
			obsNumber = Integer.parseInt(fileName.substring(14, 18));
			// For now we use the number in the name of the fits file f.ex. W50_C4_T01.FLATN.700
			//obsNumber = Integer.parseInt(resource.getName().substring(8, 10));
			System.out.println("In image " + obsNumber + " SExtractor found " + table.getData().getTabledata().getTrCount() + " sources.");
		} catch (Exception e) {
	                System.err.println("Votable unmarshal exception");
	                System.err.println("Exception: " + e.getMessage());
        	        System.exit(1);
		}

		endStream = System.currentTimeMillis();
		totalStream = totalStream + (endStream - startStream);

		double ra = 0, dec = 0, flux_max = 0, flux_iso = 0, flux_isocor = 0, flux_aper = 0, flux_auto = 0, flux_quotient = 0;
		double dra = 0, ddec = 0, frms_max = 0, frms_iso = 0, frms_isocor = 0, frms_aper = 0, frms_auto = 0;
		double iso_areaf_image = 0;
		long htmid = 0L, htmIdNumber = 0L;
		int rangeLevel = 20;
		int lofarLevel = 10;
		
		try {
			
			startDB = System.currentTimeMillis();
			startDBcon = startDB;
	                Connection con = DatabaseManager.getConnection("pipeline");
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
			startDBsel = System.currentTimeMillis();
			int fileId = selectFileId(pstmtMaxFilId);
			int startTimeId = selectStartId(pstmtMaxIntSTId);
			int integrId = selectIntegrId(pstmtMaxIntTId);
			endDBsel = System.currentTimeMillis();
			totalDBsel = totalDBsel + (endDBsel - startDBsel);

			startDBins = System.currentTimeMillis();
			doFiles(pstmtFil, fileId, resource.getName());
			doIntegrationStartTimes(pstmtIntST, startTimeId, date);
			// TODO: how do we know what the integration duration is?
			short duration = 1;// = 1 second
			doIntegrationTimes(pstmtIntT, integrId, startTimeId, fileId, duration);
			//System.out.println("fileId: " + fileId + "; startTimeId: " + startTimeId + "; integrId: " + integrId);

			endDB = System.currentTimeMillis();
			endDBins = endDB;
			totalDBins = totalDBins + (endDBins - startDBins);
			totalDB = totalDB + (endDB - startDB);

			// Every row (i) corresponds to a detected source
			//startIO = System.currentTimeMillis();
			for (int i = 0; i < table.getData().getTabledata().getTrCount(); i++) {
        	                Tr tr = table.getData().getTabledata().getTrAt(i);
                	        if (table.getFieldCount() != tr.getTdCount()) {
                        	        System.err.println("Number of columns (" + table.getFieldCount() + ") defined not equal to " +
                                	        "number of columns (" + tr.getTdCount() + ") to be inserted");
	                                System.exit(1);
        	                }
				// Every column (j) in a row (i) corresponds to a property of the source
				for (int j = 0; j < tr.getTdCount(); j++) {
	                                Field field = (Field) table.getFieldAt(j);
        	                        String name = field.getName();
                	                String ucd = field.getUcd();
                        	        Td td = table.getData().getTabledata().getTrAt(i).getTdAt(j);

	                                if (name.equals("ALPHAWIN_J2000")) {
        	                                ra = Double.parseDouble(td.getPCDATA());
                	                }
                        	        if (name.equals("DELTAWIN_J2000")) {
                                	        dec = Double.parseDouble(td.getPCDATA());
	                                }
	                                if (name.equals("ERRX2_WORLD")) {
        	                                dra = Double.parseDouble(td.getPCDATA());
						dra = 20 * Math.sqrt(dra);
                	                }
                        	        if (name.equals("ERRY2_WORLD")) {
                                	        ddec = Double.parseDouble(td.getPCDATA());
						ddec = 20 * Math.sqrt(ddec);
	                                }
        	                        if (name.equals("FLUX_MAX")) {
                	                        flux_max = Double.parseDouble(td.getPCDATA());
                        	        }
                                	if (name.equals("FLUX_ISO")) {
                                        	flux_iso = Double.parseDouble(td.getPCDATA());
	                                }
        	                        if (name.equals("FLUXERR_ISO")) {
                	                        frms_iso = Double.parseDouble(td.getPCDATA());
                        	        }
                                	if (name.equals("FLUX_ISOCOR")) {
                                        	flux_isocor = Double.parseDouble(td.getPCDATA());
	                                }
        	                        if (name.equals("FLUXERR_ISOCOR")) {
                	                        frms_isocor = Double.parseDouble(td.getPCDATA());
                        	        }
                                	if (name.equals("FLUX_APER")) {
                                        	flux_aper = Double.parseDouble(td.getPCDATA());
	                                }
        	                        if (name.equals("FLUXERR_APER")) {
                	                        frms_aper = Double.parseDouble(td.getPCDATA());
                        	        }
                                	if (name.equals("FLUX_AUTO")) {
                                        	flux_auto = Double.parseDouble(td.getPCDATA());
	                                }
        	                        if (name.equals("FLUXERR_AUTO")) {
                	                        frms_auto = Double.parseDouble(td.getPCDATA());
                        	        }
        	                        if (name.equals("ISOAREAF_IMAGE")) {
                	                        iso_areaf_image = Double.parseDouble(td.getPCDATA());
                        	        }
	                        }
				// end of reading columns for one row (= source)
				flux_quotient = Math.sqrt(iso_areaf_image);
				frms_iso = frms_iso / flux_quotient;
				frms_isocor = frms_isocor / flux_quotient;
				frms_aper = frms_aper / flux_quotient;
				frms_auto = frms_auto / flux_quotient;

				// We continue for processing this source
				startHTM = System.currentTimeMillis();
				//HTMrange range20 = HtmServices.getHtmCover(lofarLevel, ra - dra, dec + ddec, ra + dra, dec - ddec);
				//System.out.println(range20);
				// TODO: unhard-code htmid level
				htmid = HtmServices.getHtmId(lofarLevel, ra, dec);
				endHTM = System.currentTimeMillis();
				totalHTM = totalHTM + (endHTM - startHTM);


				//insertIntegrationTimes(pstmtT,);
				//insertIntegrationStartTimes(pstmtST,);

				// We set the source properties
				ExtractedSource src = new ExtractedSource();
				//src.setHtmIdLevel(20);
				src.setBeamId(1);
				//src.setFreqId(1);
				src.setIntegrId(integrId);
				src.setHtmId(htmid);
				src.setRA(ra);
				src.setDec(dec);
				src.setRaErr(dra);
				src.setDecErr(ddec);
				src.setStokesI(flux_max);
				src.setStokesQ(0);
				src.setStokesU(0);
				src.setStokesV(0);
				//TODO: Let op! Hier is nog geen goede dFlux ingevuld!
				src.setStokesIErr(frms_iso);
				src.setStokesQErr(0);
				src.setStokesUErr(0);
				src.setStokesVErr(0);
				startDB = System.currentTimeMillis();
				//TODO: use the systemvariable @@increment_offset or something like that to
				//ensure that an empty table starts at 0;
				startDBins = System.currentTimeMillis();
				for (int f = 0; f < 20; f++) {
					src.setFreqId(f);
					insertXtrSrc(pstmtXtrSrc, src);
				}
				endDB = System.currentTimeMillis();
				endDBins = endDB;
				totalDB = totalDB + (endDB - startDB);
				totalDBins = totalDBins + (endDBins - startDBins);
				//range20 = null;
				src = null;
	                }
			//Vector vec = resource.getTable();
			
			//System.out.println("Vector size: " + vec.size());
			//Param param = resource.getParamAt(0);
			//System.out.println("param.getName(): " + param.getName());
			//System.out.println("param.getValue(): " + param.getValue());
			
			//endIO = System.currentTimeMillis();
			//totalIO = totalIO + (endIO - startIO);
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
        		BufferedWriter out = new BufferedWriter(new FileWriter(logFile, true));
                        out.write(obsNumber + ";" + totalStreams + ";" + totalHTMs + ";" + 
				totalDBscon + ";" + totalDBssel + ";" + totalDBsins + ";" + totalDBscls + ";" + totalDBs + ";" + 
				subtotals + ";" + totals + "\n");
                        out.close();

		} catch (SQLException sqle) {
			System.err.println("SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("SQLException: " + sqle.getMessage());
			System.exit(1);
		} catch (HTMException e) {
                        System.err.println(e.getMessage());
			System.exit(1);
                } catch (IOException e) {
                        System.err.println("-------------------------------------------------------");
                        System.err.println("- IOException @ writeProcTimes");
                        System.err.println("- IOException Message: " + e.getMessage());
                        System.err.println("-------------------------------------------------------");
                        System.exit(1);
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

        public static void insertIntegrationStartTimes(PreparedStatement pstmt, int id, String date) throws SQLException {
                int i = 1;
                try {
                        pstmt.setInt(i++, id);
                        pstmt.setString(i++, date);
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- IntegrationStartTime Properties: " + id + "; " + date);
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
                insertIntegrationStartTimes(ps, startId, formatter.format(d));
        }

        private static void doIntegrationTimes(PreparedStatement ps, int integrId, int startId, int fileId, short duration) throws SQLException {
		insertIntegrationTimes(ps, integrId, startId, fileId, duration);
        }

}
