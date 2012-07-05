package org.lofar.transients;

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

/** This program reads an xml input file containing all sources found by SExtractor
 *  HtmIds for these sources will be calculated and the catalogue will be checked for existance
 *  of these sources (i.e htmids)
 *  If the source does not exists in the catalogue it is a new source
 */
public class AddHtmids {
	
	/**
	 * Helaas werkt PreparedStatemnet nog niet in MonetDB v4.10.2...
	 *
	 */
        public static void main(String[] args) throws HTMException {
	
		String file = null;	
		boolean output = false;
		int arguments = args.length;
		switch (arguments) {
			case 0:
				System.err.println("Usage: %>java AddHtmids filename [-o]");
				System.exit(1);
			case 1:
				file = args[0];
				break;
			case 2:
				file = args[0];
				if ("-o".equals(args[1])) {
					output = true;
				} else {
					System.err.println("Usage: %>java AddHtmids filename [-o]");
					System.exit(1);
				}
				break;
			default:
				System.err.println("Usage: %>java AddHtmids filename [-o]");
				System.exit(1);
		}
		
		/*
		if (args.length >= 1) {
			System.err.println("Usage: %>java AddHtmids filename [-o]");
			System.exit(1);
		} else {
			file = args[0];
			if (args.length > 1 && args[1].equals("-o")) {
				output = true;
			} else {
				System.err.println("Usage: %>java AddHtmids filename [o]");
				System.exit(1);
			}
		}
		*/
	
		try {

			Class.forName("nl.cwi.monetdb.jdbc.MonetDriver");
	                Connection con = DriverManager.getConnection("jdbc:monetdb://localhost:45123/bart", "user1", "pw1");

			DocumentBuilderFactory docBuilderFactory = DocumentBuilderFactory.newInstance();
		        DocumentBuilder docBuilder = docBuilderFactory.newDocumentBuilder();
		        Document doc = docBuilder.parse (new File(file));

		        doc.getDocumentElement().normalize ();
		        HtmServices.systemOutPrintln(output, "Root element of the doc is " + doc.getDocumentElement().getNodeName());
		        //System.out.println ("Attribute is : " + doc.getDocumentElement().getAttribute("nr"));
		        //System.out.println ("AttributeNode is : " + doc.getDocumentElement().getAttributeNode("nr"));

		        NodeList listOfSources = doc.getElementsByTagName("source");
		        int totalSources = listOfSources.getLength();
		        HtmServices.systemOutPrintln(output, "Total no of sources: " + totalSources);

			Statement st = con.createStatement();
		        for (int s = 0; s < listOfSources.getLength(); s++) {
				HtmServices.systemOutPrintln(output, "s = " + s);

				Node sourceNode = listOfSources.item(s);
				Element sourceElement = (Element) sourceNode;
				HtmServices.systemOutPrintln(output, "Attr nr of source value: " + sourceElement.getAttribute("nr"));

				NodeList fluxautoList = sourceElement.getElementsByTagName("flux_auto");
				Element fluxautoElement = (Element) fluxautoList.item(0);
				double flux = Double.parseDouble(((Node)fluxautoElement.getChildNodes().item(0)).getNodeValue().trim());
				HtmServices.systemOutPrintln(output, "flux_auto: " + flux);
		
				NodeList raList = sourceElement.getElementsByTagName("ra");
				Element raElement = (Element) raList.item(0);
				double ra = Double.parseDouble(((Node)raElement.getChildNodes().item(0)).getNodeValue().trim());
				HtmServices.systemOutPrintln(output, "ra: " + ra);
		
				NodeList draList = sourceElement.getElementsByTagName("dra");
				Element draElement = (Element) draList.item(0);
				double dra = Double.parseDouble(((Node)draElement.getChildNodes().item(0)).getNodeValue().trim());
				HtmServices.systemOutPrintln(output, "dra: " + dra);
		
				NodeList decList = sourceElement.getElementsByTagName("dec");
				Element decElement = (Element) decList.item(0);
				double dec = Double.parseDouble(((Node)decElement.getChildNodes().item(0)).getNodeValue().trim());
				HtmServices.systemOutPrintln(output, "dec: " + dec);
		
				NodeList ddecList = sourceElement.getElementsByTagName("ddec");
				Element ddecElement = (Element) ddecList.item(0);
				double ddec = Double.parseDouble(((Node)ddecElement.getChildNodes().item(0)).getNodeValue().trim());
				HtmServices.systemOutPrintln(output, "ddec: " + ddec);
		
				HTMrange range = HtmServices.getHtmCover(21, ra, dec + ddec, ra + dra, ddec);
				int nranges = range.nranges();
				HtmServices.systemOutPrintln(output, "nranges = " + nranges);
				// HTMrange needs to be reset in order to get the htmids for each range
				// for the method getNext(). 
				// ! Do not call any HTMrange methods in between !
				range.reset();
				// create a matrix of the pairs of ids
				// long[x][0] = start of range, long[x][1] = end of range, x = xth row of ranges
				long[][] rangeMatrix = new long[nranges][2];
		                for (int i = 0; i < nranges; i++) {
                		        long[] l = range.getNext();
					rangeMatrix[i][0] = l[0];
					rangeMatrix[i][1] = l[1];
		                        HtmServices.systemOutPrintln(output, "i = " + i + " long l: " + l[0] + " - " + l[1]);
		                }
				
				String selectHtmIds = evaluateSource(rangeMatrix, range.nranges());
				HtmServices.systemOutPrintln(output, "source nr s = " + s + " query: \n" + selectHtmIds);
				HtmServices.systemOutPrintln(output, "source nr s = " + s 
								+ " counted occurences in wenss: " + countSources(st, selectHtmIds));
				
				if (countSources(st, selectHtmIds) == 0) {
					HtmServices.systemOutPrintln(true, "This is a NEW source!");
					insertNewSource(st, ra, dra, dec, ddec, flux);
					HtmServices.systemOutPrintln(true, "And it added as a NEW source to our catalogue");
				} else {
					HtmServices.systemOutPrintln(true, "This source already exists in the WENSS catalogue");
				}

				// maybe TODO? Now that we know if the source is new or not 
				// we could store it as well in a file...
            		}
			con.close();

		} catch (SAXParseException err) {
                	System.out.println ("** Parsing error" + ", line " + err.getLineNumber () + ", uri " + err.getSystemId ());
	                System.out.println(" " + err.getMessage ());
        	} catch (SAXException e) {
	                Exception x = e.getException ();
	                ((x == null) ? e : x).printStackTrace ();
        	} catch (Throwable t) {
	                t.printStackTrace ();
    		}
	}
	
	public static String evaluateSource(long[][] htmRange, int nranges) {
		
		long htmIdStart = 0;
		long htmIdEnd = 0;
		StringBuffer selectQuery = new StringBuffer();
                selectQuery.append("SELECT COUNT(*) FROM htmtest WHERE ");
		for (int r = 0; r < nranges; r++) {
			htmIdStart = htmRange[r][0];
			htmIdEnd = htmRange[r][1];
			if (r == 0) {
			        if (htmIdStart == htmIdEnd) {
 					selectQuery.append("htmid = " + htmIdStart + " ");
                		} else {
        	       			selectQuery.append("htmid BETWEEN " + htmIdStart + " AND " + htmIdEnd + " ");
		        	}
			} else {
			        if (htmIdStart == htmIdEnd) {
 					selectQuery.append("OR htmid = " + htmIdStart + " ");
                		} else {
        	       			selectQuery.append("OR htmid BETWEEN " + htmIdStart + " AND " + htmIdEnd + " ");
		        	}
			}
		}
		selectQuery.append(";");
		//System.out.println("i: " + r + "; " + selectQuery.toString());
		return selectQuery.toString();

	}

	public static int countSources(Statement st, String query) throws SQLException, Exception {

        	int number = 0;

        	try {
                	ResultSet rs = st.executeQuery(query);
			while (rs.next()) {
				number = rs.getInt(1);
			}
        	} catch (SQLException sqle) {
                        System.err.println("-------------------------------------------------------");
                        System.err.println("- SQLException @ query: " + query);
                        System.err.println("- SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("- SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("- SQLException Message: " + sqle.getMessage());
                        System.err.println("- This query will not be inserted");
                        System.err.println("-------------------------------------------------------");
                        //writeLog(query, sqle.getMessage());
                        throw new Exception("query: " + query + "cannot be inserted");
                }
        	return number;
	}
	
	public static int insertNewSource(Statement st, double ra, double dra, double dec, double ddec, double flux) 
	throws SQLException, Exception {

		int inserted = 0;
		int level = 17;
		String comment = "LOFAR @ 75MHz; HTM-level=17";
	        StringBuffer query = new StringBuffer();

        	try {
			long htmId = HtmServices.getHtmId(level, ra, dec);
                	query.append("INSERT INTO lofarcat (htmid, ra, dra, decl, ddecl, flux, comment) VALUES (");
	                query.append(htmId + ", " + ra + ", " + dra + ", " + dec + ", " + ddec + ", " + flux + ", '" + comment + "');");
                	st.executeUpdate(query.toString());
                	inserted++;
			System.out.println("Query: " + query.toString() + " correctly inserted");
		} catch (HTMException e) {
                        System.err.println("- HTMException Message: " + e.getMessage());
                        System.err.println("- HTMException Query: " + query.toString());
                        System.err.println("- This query will not be inserted");
                        System.err.println("-------------------------------------------------------");
                        throw new Exception("query: " + query.toString() + "cannot be inserted");
	        } catch (SQLException sqle) {
        		System.err.println("-------------------------------------------------------");
                	System.err.println("- SQLException @ query: " + query.toString());
                        System.err.println("- SQLException ErrorCode: " + sqle.getErrorCode());
	                System.err.println("- SQLException SQLState: " + sqle.getSQLState());
        	        System.err.println("- SQLException Message: " + sqle.getMessage());
                	System.err.println("- This query will not be inserted");
                        System.err.println("-------------------------------------------------------");
	                throw new Exception("query: " + query.toString() + "cannot be inserted \n See errorlog");
	        }
        	return inserted;

	}

}
