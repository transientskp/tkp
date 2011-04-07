package org.lofar.util;

import java.sql.*;
import java.util.Map;
import javax.naming.*;

public class DatabaseManager {
	private static DatabaseManager uniqueInstance;
	private static Connection con;
	private static String db;
	private static Map cachedPropertiesByKey = null;
	//private static int inst = 0;
	//private static int c = 0;
	
	private DatabaseManager() {
		try {
			if ("monetdb64".equals(db) || "monetdb".equals(db)) {
				Class.forName("nl.cwi.monetdb.jdbc.MonetDriver");
				// Vanwege foutje in monetdb wordt catalog "sys" onder demo aangemaakt, en 
				// die is alleen met -umonetdb te benaderen
				//con = DriverManager.getConnection("jdbc:monetdb://acamar:50000/demo", "lofar", "cs1");
				con = DriverManager.getConnection("jdbc:monetdb://acamar:50000/demo", "monetdb", "monetdb");
			} else if ("mysqlpipeline".equals(db)) {
				Class.forName("com.mysql.jdbc.Driver");
                        	con = DriverManager.getConnection("jdbc:mysql://acamar.science.uva.nl:3306/pipeline?user=lofar&password=cs1");
                        	//con = DriverManager.getConnection("jdbc:mysql://pc-swinbank.science.uva.nl:3306/pipeline?user=lofar&password=cs1");
			} else if ("mysqlcatalog".equals(db)) {
				Class.forName("com.mysql.jdbc.Driver");
                        	con = DriverManager.getConnection("jdbc:mysql://acamar.science.uva.nl:3306/catalog_model?user=lofar&password=cs1");
                        	//con = DriverManager.getConnection("jdbc:mysql://pc-swinbank.science.uva.nl:3306/pipeline?user=lofar&password=cs1");
			} else {
				throw new Exception("[DatabaseManager]Exception: No proper database selected.");
			}
		} catch (Exception e) {
			System.err.println("[DatabaseManager]Exception: " + e.getMessage());
			System.exit(1);
		}
	}
	
	// Use synchronized when dealing with multithreading
	public static synchronized DatabaseManager getInstance() {
		if (uniqueInstance == null) {
			uniqueInstance = new DatabaseManager();
			//System.out.println("DatabaseManager.getInstance(): uniqueInstance created.");
			//inst++;
		}
		//System.out.println("Database instance nr " + inst + " established");
		return uniqueInstance;
	}

	public static Connection getConnection(String database) {
		db = database;
		//System.out.println("Database connection nr " + c + " established");
		return DatabaseManager.getInstance().con;
        }

	public static Connection getCS1Connection() {
		//c++;
		//System.out.println("Database connection nr " + c + " established");
		return DatabaseManager.getInstance().con;
        }

	public static void closeConnection() {
		try {
			if (con != null) con.close();
		} catch (Exception e) {
			System.err.println("[DatabaseManager]Exception: " + e.getMessage());
		}
        }
}
