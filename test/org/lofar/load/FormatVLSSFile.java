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
import org.lofar.data.*;

/**
* This class reads a text-file downloaded from http://www.cv.nrao.edu/4mass/CATALOG/VLSSlist.full.gz 
* and inserts the objects into the database.
*/
public class FormatVLSSFile {


    protected static final String cat = "VLSS";	
    protected static final double freq = 74000000; // 74MHz
    protected static final int level = 20;
    protected static final String comment = "VLA Low-frequency Sky Survey (VLSS) Catalog search, 1.0";
    protected static String insertQuery = "INSERT INTO vlsscat 	" + 
						"(HTMID 	" + 
						",RA		" + 
						",DRA		" + 
						",DECL		" +
						",DDECL		" +
						",FLUX		" + 
						",DFLUX		" + 
						",MAJOR		" + 
						",MINOR		" + 
						",DMAJOR	" + 
						",DMINOR	" + 
						",PA   		" + 
						",DPA  		" + 
						",RES  		" + 
						",DRES 		" + 
						",COMMENT	" +
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
						");";

    public static void main (String argv []) throws Exception {

	//read the file that contains the sources.
	if (argv.length != 1) {
		throw new Exception("You need to specify the input vlss file.");
	}
	String file = argv[0];

        double ra = 0, dec = 0, dra = 0, ddec = 0;
	String raHH = null, raMM = null, raSS = null, draHH = null, draMM = null, draSS = null;
	String decDeg = null, decAM = null, decAS = null, ddecDeg = null, ddecAM = null, ddecAS = null;
	int dist = 0, ddist = 0;
	double flux = 0., dflux = 0.;
	String major = null, minor = null;
	double dmajor = 0., dminor = 0.;
	double PA = 0., dPA = 0.;
	String res = null;
	int dres = 0;
	int nsources = 0, inserted = 0, totalInserted = 0;

	BufferedReader in = new BufferedReader(new FileReader(file));
        String str;
	String secondStr;
        int lineNr = 0;

	try {
                Class.forName("com.mysql.jdbc.Driver");
                Connection con = DriverManager.getConnection("jdbc:mysql://localhost/lofar?user=lofar&password=cs1");
                PreparedStatement pstmt = con.prepareStatement(insertQuery);

		while ((str = in.readLine()) != null) {
	        	lineNr++;
	                if (lineNr > 17) {
				raHH = null; raMM = null; raSS = null; draHH = null; draMM = null; draSS = null;
				decDeg = null; decAM = null; decAS = null; ddecDeg = null; ddecAM = null; ddecAS = null;
				dist = 0; ddist = 0; dres = 0;
				flux = 0.; dflux = 0.; dmajor = 0.; dminor = 0.; PA = 0.; dPA = 0.;
				major = null; minor = null; res = null;
				if (!"NVSS catalog".equals(str.substring(2, 14)) 
				&& !"RA(2000)  Dec(2000)".equals(str.substring(3, 22))
				&& !" h  m    s ".equals(str.substring(0, 11))
				&& !"Found".equals(str.substring(0, 5))) {
					nsources++;
					Source src = new Source();
					raHH = str.substring(0, 2);
					raMM = str.substring(3, 5);
					raSS = str.substring(6, 11).trim();
					//System.out.println("lineNr = " + lineNr);
					//System.out.println("\tra: " + raHH + " " + raMM + " " + raSS);
					src.setRA(Conversion.fromRAToDegrees(raHH + " " + raMM + " " + raSS));
					//System.out.println("\tsrc.getRA(): " + src.getRA());

					decDeg = str.substring(12, 15);
					decAM = str.substring(16, 18);
					decAS = str.substring(19, 23).trim();
					//System.out.println("\tdec: " + decDeg + " " + decAM + " " + decAS);
					src.setDec(Conversion.fromDECToDegrees(decDeg + " " + decAM + " " + decAS));
					//System.out.println("\tsrc.getDec(): " + src.getDec());

					src.setDist(Integer.parseInt(str.substring(24, 29).trim()));
					src.setFlux(Double.parseDouble(str.substring(31, 36)));
					src.setMajor(str.substring(37, 42));
					src.setMinor(str.substring(43, 49));
					if (!"".equals(str.substring(49, 54).trim())) src.setPA(Double.parseDouble(str.substring(49, 54)));
					src.setRes(str.substring(55, 57));

					// read next line for errors in measured values
					secondStr = in.readLine();
					lineNr++;

					draSS = secondStr.substring(6, 11).trim();
					src.setDRA(Conversion.fromRAToDegrees("00 00 " + draSS));

					ddecAS = secondStr.substring(19, 23).trim();
					src.setDDec(Conversion.fromDECToDegrees("00 00 " + draSS));

					src.setDDist(Integer.parseInt(secondStr.substring(24, 29).trim()));
                                        src.setDFlux(Double.parseDouble(secondStr.substring(31, 36)));
					if (secondStr.length() > 36) {	
					 if (!"".equals(secondStr.substring(38, 42).trim())) src.setDMajor(Double.parseDouble(secondStr.substring(38, 42)));
					}
        	                        if (secondStr.length() > 42) {
					 if (!"".equals(secondStr.substring(44, 49).trim())) src.setDMinor(Double.parseDouble(secondStr.substring(44, 49)));
					}
                	                if (secondStr.length() > 49) {
					 if (!"".equals(secondStr.substring(49, 54).trim())) src.setDPA(Double.parseDouble(secondStr.substring(49, 54)));
					}
                        	        if (secondStr.length() > 54) src.setDRes(Integer.parseInt(secondStr.substring(55, 58).trim()));

					//System.out.println(lineNr);

					//htmid = HtmServices.getHtmId(level, src.getRA(), src.getDec());
					src.setHtmId(HtmServices.getHtmId(level, src.getRA(), src.getDec()));
	                                src.setHtmIdLevel(20);
                                	src.setComment(comment);

					inserted = insert(pstmt, lineNr, src);
		                        totalInserted += inserted;
				}
			}
		}
		con.close();
		System.out.println("Sources found: " + nsources);
	} catch (SQLException sqle) {
        	System.err.println("SQLException ErrorCode: " + sqle.getErrorCode());
                System.err.println("SQLException SQLState: " + sqle.getSQLState());
                System.err.println("SQLException: " + sqle.getMessage());
                System.exit(1);
        } catch (HTMException e) {
                System.err.println(e.getMessage());
                System.exit(1);
	}
    }

    public static int insert(PreparedStatement pstmt, int lineNr, Source src) throws SQLException, Exception {

        int inserted = 0;

        try {
                pstmt.setLong(1, src.getHtmId());
                pstmt.setDouble(2, src.getRA());
                pstmt.setDouble(3, src.getDRA());
                pstmt.setDouble(4, src.getDec());
                pstmt.setDouble(5, src.getDDec());
                pstmt.setDouble(6, src.getFlux());
                pstmt.setDouble(7, src.getDFlux());
                pstmt.setString(8, src.getMajor());
                pstmt.setString(9, src.getMinor());
                pstmt.setDouble(10, src.getDMajor());
                pstmt.setDouble(11, src.getDMinor());
                pstmt.setDouble(12, src.getPA());
                pstmt.setDouble(13, src.getDPA());
                pstmt.setString(14, src.getRes());
                pstmt.setInt(15, src.getDRes());
                pstmt.setString(16, src.getComment());
                pstmt.executeUpdate();
                inserted++;
        } catch (SQLException sqle) {
                StringBuffer sb = new StringBuffer();
                sb.append("-------------------------------------------------------");
                sb.append("- SQLException @ " + cat + " lineNr: " + lineNr);
                sb.append("- SQLException @ params: " + src.getHtmId() + "; " + src.getRA() + "; " + src.getDec() + "::..");
                sb.append("- SQLException ErrorCode: " + sqle.getErrorCode());
                sb.append("- SQLException SQLState: " + sqle.getSQLState());
                sb.append("- SQLException Message: " + sqle.getMessage());
                sb.append("- This query will not be inserted");
                sb.append("-------------------------------------------------------");
                System.err.println(sb.toString());
                throw new Exception("query cannot be inserted because (see errorlog):\n" + sb.toString());
        }
        return inserted;
    }
    
    public static void write(StringBuffer query, String message) throws IOException {
	try {
		//Format formatter;
		//formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss:SSS");
		BufferedWriter out = new BufferedWriter(new FileWriter("../databases/vlss/vlsscat.txt", true));
		out.write(query.toString() + "\n");
		out.close();
	} catch (IOException ioe) {
		System.err.println(ioe.getMessage());
		System.exit(1);
	}
    }

}
