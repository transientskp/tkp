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
import org.lofar.data.catalog.*;
import org.lofar.util.*;

/**
 * .
 * This program inserts the VLSS sources into the catalogue area.
 * Therefore it reads a text-file with the sources (downloaded from http://www.cv.nrao.edu/4mass/CATALOG/VLSSlist.full.gz).
 * Furthermore we used the publication in AJ, 2007, 134, 1245-1262 (http://lwa.nrl.navy.mil/VLSS/VLSS.2007AJ.pdf).
 * .
 */
public class LoadVLSS {

    protected static final String catalogue = "VLSS";	
    // The bandwith is 1.56 MHz divided into 128 channels.
    protected static final int freqband1_low = 73020000;
    protected static final int freqband1_high = 74580000;
    protected static final int freqband1_channels = 128;
    protected static String insertFreqBand = "INSERT INTO frequencybands 	" + 
						"(freqbandid         " +
						",freqband1_low      " +
						",freqband1_high     " +
						",freqband1_channels " + 
						") 		" + 
					"VALUES 		" +
						"(? 		" +
						",?		" + 
						",?		" + 
						",?		" + 
						");";
    protected static final double freq_eff1 = 73800000; // in MHz (73.8 MHz, the central frequency of the VLSSurvey)
    protected static String insertEffFreq = "INSERT INTO effectivefrequencies 	" + 
						"(freqeffid         " +
						",freqband_id     " +
						",freq_eff1 " + 
						") 		" + 
					"VALUES 		" +
						"(? 		" +
						",?		" + 
						",?		" + 
						");";
    // The level that is sufficient for the 80'' resolution of the VLSS
    protected static final int level = 12;
    protected static final String comment = "VLA Low-frequency Sky Survey (VLSS) Catalog Version: 2007-06-26";
    protected static String insertSource = "INSERT INTO sources " + 
						"(srcid 	" +
						//",class_id 	" +
						",htmid 	" +
						",ra 		" +
						",decl 		" +
						",ra_err 	" +
						",decl_err 	" +
						",sp_indx 	" +
						") 		" + 
					"VALUES 		" +
						"(? 		" +
						//",? 		" +
						",? 		" +
						",? 		" +
						",? 		" +
						",? 		" +
						",? 		" +
						",? 		" +
						");";
		protected static String insertCatSource = "INSERT INTO cataloguesources " + 
						"(		" + 
						//",catsrcid 	" +
						"cat_id 	" +
						",src_id 	" +
						",freqeff_id 	" +
						",I1 		" +
						",I1_err 	" +
						") 		" + 
					"VALUES 		" +
						"(		" +
						//",? 		" +
						"? 		" +
						",? 		" +
						",? 		" +
						",? 		" +
						",? 		" +
						");";
		protected static String maxSrcId = "SELECT MAX(srcid) FROM sources";


	public static void main (String argv []) throws Exception {

		// Read the file that contains the sources.
		// This is a VLSS specific file
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
		long start = System.currentTimeMillis();
		System.out.println("Loading started");
		String database = "mysqlcatalog";
		Connection con = DatabaseManager.getConnection(database);

		PreparedStatement psMaxId = con.prepareStatement(maxSrcId);

                PreparedStatement psFreqBand = con.prepareStatement(insertFreqBand);
                PreparedStatement psEffFreq = con.prepareStatement(insertEffFreq);
                PreparedStatement psSource = con.prepareStatement(insertSource);
                PreparedStatement psCatSource = con.prepareStatement(insertCatSource);

		int srcId = selectMax(psMaxId);

		FrequencyBands fb = new FrequencyBands();
		fb.setFreqBandId(1);
		fb.setFreqBand1Low(freqband1_low);
		fb.setFreqBand1High(freqband1_high);
		fb.setFreqBand1Channels(freqband1_channels);
		insertFreqBand(psFreqBand, fb);

		EffectiveFrequency ef = new EffectiveFrequency();
		ef.setFreqEffId(1);
		ef.setFreqBandId(fb.getFreqBandId());
		ef.setFreqEff1(freq_eff1);
		insertEffFreq(psEffFreq, ef);
		while ((str = in.readLine()) != null) {
	        	lineNr++;
			// This is file specific!)
	                if (lineNr > 9) {
				raHH = null; raMM = null; raSS = null; draHH = null; draMM = null; draSS = null;
				decDeg = null; decAM = null; decAS = null; ddecDeg = null; ddecAM = null; ddecAS = null;
				dist = 0; ddist = 0; dres = 0;
				flux = 0.; dflux = 0.; dmajor = 0.; dminor = 0.; PA = 0.; dPA = 0.;
				major = null; minor = null; res = null;
				/*if (!"NVSS catalog".equals(str.substring(2, 14)) 
				&& !"RA(2000)  Dec(2000)".equals(str.substring(3, 22))
				&& !" h  m    s ".equals(str.substring(0, 11))
				&& !"Found".equals(str.substring(0, 5))) {*/

				nsources++;
				srcId++;
				Source src = new Source();
				src.setSrcId(srcId);
				CatSource catSrc = new CatSource();
				catSrc.setCatId((byte)1);
				catSrc.setSrcId(src.getSrcId());
				catSrc.setFreqEffId(ef.getFreqEffId());
				raHH = str.substring(0, 2);
				raMM = str.substring(3, 5);
				raSS = str.substring(6, 11).trim();

				//System.out.println("lineNr = " + lineNr);
				//System.out.println("\tra: " + raHH + " " + raMM + " " + raSS);
				src.setRA(Conversion.fromRAToDegrees(raHH + " " + raMM + " " + raSS));
				//System.out.println("\tsrc.getRA(): " + src.getRA());

				decDeg = str.substring(14, 17);
				decAM = str.substring(18, 20);
				decAS = str.substring(21, 25).trim();
				//System.out.println("\tdec: " + decDeg + " " + decAM + " " + decAS);
				src.setDec(Conversion.fromDECToDegrees(decDeg + " " + decAM + " " + decAS));
				//System.out.println("\tsrc.getDec(): " + src.getDec());

				//src.setDist(Integer.parseInt(str.substring(24, 29).trim()));
				catSrc.setStokesI1(Double.parseDouble(str.substring(30, 35)));
				/*src.setMajor(str.substring(37, 42));
				src.setMinor(str.substring(43, 49));
				if (!"".equals(str.substring(49, 54).trim())) src.setPA(Double.parseDouble(str.substring(49, 54)));
				src.setRes(str.substring(55, 57));*/

				// read next line for errors in measured values
				secondStr = in.readLine();
				lineNr++;

				draSS = secondStr.substring(6, 11).trim();
				src.setRAErr(Conversion.fromRAToDegrees("00 00 " + draSS));

				ddecAS = secondStr.substring(21, 25).trim();
				src.setDecErr(Conversion.fromDECToDegrees("00 00 " + draSS));

				//src.setDDist(Integer.parseInt(secondStr.substring(24, 29).trim()));
                                catSrc.setStokesI1Err(Double.parseDouble(secondStr.substring(30, 35)));
				/*if (secondStr.length() > 36) {	
					if (!"".equals(secondStr.substring(38, 42).trim())) src.setDMajor(Double.parseDouble(secondStr.substring(38, 42)));
				}
        	                if (secondStr.length() > 42) {
					if (!"".equals(secondStr.substring(44, 49).trim())) src.setDMinor(Double.parseDouble(secondStr.substring(44, 49)));
				}
                	        if (secondStr.length() > 49) {
					if (!"".equals(secondStr.substring(49, 54).trim())) src.setDPA(Double.parseDouble(secondStr.substring(49, 54)));
				}
                        	if (secondStr.length() > 54) src.setDRes(Integer.parseInt(secondStr.substring(55, 58).trim()));*/

				//System.out.println("Source id: " + srcId);

				//htmid = HtmServices.getHtmId(level, src.getRA(), src.getDec());
				src.setHtmId(HtmServices.getHtmId(level, src.getRA(), src.getDec()));
                                //src.setHtmIdLevel(20);
                               	//src.setComment(comment);

				//inserted = insert(pstmt, lineNr, src);
				insertSource(psSource, src);
				insertCatSource(psCatSource, catSrc);
		                //totalInserted += inserted;
				//}
			}
		}
		con.close();
		System.out.println("Sources found: " + nsources);
		long end = System.currentTimeMillis();
		System.out.println("Run time: " + (end -start) + " ms");
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

	public static int insertSource(PreparedStatement pstmt, Source src) throws SQLException, Exception {
		int inserted = 0;
		try {
                	pstmt.setInt(1, src.getSrcId());
	                //pstmt.setInt(2, src.getClassId());
        	        pstmt.setLong(2, src.getHtmId());
                	pstmt.setDouble(3, src.getRA());
	                pstmt.setDouble(4, src.getDec());
        	        pstmt.setDouble(5, src.getRAErr());
                	pstmt.setDouble(6, src.getDecErr());
	                pstmt.setDouble(7, src.getSpectralIndex());
        	        pstmt.executeUpdate();
                	inserted++;
	        } catch (SQLException sqle) {
        	        StringBuffer sb = new StringBuffer();
                	sb.append("-------------------------------------------------------");
	                //sb.append("- SQLException @ " + catalogue + " lineNr: " + lineNr);
        	        sb.append("- SQLException @ params: insertSource()");
        	        sb.append("- SQLException @ params: " + src.getSrcId() + "; " + src.getHtmId() + "; " + src.getRA() + "; " + src.getDec() + "::..");
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

	public static int insertCatSource(PreparedStatement pstmt, CatSource catSrc) throws SQLException, Exception {
		int inserted = 0;
		try {
                	pstmt.setByte(1, catSrc.getCatId());
	                pstmt.setInt(2, catSrc.getSrcId());
        	        pstmt.setInt(3, catSrc.getFreqEffId());
                	pstmt.setDouble(4, catSrc.getStokesI1());
	                pstmt.setDouble(5, catSrc.getStokesI1Err());
        	        pstmt.executeUpdate();
                	inserted++;
	        } catch (SQLException sqle) {
        	        StringBuffer sb = new StringBuffer();
                	sb.append("-------------------------------------------------------");
        	        sb.append("- SQLException @ params: insertCatSource()");
	                //sb.append("- SQLException @ " + catalogue + " lineNr: " + lineNr);
        	        sb.append("- SQLException @ params: " + catSrc.getSrcId() + "::..");
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

	public static int insertFreqBand(PreparedStatement pstmt, FrequencyBands fb) throws SQLException, Exception {
		int inserted = 0;
		try {
                	pstmt.setInt(1, fb.getFreqBandId());
	                pstmt.setInt(2, fb.getFreqBand1Low());
        	        pstmt.setInt(3, fb.getFreqBand1High());
                	pstmt.setInt(4, fb.getFreqBand1Channels());
        	        pstmt.executeUpdate();
                	inserted++;
	        } catch (SQLException sqle) {
        	        StringBuffer sb = new StringBuffer();
                	sb.append("-------------------------------------------------------");
        	        sb.append("- SQLException @ params: insertFreqBand()");
	                //sb.append("- SQLException @ " + catalogue + " lineNr: " + lineNr);
        	        sb.append("- SQLException @ params: " + fb.getFreqBandId() + "::..");
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

	public static int insertEffFreq(PreparedStatement pstmt, EffectiveFrequency ef) throws SQLException, Exception {
		int inserted = 0;
		try {
                	pstmt.setInt(1, ef.getFreqEffId());
	                pstmt.setInt(2, ef.getFreqBandId());
        	        pstmt.setDouble(3, ef.getFreqEff1());
        	        pstmt.executeUpdate();
                	inserted++;
	        } catch (SQLException sqle) {
        	        StringBuffer sb = new StringBuffer();
                	sb.append("-------------------------------------------------------");
        	        sb.append("- SQLException @ insertEffFreq()");
	                //sb.append("- SQLException @ " + catalogue + " lineNr: " + lineNr);
        	        sb.append("- SQLException @ params: " + ef.getFreqEffId() + "::..");
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

        private static int selectMax(PreparedStatement ps) throws SQLException {
		int max = 0;
                try {
                        ResultSet rs = ps.executeQuery();
                        while (rs.next()) {
                                max = rs.getInt(1);
                        }
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ selectMax()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

                return max;
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
