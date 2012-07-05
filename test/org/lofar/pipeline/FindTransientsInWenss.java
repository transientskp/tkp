package org.lofar.pipeline;

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

import VOTableUtil.*;
import org.lofar.data.*;
import org.lofar.services.*;
import org.lofar.util.DatabaseManager;

/** 
 *  This program reads data containing all sources found by SExtractor and streaming out as an output stream
 *  HtmIds for these sources will be calculated and the catalogues will be checked for existance
 *  of these sources (by htmids)
 *  If the source does not exists in one of the catalogues it is a new source
 */

/**
 * TODO: Input needed (from SExtractor) for frequency, stokes, logtime, observation, beam
 */
public class FindTransientsInWenss {
	
	// The run-specific variables //
	private static final String lofarTable = "lofarcat";
	private static final String writeDir = "files/sources/sexruns/wenss_transients/";
	private static final String thisRunComment = "; see file:///home/bscheers/test/lofar.html; LOFAR @ 75MHz; HTM-level=20";
	private static final int runid = 101;

	/* 
	1. Read SExtractor xml output file in which extracted sources are
	2. Every row corresponds to source
		2.1 Lookup in catalogues if the source exists in there
			2.1.1 If yes, it is known
				2.1.1.1 Check whether its flux has changed since last time
					if yes => write flux
					if no  => do nothing
			2.1.2 If no, the source is new 
				2.1.2.1 Insert it into the lofar catalogue
				2.1.2.2 Give ALERT
	*/
        public static void main(String[] args) throws IOException {
	
		long start = System.currentTimeMillis();
		long end = 0, total = 0;
		long startHTM = 0, endHTM = 0, totalHTM = 0, startDB = 0, endDB = 0, totalDB = 0;
		long startStream = 0, endStream = 0, totalStream = 0, startIO = 0, endIO = 0, totalIO = 0;
		float subtotals = 0, totals = 0, totalHTMs = 0, totalDBs = 0, totalStreams = 0, totalIOs = 0;
		int obsNumber = 0;

		Votable v = new Votable();
		Votable vot = null;
		Resource resource = null;
		Table table = null;
		startStream = System.currentTimeMillis();
		try {
			vot = v.unmarshal(System.in);
        		resource = vot.getResourceAt(0);
	        	table = resource.getTableAt(0);
			// PAY ATTENTION: choose the right obsNumber from file name
			// First we have to extract the observation time of image
			// For now we use the number in the name of the fits file f.ex. random_sources0465.fits
			// For now we use the number in the name of the fits file f.ex. wenss001.fits
			obsNumber = Integer.parseInt(resource.getName().substring(5, 8));
			// For now we use the number in the name of the fits file f.ex. W50_C4_T01.FLATN.700
			//obsNumber = Integer.parseInt(resource.getName().substring(8, 10));
			System.out.println("In image " + obsNumber + " SExtractor found " + table.getData().getTabledata().getTrCount() + " sources.");
		} catch (Exception e) {
	                System.err.println("Votable unmarshal exception");
	                System.err.println("Exception: " + e.getMessage());
        	        System.exit(1);
		}

		endStream = System.currentTimeMillis();
		totalStream = totalStream + (endStream - startStream);

		double ra = 0, dec = 0, flux_max = 0, flux_iso = 0, flux_isocor = 0, flux_aper = 0, flux_auto = 0, flux_quotient = 0;
		double dra = 0, ddec = 0, frms_max = 0, frms_iso = 0, frms_isocor = 0, frms_aper = 0, frms_auto = 0;
		double iso_areaf_image = 0;
		long htmid = 0L, htmIdNumber = 0L;
		int rangeLevel = 20;
		int lofarLevel = 10;
		
		try {
	                Connection con = DatabaseManager.getConnection("monetdb");
			Statement st = con.createStatement();

			// Every row (i) corresponds to a detected source
			//startIO = System.currentTimeMillis();
			for (int i = 0; i < table.getData().getTabledata().getTrCount(); i++) {
        	                Tr tr = table.getData().getTabledata().getTrAt(i);
                	        if (table.getFieldCount() != tr.getTdCount()) {
                        	        System.err.println("Number of columns (" + table.getFieldCount() + ") defined not equal to " +
                                	        "number of columns (" + tr.getTdCount() + ") to be inserted");
	                                System.exit(1);
        	                }
				// Every column (j) in a row (i) corresponds to a property of the source
				for (int j = 0; j < tr.getTdCount(); j++) {
	                                Field field = (Field) table.getFieldAt(j);
        	                        String name = field.getName();
                	                String ucd = field.getUcd();
                        	        Td td = table.getData().getTabledata().getTrAt(i).getTdAt(j);

	                                if (name.equals("ALPHAWIN_J2000")) {
        	                                ra = Double.parseDouble(td.getPCDATA());
                	                }
                        	        if (name.equals("DELTAWIN_J2000")) {
                                	        dec = Double.parseDouble(td.getPCDATA());
	                                }
	                                if (name.equals("ERRX2_WORLD")) {
        	                                dra = Double.parseDouble(td.getPCDATA());
						dra = 20 * Math.sqrt(dra);
                	                }
                        	        if (name.equals("ERRY2_WORLD")) {
                                	        ddec = Double.parseDouble(td.getPCDATA());
						ddec = 20 * Math.sqrt(ddec);
	                                }
        	                        if (name.equals("FLUX_MAX")) {
                	                        flux_max = Double.parseDouble(td.getPCDATA());
                        	        }
                                	if (name.equals("FLUX_ISO")) {
                                        	flux_iso = Double.parseDouble(td.getPCDATA());
	                                }
        	                        if (name.equals("FLUXERR_ISO")) {
                	                        frms_iso = Double.parseDouble(td.getPCDATA());
                        	        }
                                	if (name.equals("FLUX_ISOCOR")) {
                                        	flux_isocor = Double.parseDouble(td.getPCDATA());
	                                }
        	                        if (name.equals("FLUXERR_ISOCOR")) {
                	                        frms_isocor = Double.parseDouble(td.getPCDATA());
                        	        }
                                	if (name.equals("FLUX_APER")) {
                                        	flux_aper = Double.parseDouble(td.getPCDATA());
	                                }
        	                        if (name.equals("FLUXERR_APER")) {
                	                        frms_aper = Double.parseDouble(td.getPCDATA());
                        	        }
                                	if (name.equals("FLUX_AUTO")) {
                                        	flux_auto = Double.parseDouble(td.getPCDATA());
	                                }
        	                        if (name.equals("FLUXERR_AUTO")) {
                	                        frms_auto = Double.parseDouble(td.getPCDATA());
                        	        }
        	                        if (name.equals("ISOAREAF_IMAGE")) {
                	                        iso_areaf_image = Double.parseDouble(td.getPCDATA());
                        	        }
	                        }
				// end of reading columns for one row (= source)
				flux_quotient = Math.sqrt(iso_areaf_image);
				frms_iso = frms_iso / flux_quotient;
				frms_isocor = frms_isocor / flux_quotient;
				frms_aper = frms_aper / flux_quotient;
				frms_auto = frms_auto / flux_quotient;

				// We continue for processing this source
				startHTM = System.currentTimeMillis();
				HTMrange range20 = HtmServices.getHtmCover(rangeLevel, ra - dra, dec + ddec, ra + dra, dec - ddec);
				//System.out.println(range20);
				// TODO: unhard-code htmid level
				htmid = HtmServices.getHtmId(20, ra, dec);
				endHTM = System.currentTimeMillis();
				totalHTM = totalHTM + (endHTM - startHTM);
				// We set the source properties
				Source src = new Source();
				src.setHtmId(htmid);
				src.setHtmIdLevel(20);
				src.setRA(ra);
				src.setDRA(dra);
				src.setDec(dec);
				src.setDDec(ddec);
				src.setFluxMax(flux_max);
				//TODO: Let op! Hier is nog geen goede dFlux ingevuld!
				src.setDFluxMax(frms_iso);
				src.setFluxIso(flux_iso);
				src.setDFluxIso(frms_iso);
				src.setFluxIsocor(flux_isocor);
				src.setDFluxIsocor(frms_isocor);
				src.setFluxAper(flux_aper);
				src.setDFluxAper(frms_aper);
				src.setFluxAuto(flux_auto);
				src.setDFluxAuto(frms_auto);
				src.setIsoAreafImage(iso_areaf_image);
				src.setRunid(runid);
				src.setHtmRange(range20);
				src.setHtmRangeLevel(rangeLevel);
				src.setObsTime("" + obsNumber);
				src.setComment(src.getObsTime() + thisRunComment);
				// Lookup catalogues for existence of this source
				String[] views = CatalogueViews.getCatalogueViews();
				boolean knownSource = false;
				startDB = System.currentTimeMillis();
				for (int k = 0; k < views.length; k++) {
					if (sourceInCatalogue(st, views[k], src)) {
						// source already exists
						// TODO: check whether flux changed
						knownSource = true;
						// Source exists in one of the catalogues => no need to search any further
						//k = views.length;
						break;
					}
				}
				//System.out.println("knownSource = " + knownSource);
				endDB = System.currentTimeMillis();
				totalDB = totalDB + (endDB - startDB);
				// extra check (if views exists)
				//if (!knownSource && views.length == 0) {
				//TODO: Maak hier nog selectie als aantal view nul is
				if (!knownSource) {
					// new source => insert in lofar catalogue and make alertation
					//startHTM = System.currentTimeMillis();
					//endHTM = System.currentTimeMillis();
					//totalHTM = totalHTM + (endHTM - startHTM);
					startDB = System.currentTimeMillis();
					insert(st, lofarTable, src);
					endDB = System.currentTimeMillis();
					totalDB = totalDB + (endDB - startDB);
					System.out.println("		+-----------------------------------------------------------------------+");
					System.out.println("		|                                                                       |");
					System.out.println("		|                     !! NEW SOURCE !!                                  |");
					System.out.println("		|                                                                       |");
					System.out.println("		|  (htmid)       = (" + src.getHtmId() + ")                              ");
					System.out.println("		|  (RA, dec)     = (" + src.getRA() + ", " + src.getDec() + ")           ");
					System.out.println("		|  (dRA, ddec)   = (" + src.getDRA() + ", " + src.getDDec() + ")         ");
					System.out.println("		|  (flux, dflux) = (" + src.getFluxMax() + ", " + src.getDFluxMax() + ") ");
					System.out.println("		|                                                                       |");
					System.out.println("		|                                                                       |");
					System.out.println("		|  Inserted in the lofar catalogue (" + lofarTable + ")                  ");
					System.out.println("		|                                                                       |");
					System.out.println("		+-----------------------------------------------------------------------+");
				}
				// Write the flux of every source
				startIO = System.currentTimeMillis();
				write(src);
				endIO = System.currentTimeMillis();
				totalIO = totalIO + (endIO - startIO);
				range20 = null;
				src = null;
	                }
			//endIO = System.currentTimeMillis();
			//totalIO = totalIO + (endIO - startIO);
			con.close();
		} catch (SQLException sqle) {
			System.err.println("SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("SQLException: " + sqle.getMessage());
			System.exit(1);
		} catch (HTMException e) {
                        System.err.println(e.getMessage());
			System.exit(1);
    		} finally {
			end = System.currentTimeMillis();
			total = total + (end - start);
			totals = total / 1000f;
			totalHTMs = totalHTM / 1000f;
			totalDBs = totalDB / 1000f;
			totalStreams = totalStream / 1000f;
			totalIOs = totalIO / 1000f;
			subtotals = totalStreams + totalHTMs + totalDBs + totalIOs;
			System.out.println("+-------------------------------------+");
			System.out.println("|                                     |");
			System.out.println("| PROCESSING TIMES                    |");
			System.out.println("| InputStream: " + totalStreams   + " s");
			System.out.println("| HTM        : " + totalHTMs      + " s");
			System.out.println("| DB         : " + totalDBs       + " s");
			System.out.println("| IO         : " + totalIOs       + " s");
			System.out.println("|              -------                |");
			System.out.println("|              " + subtotals      + " s");
			System.out.println("|                                     |");
			System.out.println("| TOTAL      : " + totals         + " s");
			System.out.println("|                                     |");
			System.out.println("+-------------------------------------+");
		}
	}

	private static boolean sourceInCatalogue(Statement st, String catalogueView, Source src) {
		boolean sourceExists = true;
		StringBuffer query = new StringBuffer();
		// This is the way to get all the htmids
		int nranges = src.getHtmRange().nranges();
                src.getHtmRange().reset();
                long[][] rangeMatrix = new long[nranges][2];
		StringBuffer whereRestClause = new StringBuffer();
                for (int i = 0; i < nranges; i++) {
                	long[] l = src.getHtmRange().getNext();
                        //System.out.println("i = " + i + " long l: " + l[0] + " - " + l[1]);
			// First row of where clause
			if (i == 0) {
				if (l[0] == l[1]) {
					whereRestClause.append(" htmid = " + l[0]);
				} else {
					whereRestClause.append(" htmid BETWEEN " + l[0] + " AND " + l[1]);
				}
			} else {
				if (l[0] == l[1]) {
					whereRestClause.append(" OR htmid = " + l[0]);
				} else {
					whereRestClause.append(" OR htmid BETWEEN " + l[0] + " AND " + l[1]);
				}
			}
                }
		query.append(	"SELECT COUNT(*) " +
				"  FROM " + catalogueView +
				" WHERE " + whereRestClause.toString() +
				";");
		//System.out.println("QUERY: " + query.toString());
		try {
			ResultSet rs = st.executeQuery(query.toString());
                        while (rs.next()) {
                                if (rs.getInt(1) == 0) {
					sourceExists = false;
				} else {
					sourceExists = true;
				}
                        }
		} catch (SQLException sqle) {
			System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ sourceInCatalogue(st, view, src): \nquery:\n" + query.toString());
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
			System.exit(1);
		}
		
		return sourceExists;
	}

	private static void insert(Statement st, String lofarTable, Source src) {
                StringBuffer query = new StringBuffer();
		query.append("INSERT INTO " + lofarTable +
                                        " (htmid " +
                                        " ,ra " +
                                        " ,dra " +
                                        " ,decl " +
                                        " ,ddecl " +
                                        " ,runid " +
                                        " ,flux_max " +
                                        " ,flux_iso " +
                                        " ,flux_isocor " +
                                        " ,flux_aper " +
                                        " ,flux_auto " +
                                        " ,dflux_max " +
                                        " ,dflux_iso " +
                                        " ,dflux_isocor " +
                                        " ,dflux_auto " +
                                        " ,dflux_aper " +
                                        " ,isoareaf_image " +
                                        //" ,flux_isoadj " +
                                        " ,comment " +
                                        " ) VALUES ("
                                );
		query.append(	       	       src.getHtmId() +
                                        ", " + src.getRA() +
                                        ", " + src.getDRA() +
                                        ", " + src.getDec() +
                                        ", " + src.getDDec() +
                                        ", " + src.getRunid() +
                                        ", " + src.getFluxMax() +
                                        ", " + src.getFluxIso() +
                                        ", " + src.getFluxIsocor() +
                                        ", " + src.getFluxAper() +
                                        ", " + src.getFluxAuto() +
                                        ", " + src.getDFluxMax() +
                                        ", " + src.getDFluxIso() +
                                        ", " + src.getDFluxIsocor() +
                                        ", " + src.getDFluxAper() +
                                        ", " + src.getDFluxAuto() +
                                        ", " + src.getIsoAreafImage() +
                                        //", " + src.getflux_isoadj +
                                        ", '" + src.getComment() + "'" +
                                        ");"
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

	public static void write(Source src) {
                try {
			StringBuffer file = new StringBuffer(writeDir);
                        file.append("LFR" + src.getHtmId() + ".flux");
                        BufferedWriter out = new BufferedWriter(new FileWriter(file.toString(), true));
                        out.write(src.getObsTime() + ":" + src.getFluxMax() + ";");
                        out.close();
			file = null; 
			out = null;
                } catch (IOException e) {
                        System.err.println("-------------------------------------------------------");
                        System.err.println("- IOException @ write(Source src)");
                        System.err.println("- IOException @ write: src.getHtnId() = " + src.getHtmId());
                        System.err.println("- IOException @ write: src.getObsTime() = " + src.getObsTime());
                        System.err.println("- IOException @ write: src.getFluxMax() = " + src.getFluxMax());
                        System.err.println("- IOException Message: " + e.getMessage());
                        System.err.println("-------------------------------------------------------");
                }
        }

}
