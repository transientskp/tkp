package org.lofar.pipeline;

import java.io.*;
import java.sql.*;
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
 *  This program loads the meta data from an observation run.
 *  Data from individual images are loaded via LoadExtractedSources
 */

/**
 * TODO: Input needed (from SExtractor) for frequency, stokes, logtime, observation, beam
 */
public class LoadMeta {
	
	// The run-specific variables //
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
	protected static String insertBeams = "INSERT INTO beams  " +
                                                "(BEAMID        " +
                                                ",OBSID         " +
                                                ",RESID         " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
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

        public static void main(String[] args) throws IOException {
	
		long start = System.currentTimeMillis();

		try {
	                Connection con = DatabaseManager.getConnection();
			Statement st = con.createStatement();

			PreparedStatement pstmtObs = con.prepareStatement(insertObservation);
			PreparedStatement pstmtRes = con.prepareStatement(insertResolution);
			PreparedStatement pstmtBms = con.prepareStatement(insertBeams);
			PreparedStatement pstmtFreq = con.prepareStatement(insertFrequencyBand);
			
			insertObs(pstmtObs, 1);
			insertRes(pstmtRes, 1, 9.0909e-02, 7.6207e-02, 3.08);
			insertBms(pstmtBms, 1, 1, 1);
			double freq_eff = 7.34398925781e07;
			double dfreq_eff = 7.32421875e05;
			double freq_s = freq_eff - (63 * dfreq_eff);
			double freq_e = freq_eff + (63 * dfreq_eff);
			insertFreq(pstmtFreq, 1, freq_s, freq_e, freq_eff);


			// For now it is very easy because all the images have
			// the same RESOLUTION: RESID (BMAJ, BMIN, BPA) and
			// for just one BEAMS: (BEAMID, OBSID, RESID) and
			// at the same FREQUENCYBAND: FREQID (FREQ_S, FREQ_E, FREQ_EFF) and
			// in the same OBSERVATION: OBSID (TIME_S, TIME_E)

			con.close();
		} catch (SQLException sqle) {
			System.err.println("SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("SQLException: " + sqle.getMessage());
			System.exit(1);
    		} finally {
			long end = System.currentTimeMillis();
			long totals = end - start;
			System.out.println("+-------------------------------------+");
			System.out.println("|                                     |");
			/*System.out.println("| PROCESSING TIMES                    |");
			System.out.println("| InputStream: " + totalStreams   + " s");
			System.out.println("| HTM        : " + totalHTMs      + " s");
			System.out.println("| DB         : " + totalDBs       + " s");
			System.out.println("| IO         : " + totalIOs       + " s");
			System.out.println("|              -------                |");
			System.out.println("|              " + subtotals      + " s");
			System.out.println("|                                     |");*/
			System.out.println("| TOTAL      : " + totals         + " s");
			System.out.println("|                                     |");
			System.out.println("+-------------------------------------+");
		}
	}

	public static void insertObs(PreparedStatement pstmt, int obsId) throws SQLException {
	        try {
        	        pstmt.setInt(1, obsId);
			pstmt.setTimestamp(2, new java.sql.Timestamp(new java.util.Date().getTime()));
			pstmt.setTimestamp(3, null);
                	pstmt.executeUpdate();
	        } catch (SQLException sqle) {
        	        StringBuffer sb = new StringBuffer();
                	sb.append("-------------------------------------------------------");
	                sb.append("- SQLException @ obsId: " + obsId);
        	        sb.append("- SQLException ErrorCode: " + sqle.getErrorCode());
                	sb.append("- SQLException SQLState: " + sqle.getSQLState());
	                sb.append("- SQLException Message: " + sqle.getMessage());
        	        sb.append("- This query will not be inserted");
                	sb.append("-------------------------------------------------------");
	                System.err.println(sb.toString());
        	}
	}

        public static void insertRes(PreparedStatement pstmt, int resId, double major, double minor, double pa) throws SQLException {
                try {
                        pstmt.setInt(1, resId);
			pstmt.setDouble(2, major);
			pstmt.setDouble(3, minor);
			pstmt.setDouble(4, pa);
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("-------------------------------------------------------");
                        sb.append("- SQLException @ resId: " + resId);
                        sb.append("- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("- SQLException Message: " + sqle.getMessage());
                        sb.append("- This query will not be inserted");
                        sb.append("-------------------------------------------------------");
                        System.err.println(sb.toString());
                }
        }

        public static void insertBms(PreparedStatement pstmt, int beamId, int obsId, int resId) throws SQLException {
                try {
                        pstmt.setInt(1, beamId);
                        pstmt.setInt(2, obsId);
                        pstmt.setInt(3, resId);
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("-------------------------------------------------------");
                        sb.append("- SQLException @ beamId: " + beamId);
                        sb.append("- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("- SQLException Message: " + sqle.getMessage());
                        sb.append("- This query will not be inserted");
                        sb.append("-------------------------------------------------------");
                        System.err.println(sb.toString());
                }
        }

        public static void insertFreq(PreparedStatement pstmt, int freqId, double freq_s, double freq_e, double freq_eff) throws SQLException {
                try {
                        pstmt.setInt(1, freqId);
			pstmt.setDouble(2, freq_s);
			pstmt.setDouble(3, freq_e);
			pstmt.setDouble(4, freq_eff);
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("-------------------------------------------------------");
                        sb.append("- SQLException @ freqId: " + freqId);
                        sb.append("- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("- SQLException Message: " + sqle.getMessage());
                        sb.append("- This query will not be inserted");
                        sb.append("-------------------------------------------------------");
                        System.err.println(sb.toString());
                }
        }

}
