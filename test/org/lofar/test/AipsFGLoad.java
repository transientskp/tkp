package org.lofar.test;

import java.io.*;
import java.sql.*;

public class AipsFGLoad {

    protected static String insertQuery = "INSERT INTO aipsfg2  " +
                                                "(ROW           " +
                                                ",SRC           " +
                                                ",SUBARRAY      " +
                                                ",FREQID        " +
                                                ",ANTS1         " +
                                                ",ANTS2         " +
                                                ",TIMERANGE1    " +
                                                ",TIMERANGE2    " +
                                                ",IFS1          " +
                                                ",IFS2          " +
                                                ",CHANS1        " +
                                                ",CHANS2        " +
                                                ",PFLAGS        " +
                                                ",REASON        " +
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
                                                ");";



	public static void main(String[] args) {

		int lineNr = 0;
		try {
			Class.forName("com.mysql.jdbc.Driver");
                        Connection con = DriverManager.getConnection("jdbc:mysql://acamar.science.uva.nl:3306/lofar?user=lofar&password=cs1");
			Statement st = con.createStatement();
	                PreparedStatement pstmt = con.prepareStatement(insertQuery);

			String file = "org/lofar/test/20050502AFG2";
     			BufferedReader in = new BufferedReader(new FileReader(file));
		        String str;
			int row = 0
				, src      = 0
				, subarray = 0
				, freqid   = 0
				, ants1    = 0
				, ants2    = 0
				, ifs1     = 0
				, ifs2     = 0
				, chans1   = 0
				, chans2   = 0; 
                        String timerange1
				, timerange2
				, pflags
				, reason;

			timerange1 = "";
			timerange2 = "";
			pflags = "";
			reason = "";
		        while ((str = in.readLine()) != null) {
				lineNr++;
		        	if (lineNr % 2 != 0) {
					row = Integer.parseInt(str.substring(4, 8).trim());
					src = Integer.parseInt(str.substring(16, 17).trim());
					subarray = Integer.parseInt(str.substring(28, 29).trim());
					freqid = Integer.parseInt(str.substring(40, 41).trim());
					ants1 = Integer.parseInt(str.substring(50, 52).trim());
					timerange1 = str.substring(58, 70);
					ifs1 = Integer.parseInt(str.substring(76, 77).trim());
					chans1 = Integer.parseInt(str.substring(85, 87).trim());
					pflags = str.substring(94, 98);
					reason = str.substring(104, str.length());
				} else {
					ants2 = Integer.parseInt(str.substring(50, 52).trim());
					timerange2 = str.substring(58, 70);
					ifs2 = Integer.parseInt(str.substring(76, 77).trim());
					chans2 = Integer.parseInt(str.substring(85, 87).trim());
		                        int inserted = insert(pstmt, row, src, subarray, freqid, ants1, ants2, timerange1, timerange2
						, ifs1, ifs2, chans1, chans2, pflags, reason);
				}
		        }
		        in.close();
			con.close();

		} catch (IOException e) {
			System.out.println("IOException: " + e.getMessage());
		} catch (Exception e) {
			System.out.println("Exception: @ lineNr: " + lineNr + "\n" + e.getMessage());
		}

	}

    public static int insert(PreparedStatement pstmt
				, int row
				, int src
				, int subarray
				, int freqid
				, int ants1
				, int ants2
				, String timerange1
				, String timerange2
				, int ifs1
				, int ifs2
				, int chans1
				, int chans2
				, String pflags
				, String reason) throws SQLException, Exception {

        int inserted = 0;

        try {
                pstmt.setInt(1, row);
                pstmt.setInt(2, src);
                pstmt.setInt(3, subarray);
                pstmt.setInt(4, freqid);
                pstmt.setInt(5, ants1);
                pstmt.setInt(6, ants2);
                pstmt.setString(7, timerange1);
                pstmt.setString(8, timerange2);
                pstmt.setInt(9, ifs1);
                pstmt.setInt(10, ifs2);
                pstmt.setInt(11, chans1);
                pstmt.setInt(12, chans2);
                pstmt.setString(13, pflags);
                pstmt.setString(14, reason);
                pstmt.executeUpdate();
                inserted++;
        } catch (SQLException sqle) {
                StringBuffer sb = new StringBuffer();
                sb.append("-------------------------------------------------------");
                sb.append("- SQLException @ row: " + row);
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
