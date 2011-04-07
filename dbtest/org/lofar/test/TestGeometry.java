package org.lofar.test;

import java.sql.*;
import java.util.*;

public class TestGeometry {
	public static void main(String[] args) {

		Connection con;
		DatabaseMetaData dbmd;

		try {
			Class.forName("com.mysql.jdbc.Driver");

			con = DriverManager.getConnection("jdbc:mysql://acamar.science.uva.nl:3306/lofar?user=lofar&password=cs1");

			Statement st = con.createStatement();
		
			Random rand = new Random();	
			String x = null, y = null;
			StringBuffer multipoint = null;
			long htmid = 0;
			long start = System.currentTimeMillis();

			// This run takes ~ 6347.378s, whereas time increases to the end.
			for (int i = 0; i < 30000; i++) {
				ResultSet rs = st.executeQuery("SELECT htmid, astext(lightcurve), x(first), y(first) FROM lightcurves where htmid = 6;");
				while (rs.next()) {
					htmid = rs.getLong(1);
					multipoint = new StringBuffer(rs.getString(2));
					x = rs.getString(3);
					y = rs.getString(4);
				}
				if (i % 100 == 0) System.out.println("i = " + i);
				//System.out.println("htmid = " + htmid);
				//System.out.println("selected multipoint.toString() = " + multipoint.toString());
				//System.out.println("x = " + x);
				//System.out.println("y = " + y);
				multipoint.insert(multipoint.length() - 1, "," + x + " " + y);
				//System.out.println("to be updated: multipoint.toString() = " + multipoint.toString());

				update(st, multipoint, htmid);
				rs.close();
			}
			con.close();
			long end = System.currentTimeMillis();
			System.out.println("Tijd: " + ((end - start) / 1000f) + "s");
			
		} catch (ClassNotFoundException e) {
                	System.err.println("ClassNotFoundException: " + e.getMessage());
		} catch (SQLException sqle) {
                	System.err.println("SQLException ErrorCode: " + sqle.getErrorCode());
                	System.err.println("SQLException SQLState: " + sqle.getSQLState());
                	System.err.println("SQLException Message: " + sqle.getMessage());
        	}

	}

	private static void update(Statement st, StringBuffer multipoint, long htmid) {
                StringBuffer query = new StringBuffer();
		Random rand = new Random();
		int x = rand.nextInt();
		int y = rand.nextInt();
                query.append("UPDATE lightcurves" +
                                        " SET lightcurve = multipointfromtext('" + multipoint.toString() + "')" + 
                                        ",first = pointfromtext('point(" + x + " " + y + ")')" + 
					" WHERE htmid = " + htmid + 
                                        ";"
                                );
                try {
                        st.executeUpdate(query.toString());
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ insert(st, lofarTable, src): \nquery:\n" + query.toString());
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

        }

}
