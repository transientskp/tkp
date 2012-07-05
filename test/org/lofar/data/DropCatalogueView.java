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

public class DropCatalogueView {
	
	private static final String catalogueTable = "wensscat";
	private static final String catalogueView = "wensscatview";

        public static void main(String[] args) {

		long start = System.currentTimeMillis();
		try {
			Class.forName("com.mysql.jdbc.Driver");
	                Connection con = DriverManager.getConnection("jdbc:mysql://acamar.science.uva.nl:3306/lofar?user=lofar&password=cs1");

			Statement st = con.createStatement();
			dropView(st, catalogueView);
			st.close();
			con.close();
		} catch (SQLException sqle) {
			System.err.println("SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("SQLException: " + sqle.getMessage());
		} catch (Exception e) {
                        System.err.println("Exception: " + e.getMessage());
    		} finally {
			float elapsed = (System.currentTimeMillis() - start) / 1000f;
			System.out.println("Total (DB + File I/O) Elapsed time: " + elapsed + " s");
		}
	}
	
	public static void dropView(Statement st, String catalogueView) throws SQLException {

		StringBuffer dropCatView = new StringBuffer();
		try {
			dropCatView.append("DROP VIEW " + catalogueView + ";");
			st.executeUpdate(dropCatView.toString());
		} catch (SQLException e) {
			System.err.println(e.getMessage());
		}

        }
}
