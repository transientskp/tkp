package org.lofar.test.cs1;

import java.io.*;
import java.sql.*;
import java.util.*;

public class LoadXtrSrcs {

    protected static String insertExtractedSources = "INSERT INTO extractedsources  " +
                                                "(XTRSRCID      " +
                                                ",BEAMID        " +
                                                ",LOGTIMEID     " +
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
                                                "(?             " +
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

    protected static String insertBeams = "INSERT INTO beams  " +
                                                "(BEAMID        " +
                                                ",OBSID         " +
                                                ",RESID         " +
                                                ",FREQID        " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
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

    protected static String insertObservation = "INSERT INTO observation  " +
                                                "(OBSID         " +
                                                ",TIME_S        " +
                                                ",TIME_E        " +
                                                ",TIME_INTEGR   " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";

    protected static String insertIntegrationTimes = "INSERT INTO beams  " +
                                                "(INTEGRID      " +
                                                ",BEAMID        " +
                                                ",RESID         " +
                                                ",FREQID        " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";







	public static void main(String[] args) {

		long start = System.currentTimeMillis();
		int lineNr = 0;
		int rows = Integer.parseInt(args[0]);
		Random r = new Random();
		try {
			Class.forName("com.mysql.jdbc.Driver");
                        Connection con = DriverManager.getConnection("jdbc:mysql://acamar.science.uva.nl:3306/cs1?user=lofar&password=cs1");
			Statement st = con.createStatement();
	                PreparedStatement pstmt = con.prepareStatement(insertExtractedSources);

			int xtrsrcid = 0
				, beamid      = 0
				, logtimeid = 0;
                        long htmid = 0;
			double ra = 0, decl = 0, ra_err = 0, decl_err = 0;
			double I = 0, Q = 0, U = 0, V = 0, I_err = 0, Q_err = 0, U_err = 0, V_err = 0;

		       
			for (int i = 0; i < rows; i++) {
				ra = r.nextDouble();
				decl = r.nextDouble();
				ra_err = r.nextDouble();
				decl_err = r.nextDouble();
				I = r.nextDouble();
				Q = r.nextDouble();
				U = r.nextDouble();
				V = r.nextDouble();
				I_err = r.nextDouble();
				Q_err = r.nextDouble();
				U_err = r.nextDouble();
				V_err = r.nextDouble();
				insertExtractedSources(pstmt, ++xtrsrcid, beamid, logtimeid, htmid, ra, decl, ra_err, decl_err
							, I, Q, U, V, I_err, Q_err, U_err, V_err);
			} 
			con.close();
			long end = System.currentTimeMillis();
			System.out.println("Time: " + (end - start) + " ms");

		} catch (IOException e) {
			System.out.println("IOException: " + e.getMessage());
		} catch (Exception e) {
			System.out.println("Exception: @ lineNr: " + lineNr + "\n" + e.getMessage());
		}

	}

    public static int insertExtractedSources(PreparedStatement pstmt
				, int xtrsrcid
				, int beamid
				, int logtimeid
				, long htmid
				, double ra
				, double decl  
				, double ra_err
				, double decl_err
				, double I
				, double Q
				, double U
				, double V
				, double I_err
				, double Q_err
				, double U_err
				, double V_err) throws SQLException, Exception {

        int inserted = 0;

        try {
                pstmt.setInt(1, xtrsrcid);
                pstmt.setInt(2, beamid);
                pstmt.setInt(3, logtimeid);
                pstmt.setLong(4, htmid);
                pstmt.setDouble(5, ra);
                pstmt.setDouble(6, decl);
                pstmt.setDouble(7, ra_err);
                pstmt.setDouble(8, decl_err);
                pstmt.setDouble(9, I);
                pstmt.setDouble(10, Q);
                pstmt.setDouble(11, U);
                pstmt.setDouble(12, V);
                pstmt.setDouble(13, I_err);
                pstmt.setDouble(14, Q_err);
                pstmt.setDouble(15, U_err);
                pstmt.setDouble(16, V_err);
                pstmt.executeUpdate();
                inserted++;
        } catch (SQLException sqle) {
                StringBuffer sb = new StringBuffer();
                sb.append("-------------------------------------------------------");
                sb.append("- SQLException @ xtrsrcid: " + xtrsrcid);
                sb.append("- SQLException ErrorCode: " + sqle.getErrorCode());
                sb.append("- SQLException SQLState: " + sqle.getSQLState());
                sb.append("- SQLException Message: " + sqle.getMessage());
                sb.append("- This query will not be inserted");
                sb.append("-------------------------------------------------------");
                System.err.println(sb.toString());
        }
        return inserted;
    }


}
