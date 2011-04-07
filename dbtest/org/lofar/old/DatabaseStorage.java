package org.lofar.data;

import java.sql.*;

import org.lofar.services.*;
import org.lofar.util.*;

import edu.jhu.htm.core.*;
import edu.jhu.htm.geometry.*;
import edu.jhu.skiplist.*;

public class DatabaseStorage implements Observer, Storage {
	private Source source;
	private Subject lofarData;

	// Constructor is passed the lofarData object (the Subject)
	// and we use it to register the Storage as an observer
	public DatabaseStorage(Subject lofarData) {
		this.lofarData = lofarData;
		lofarData.registerObserver(this);
	}

	/**
	 * TODO: Use the MVC pattern in order to make a better design 
	 * for calling store()
	 */
	/*public void update(Observable obs, Object arg) {
		if (obs instanceof LofarData) {
			long startDB = System.currentTimeMillis();
			LofarData lofarData = (LofarData) obs;
			this.source = lofarData.getSource();
			// If the source already exists in the catalogues (for now only WENSS and our own) 
			// then it's a known source, else it is a new source
			// If it is new we add it to our lofar catalogue (and create a new lightcurve file)
			// If it is known we leave the catalogue (and add the flux to the existing lightcurve file)
			//boolean isNew = !isKnownSource(source);
			//System.out.println("isNew = " + isNew);
			//if (isNew) store();
			if (!isKnownSource(source)) store();
			float elapsedDB = (System.currentTimeMillis() - startDB) / 1000f;
			System.out.println("\tDatabase elapsed time: " + elapsedDB + " s");
		}
	}*/
	
	public void update(Source src) {
		this source = source;
		if (sourceIsNew()) store();
	}

	// TODO: Here we have to implement the Storage interface methods
	// See below
	//public void store() {
		// Store this source in the catalogue
	//}

	// TODO: Here we have to implement the Storage interface methods
	public boolean sourceIsNew() {
		return false;
	}

	// TODO: Here we have to implement the Storage interface methods
	public boolean sourceIsKnown() {
		return false;
	}

	// TODO: Here we have to implement the Storage interface methods
	public boolean fluxHasChanged() {
		return false;
	}

	/**
	 * This method check whether the extracted source is known or new; 
	 * For safety reasons we set it default to existing
	 */
	
//	private boolean isKnownSource(Source src) {
//		boolean known = true;
//
//		StringBuffer wenssCat = new StringBuffer();
//		HTMrange rangeWenss = null;
//		try {
//			rangeWenss = HtmServices.getHtmCover(src.getHtmRangeLevel()
//								,src.getRA() - src.getDRA() / 2
//								,src.getDec() + src.getDDec() / 2
//								,src.getRA() + src.getDRA() / 2
//								,src.getDec() - src.getDDec() / 2);
//		} catch (HTMException e) {
//			System.err.println("DatabaseStorage.isKnownSource: " + e.getMessage());
//			System.err.println("Source: HtmRangeLevel = " + src.getHtmRangeLevel() +
//						" RA = " + src.getRA() + 
//						" dRA = " + src.getDRA() + 
//						" dec = " + src.getDec() + 
//						" dDec = " + src.getDDec() + ";");
//			System.exit(1);
//		}
//
//		int nrangesWenss = rangeWenss.nranges();
//
//		long[][] rangeWenssMatrix = getRangeMatrix(rangeWenss);
//             	/*for (int i = 0; i < nrangesWenss; i++) {
//                   System.out.println("rangeWenssMatrix[" + i + "][0] = " + rangeWenssMatrix[i][0] + 
//					"rangeWenssMatrix[" + i + "][1] = " + rangeWenssMatrix[i][1]);
//       	        }*/
//
//		wenssCat.append("SELECT COUNT(*) FROM wenss WHERE ");
//		long htmIdStart = 0;
//		long htmIdEnd = 0;
//		for (int r = 0; r < nrangesWenss; r++) {
  //                      htmIdStart = rangeWenssMatrix[r][0];
    //                    htmIdEnd = rangeWenssMatrix[r][1];
//                        if (r == 0) {
//                                if (htmIdStart == htmIdEnd) {
//                                        wenssCat.append("htmid = " + htmIdStart + " ");
///                                } else {
//                                        wenssCat.append("htmid BETWEEN " + htmIdStart + " AND " + htmIdEnd + " ");
//                                }
//                        } else {
//                                if (htmIdStart == htmIdEnd) {
//                                        wenssCat.append("OR htmid = " + htmIdStart + " ");
//                                } else {
//                                        wenssCat.append("OR htmid BETWEEN " + htmIdStart + " AND " + htmIdEnd + " ");
//                                }
//                        }
//                }
//                wenssCat.append(";");
		//System.out.println("WENSS Query: " + wenssCat.toString());
		//int numWenssSources = executeQuery(wenssCat);
		//System.out.println("WENSS number od sources: " + numWenssSources);
		//if (numWenssSources == 0) {
//		if (executeQuery(wenssCat) == 0) {
//			known = false;
//		} else {
//			known = true;
//			System.out.println("+---------------------------");
//			System.out.println("| KNOWN WENSS source FOUND:");
//			System.out.println("| htmid = " + src.getHtmId() + "; ra = " + src.getRA() + 
//					"; dec = " + src.getDec() + "; flux = " + src.getFlux());
//			System.out.println("+---------------------------");
//			return known;
//		}

//		StringBuffer lofarCat = new StringBuffer();
//		HTMrange rangeLofar = null;
//		try {
  //                      rangeLofar = HtmServices.getHtmCover(19
    //                                                            ,src.getRA() - src.getDRA() / 2
//                                                                ,src.getDec() + src.getDDec() / 2
  //                                                              ,src.getRA() + src.getDRA() / 2
//                                                                ,src.getDec() - src.getDDec() / 2);
//                } catch (HTMException e) {
//                        System.err.println("DatabaseStorage.isKnownSource: " + e.getMessage());
//                        System.err.println("Source: HtmRangeLevel = 19" +
//                                                " RA = " + src.getRA() +
//                                                " dRA = " + src.getDRA() +
//                                                " dec = " + src.getDec() +
//                                                " dDec = " + src.getDDec() + ";");
//                        System.exit(1);
//                }

//		int nrangesLofar = rangeLofar.nranges();
//		long[][] rangeLofarMatrix = getRangeMatrix(rangeLofar);
		//System.out.println("nrangesLofar = " + nranges);
               	/*for (int i = 0; i < nrangesLofar; i++) {
                       System.out.println("rangeLofarMatrix[" + i + "][0] = " + rangeLofarMatrix[i][0] + 
					"rangeLofarMatrix[" + i + "][1] = " + rangeLofarMatrix[i][1]);
       	        }*/

//		lofarCat.append("SELECT COUNT(*) FROM lofarcat WHERE ");
  //              for (int r = 0; r < nrangesLofar; r++) {
//                        htmIdStart = rangeLofarMatrix[r][0];
  //                      htmIdEnd = rangeLofarMatrix[r][1];
//                        if (r == 0) {
  //                              if (htmIdStart == htmIdEnd) {
//                                        lofarCat.append("htmid = " + htmIdStart + " ");
//                                } else {
//                                        lofarCat.append("htmid BETWEEN " + htmIdStart + " AND " + htmIdEnd + " ");
//                                }
//                        } else {
///                                if (htmIdStart == htmIdEnd) {
//                                        lofarCat.append("OR htmid = " + htmIdStart + " ");
//                                } else {
//                                        lofarCat.append("OR htmid BETWEEN " + htmIdStart + " AND " + htmIdEnd + " ");
//                                }
//                        }
//                }
//		lofarCat.append(";");
		//System.out.println(lofarCat.toString());
		//System.out.println("LOFAR Query: " + lofarCat.toString());
                //int numLofarSources = executeQuery(lofarCat);
                //System.out.println("LOFAR number of sources: " + numLofarSources);
		//if (numLofarSources == 0) {
//		if (executeQuery(lofarCat) == 0) {
//			known = false;
//		} else {
//			known = true;
//			System.out.println("+---------------------------");
//			System.out.println("| KNOWN LOFAR source FOUND:");
//			System.out.println("| htmid = " + src.getHtmId() + "; ra = " + src.getRA() + 
//					"; dec = " + src.getDec() + "; flux = " + src.getFlux());
//			System.out.println("+---------------------------");
//		}
//		return known;
//
//	}

	/*	
	private long[][] getRangeMatrix(HTMrange range) {
		//System.out.println("htmrange: \n" + range);
		range.reset();
		int nranges = range.nranges();
		range.reset();
                long[][] rangeMatrix = new long[nranges][2];
                for (int i = 0; i < nranges; i++) {
                       long[] l = range.getNext();
                       rangeMatrix[i][0] = l[0];
                       rangeMatrix[i][1] = l[1];
                       //System.out.println("i = " + i + " long l: " + l[0] + " - " + l[1]);
                }
		return rangeMatrix;
	}
	*/

	/*
	private int executeQuery(StringBuffer query) {
		int number = 0;
		try {
	                Connection con = DatabaseManager.getConnection();
        	        Statement st = con.createStatement();
			ResultSet rs = st.executeQuery(query.toString());
			while (rs.next()) {
                 	       number = rs.getInt(1);
	                }
		} catch (SQLException e) {
			System.err.println("SQLException @ DatabaseStorage.executeQuery(): " + e.getMessage());
			System.err.println("SQLException : Query: " + query.toString());
			System.exit(1);
		}
		return number;
	}
	*/

	/*
	 * TODO This method should make use of a singleton
	 * AND an stored procedure
	 */
	public void store() {
		/*
		try {
			Connection con = DatabaseManager.getConnection();
			Statement st = con.createStatement();
			String query = "INSERT INTO lofarcat " + 
					"(htmid, ra, decl, flux) " +
					"VALUES (" + 
					source.getHtmId() + ", " +
                                        source.getRA() + ", " +
                                        source.getDec() + ", " +
                                        source.getFlux() + ")";
			st.executeUpdate(query);
			System.out.println("+---------------------------");
			System.out.println("| NEW source DETECTED:");
			System.out.println("| htmid = " + source.getHtmId() + "; ra = " + source.getRA() + 
					"; dec = " + source.getDec() + "; flux = " + source.getFlux());
			System.out.println("+---------------------------");
			//con.close();
		} catch (SQLException e) {
			System.err.println("SQLException @ dbstore: " + e.getMessage());
			System.err.println("SQLException @ dbstore: Source: " + 
					source.getHtmId() + ", " +
                                        source.getRA() + ", " +
                                        source.getDRA() + ", " +
                                        source.getDec() + ", " +
                                        source.getDDec() + ", " +
                                        source.getFlux());
			System.exit(1);
		} catch (Exception e) {
			System.err.println("Exception @ dbstore: " + e.getMessage());
			System.exit(1);
		}
		*/
	}
}
