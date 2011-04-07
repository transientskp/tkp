package org.lofar.load;

import java.io.*;
import java.text.*;
import java.math.*;
import java.sql.*;
import java.util.*;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;

import org.w3c.dom.Document;
import org.w3c.dom.*;
import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

import edu.jhu.htm.core.*;
import VOTableUtil.*; 

import org.lofar.services.*;

/**
* This class reads an xml-file of type VOTable (see http://www...)
* and inserts (suitable) objects into the database.
*/
public class LoadNVSS {


    protected static final String cat = "NVSS";	
    protected static final double freq = 1400000000;
    protected static String insertQuery = "INSERT INTO nvsscat 	" + 
						"(catsrcid " + 
						",class_id " +
						",cat_id " +
						",freq_id " +
						",htmid " +
						",ra " +
						",decl " +
						",ra_err " +
						",decl_err " +
						",I " +
						",Q " +
						",U " +
						",V " +
						",I_err " +
						",Q_err " +
						",U_err " +
						",V_err " +
						") 		" + 
					"VALUES 		" +
						"(? 		" +
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						",?		" + 
						");";


    public static void main (String argv []) throws Exception {

	//TODO read a file that lists the xml files to be uploaded.
	if (argv.length != 1) {
		throw new Exception("You need to specify the VOTable xml file.");
	}
	String fileOrUrl = argv[0];
	String listFile = argv[0];
	BufferedReader in = new BufferedReader(new FileReader(listFile));
	String str;
	while ((str = in.readLine()) != null) {
		String xmlFile = "../databases/nvss/" + str;
		System.out.println("Now loading data from " + xmlFile + "...");
	
	//PrintWriter out = new PrintWriter(System.out, true);
	//VOTableWrapper votw = new VOTableWrapper(fileOrUrl, out);
	//VOTableWrapper votw = new VOTableWrapper(fileOrUrl, null);
	VOTableWrapper votw = new VOTableWrapper(xmlFile, null);

	if (votw.getLastError() != null) {
		System.err.println("No VOTable found " + fileOrUrl);
		System.err.println("Last error is " + votw.getLastError());
		System.exit(1);
	}

	Votable v = votw.getVotable();
	if (v.getResourceCount() != 1) {
		System.err.println("We want VOTable to consist of 1 resource tag and not " + v.getResourceCount());
                System.exit(1);
	}

	Resource resource = v.getResourceAt(0);
	Table table = resource.getTableAt(0);

	//System.out.println("Number of columns to be inserted in MonetDB: " + table.getFieldCount());
	
	StringBuffer columnNames = new StringBuffer(cat + " Columns: \n");
	for (int i = 0; i < table.getFieldCount(); i++) {
        	Field field = (Field) table.getFieldAt(i);
        	//String u = field.getUcd();
		/*
        	if (u != null && u.equals("POS_EQ_RA_MAIN")) {
			System.out.println("Field " + i + " is for RA");
		}*/
		columnNames.append(i + " :: " + field.getName() + " :: " + field.getUnit() + "; \n");
	}
	System.out.println(columnNames.toString());
	

	//System.out.println("Tr count = " + table.getData().getTabledata().getTrCount());

	BigInteger htmid = null;
	long htmIdNumber = 0;
	int level = 20;
	double ra = 0, dra = 0;
	double decl = 0, ddecl = 0;
	double flux = 0, dflux = 0;
	String flg1 = null;
	int recno = 0;
	Double type = null;
	String comment = cat + "@" + freq/1000000 + "MHz";
	String query = null;
	int inserted = 0;
	long totalInserted = 0;
	//System.out.println("Before try");

	try {
		Class.forName("nl.cwi.monetdb.jdbc.MonetDriver");
        	Connection con = DriverManager.getConnection("jdbc:monetdb://localhost:45123/bart", "user1", "pw1");
		//Class.forName("com.mysql.jdbc.Driver");
                //Connection con = DriverManager.getConnection("jdbc:mysql://localhost/lofar?user=lofar&password=cs1");
		System.out.println("Number of rows to be inserted: " + table.getData().getTabledata().getTrCount());
		PreparedStatement pstmt = con.prepareStatement(insertQuery);
		for (int i = 0; i < table.getData().getTabledata().getTrCount(); i++) {
			Tr tr = table.getData().getTabledata().getTrAt(i);
			if (table.getFieldCount() != tr.getTdCount()) {
				System.err.println("Number of columns (" + table.getFieldCount() + ") defined not equal to " +
					"number of columns (" + tr.getTdCount() + ") to be inserted");
		                System.exit(1);
			}
			
			for (int j = 0; j < tr.getTdCount(); j++) {
				Field field = (Field) table.getFieldAt(j);
				String name = field.getName();
				String ucd = field.getUcd();
				Td td = table.getData().getTabledata().getTrAt(i).getTdAt(j);

				//if (name.equals("_RAJ2000")) {
				if (name.equals("RAJ2000")) {
					ra = convertRAtoDegrees(td.getPCDATA());
					//System.out.println("ra: " + ra);
				}
				if (name.equals("e_RAs")) {
					// this is in seconds (s) so we have to convert it to degrees as well
					dra = Double.parseDouble(td.getPCDATA()) / 240;
				}
				//if (name.equals("_DEJ2000")) {
				if (name.equals("DEJ2000")) {
					decl = convertDECtoDegrees(td.getPCDATA());
					//System.out.println("decl: " + decl);
				}
				if (name.equals("e_DEs")) {
					// this is in arcsec (") so we have to convert it to degrees as well
					ddecl = Double.parseDouble(td.getPCDATA()) / 3600;
				}
				if (name.equals("S1.4")) {
					flux = Double.parseDouble(td.getPCDATA());
					//System.out.println("flux: " + flux);
				}
				if (name.equals("e_S1.4")) {
					dflux = Double.parseDouble(td.getPCDATA());
				}
				/*if (name.equals("flg1")) {
					flg1 = td.getPCDATA();
				}*/
				if (name.equals("recno")) {
					recno = Integer.parseInt(td.getPCDATA());
				}

			}
			// create the level index required
		        HTMindex si = new HTMindexImp(level);
		        //String htmName = si.lookup(ra, decl);
	                //htmIdNumber = si.nameToId(htmName);
	                htmIdNumber = si.lookupId(ra, decl);
			
			//Statement st = con.createStatement();	
			inserted = insert(pstmt, recno, htmIdNumber, ra, dra, decl, ddecl, flux, dflux, comment);
			totalInserted += inserted;
        	
			if (i % 100 == 0) {
				System.out.println("Query nr " + i + " to be inserted");
			}
		}
		con.close();
		System.out.println("Total inserted rows: " + totalInserted);
	} catch (HTMException h) {
		System.err.println("Could not do look " + h);
	} catch (Exception e) {
		System.err.println("Error for recno = " + recno + " at htmId = " + htmIdNumber + ", ra = " + ra + ", decl = " + decl + ", ");
		System.err.println("flux = " + flux + ", flg1 = " + flg1 + ", comment = " + comment);
		System.err.println(e.getMessage());
		writeLog(new StringBuffer("Fatal error @ " + cat + " recno: " + recno + " :: "), e.getMessage());
		System.exit(1);
	}
	}//end-while
    }

    public static double convertRAtoDegrees(String ra) {
	String inputStr = ra;
	String patternStr = " ";
	String[] fields = inputStr.split(patternStr);
	return (((((Double.parseDouble(fields[2]) / 60) + Double.parseDouble(fields[1])) / 60) + Double.parseDouble(fields[0])) / 24) * 360;
    }

    public static double convertDECtoDegrees(String dec) {
	String inputStr = dec;
	String patternStr = " ";
	String[] fields = inputStr.split(patternStr);
	if ("-".equals(fields[0].substring(0, 1))) {
		return (-1 * (((Math.abs(Double.parseDouble(fields[2])) / 60) + Double.parseDouble(fields[1])) / 60) + Double.parseDouble(fields[0]));
	} else {
		return (((Double.parseDouble(fields[2]) / 60) + Double.parseDouble(fields[1])) / 60) + Double.parseDouble(fields[0]);
	}
    }

    public static int insert(PreparedStatement pstmt, int recno, long htmId, double ra, double dra
				, double dec, double ddec, double flux, double dflux, String comment) 
    throws SQLException, Exception {

	int inserted = 0;
	
	try {
		pstmt.setLong(1, htmId);
		pstmt.setDouble(2, ra);
		pstmt.setDouble(3, dra);
		pstmt.setDouble(4, dec);
		pstmt.setDouble(5, ddec);
		pstmt.setDouble(6, flux);
		pstmt.setDouble(7, dflux);
		pstmt.setString(8, comment);
		pstmt.executeUpdate();
		inserted++;
	} catch (SQLException sqle) {
		StringBuffer sb = new StringBuffer();
		sb.append("-------------------------------------------------------");
		sb.append("- SQLException @ " + cat + " recno: " + recno);
		sb.append("- SQLException @ params: " + htmId + "; " + ra + "; " + dra + "; " + dec + "; " + ddec + 
					"; " + flux + "; " + dflux + "; " + comment + "::..");
		sb.append("- SQLException ErrorCode: " + sqle.getErrorCode());
		sb.append("- SQLException SQLState: " + sqle.getSQLState());
		sb.append("- SQLException Message: " + sqle.getMessage());
		sb.append("- This query will not be inserted");
		sb.append("-------------------------------------------------------");
		System.err.println(sb.toString());
		writeLog(sb, sqle.getMessage());
		throw new Exception("query cannot be inserted because (see errorlog):\n" + sb.toString());
	}
	return inserted;
    }
    
    public static void writeLog(StringBuffer query, String message) throws IOException {
	try {
		Format formatter;
		formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss:SSS");
		BufferedWriter log = new BufferedWriter(new FileWriter("files/loadnvss.log", true));
		log.write(" - " + formatter.format(new java.util.Date()) + " - " + message + "\n\t - " + query.toString() + "\n");
		log.close();
	} catch (IOException ioe) {
		System.err.println(ioe.getMessage());
		System.exit(1);
	}
    }

}
