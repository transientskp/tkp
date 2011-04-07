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
import org.lofar.services.*;
import org.lofar.util.DatabaseManager;

/** 
 *  This program loads the data of all sources found and STDOUTed by SExtractor
 *  HtmIds for these sources will be calculated 
 */

/**
 * TODO: Input needed (from SExtractor) for frequency, stokes, logtime, observation, beam
 */
public class TestQuery {
	
	protected static String showVariable = "SHOW VARIABLES LIKE 'max_al%';";
	protected static String setVariable = "SET @@max_allowed_packet=3000000;";

        public static void main(String[] args) throws IOException {
	
		try {
	                Connection con = DatabaseManager.getConnection();
			Statement st = con.createStatement();
			PreparedStatement pstmtShowVariable = con.prepareStatement(showVariable);
			PreparedStatement pstmtSetVariable = con.prepareStatement(setVariable);
			String value = selectVariable(pstmtShowVariable);
			System.out.println("VarVal: " + value);
			setVariable(pstmtSetVariable);
			value = selectVariable(pstmtShowVariable);
			System.out.println("VarVal: " + value);
                        con.close();
		} catch (SQLException sqle) {
			System.err.println("SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("SQLException: " + sqle.getMessage());
			System.exit(1);
		}
	}

        private static String selectVariable(PreparedStatement ps) throws SQLException {
		String value = null;
                try {
                        ResultSet rs = ps.executeQuery();
                        while (rs.next()) {
                                value = rs.getString(1);
                                value = rs.getString(2);
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

                return value;
        }

	private static void setVariable(PreparedStatement ps) throws SQLException {
                try {
                        ps.execute();
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ selectMaxFileId()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }
        }

}
