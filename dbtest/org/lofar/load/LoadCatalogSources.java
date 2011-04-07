package org.lofar.load;

import java.io.*;
import java.text.*;
import java.sql.*;

import VOTableUtil.*; 
import JAVOT.src.VOTableWrapper;

import org.lofar.data.Catalog;
import org.lofar.data.CatalogSource;
import org.lofar.data.pipeline.FrequencyBand;
import org.lofar.util.DatabaseManager;

/**
* This class reads an xml-file of type VOTable (see http://www...)
* and inserts (suitable) objects into the database.
*/
public class LoadCatalogSources {

	protected static String insertCatalog = "INSERT INTO catalogues " +
                                                "(              " + 
						//" CATID         " +
                                                " CATNAME       " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(              " +
						//" ?             " +
                                                " ?             " +
                                                ");";

	protected static String insertFrequencyBand = "INSERT INTO frequencybands " +
                                                "(              " + 
						//" FREQID        " +
                                                " FREQ_LOW      " +
                                                ",FREQ_HIGH     " +
                                                //",FREQ_CHANNELS " +
                                                ",FREQ_EFF      " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(              " +
						//" ?             " +
                                                " ?             " +
                                                ",?             " +
                                                //",?             " +
                                                ",?             " +
                                                ");";


	protected static String insertCatalogSource = "INSERT INTO cataloguesources  " +
                                                "(              " + 
						//" CATSRCID      " +
                                                "CLASS_ID      " +
                                                ",CAT_ID        " +
                                                ",FREQ_ID       " +
                                                ",RA            " +
                                                ",DECL          " +
                                                ",RA_ERR        " +
                                                ",DECL_ERR      " +
                                                ",I             " +
                                                ",Q             " +
                                                ",U             " +
                                                ",V             " +
                                                ",I_ERR         " +
                                                ",Q_ERR         " +
                                                ",U_ERR         " +
                                                ",V_ERR         " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(              " + 
						//" ?             " +
                                                "?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";

	public static void main (String args []) throws Exception {

		if (args.length != 3) {
			throw new Exception("\n" +
				"You need to specify:\n" +
				"[1]: database (f.ex. mysqlpipeline) \n" + 
				"[2]: catalogue (f.ex. wenss) \n" + 
				"[3]: the name of the list file (incl. rel. path) containing the xml VOTable files.");
		}

		double ra = 0, decl = 0, flux = 0, fluxInt = 0;
		String classId = null;
		int recno = 0;
		long totalInserted = 0;

		try {
			String database = args[0];
			String catalogName = args[1];
			File listFileName = new File(args[2]);
			Connection con = DatabaseManager.getConnection(database);
			PreparedStatement pstmtFreqBand = con.prepareStatement(insertFrequencyBand);
			PreparedStatement pstmtCat = con.prepareStatement(insertCatalog);
			Catalog cat = new Catalog();
			cat.setCatId((byte)1);
			FrequencyBand fb = new FrequencyBand();
			fb.setFreqLow(33);
			fb.setFreqHigh(4.6);
			// Some pre-knowledge about existing catalogues
			if ("wenss".equals(catalogName)) {
				System.out.println("In if to fb.setFreqEff(330000000.)");
				cat.setCatName("wenss");
				fb.setFreqEff(330000000.);
			}
			System.out.println("Before insert fb");
			insertFreqBand(pstmtFreqBand, fb);
			System.out.println("After insert fb");
			insertCat(pstmtCat, cat);
			
		        BufferedReader in = new BufferedReader(new FileReader(listFileName));
		        String fileNameDir = listFileName.getParent();
			String absFileName;
			String fileName;
		        while ((fileName = in.readLine()) != null) {
				System.out.println("fileName = " + fileName);
				absFileName = fileNameDir + "/" + fileName;
				System.out.println("absFileName = " + absFileName);
				VOTableWrapper votw = new VOTableWrapper(absFileName, null);
				if (votw.getLastError() != null) {
					System.err.println("No VOTable found " + absFileName);
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
				System.out.println("Number of columns to be inserted: " + table.getFieldCount());
				StringBuffer columnNames = new StringBuffer("WENSS Columns: \n");
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
	
				System.out.println("Tr count = " + table.getData().getTabledata().getTrCount());

				PreparedStatement pstmtCatSrc = con.prepareStatement(insertCatalogSource);

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
						//String ucd = field.getUcd();
						Td td = table.getData().getTabledata().getTrAt(i).getTdAt(j);
						if (name.equals("_RAJ2000")) {
							ra = convertRAtoDegrees(td.getPCDATA());
							//System.out.println("ra: " + ra);
						}
						if (name.equals("_DEJ2000")) {
							decl = convertDECtoDegrees(td.getPCDATA());
							//System.out.println("decl: " + decl);
						}
						if (name.equals("Speak")) {
							flux = Double.parseDouble(td.getPCDATA());
							//System.out.println("flux: " + flux);
						}
						if (name.equals("Sint")) {
							fluxInt = Double.parseDouble(td.getPCDATA());
							//System.out.println("flux: " + flux);
						}
						if (name.equals("flg1")) {
							classId = td.getPCDATA();
						}
						if (name.equals("recno")) {
							recno = Integer.parseInt(td.getPCDATA());
						}
					}

					CatalogSource catsrc = new CatalogSource();
					//catsrc.setCatSrcId();
					catsrc.setCatId(cat.getCatId());
					if ("S".equals(classId)) {			
						catsrc.setClassId((byte)1);
					} else {
						catsrc.setClassId((byte)2);
					}
					catsrc.setFreqId(1);
					catsrc.setRA(ra);
					catsrc.setRaErr(0);			
					catsrc.setDec(decl);
					catsrc.setDecErr(0);			
					catsrc.setStokesI(new Double(flux));			
					insertCatSrc(pstmtCatSrc, catsrc);
        	
					if (i % 100 == 0) {
						System.out.println("Query nr " + i + " to be inserted");
					}
				}
		        }
			System.out.println("Total inserted rows: " + totalInserted);
		        in.close();
			con.close();
		} catch (IOException ioe) {
			System.err.println("IOException");
			System.err.println(ioe.getMessage());
			System.exit(1);
		} catch (SQLException se) {
			System.err.println("Exception");
			System.err.println(se.getMessage());
			System.exit(1);
		} catch (Exception e) {
			System.err.println("Error for recno = " + recno + " at ra = " + ra + ", decl = " + decl + ", ");
			System.err.println("flux = " + flux + ", flg1 = " + classId);
			System.err.println(e.getMessage());
			writeLog(new StringBuffer("Fatal error @ WENSS recno: " + recno + " :: "), e.getMessage());
			System.exit(1);
		}
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
		return (((Double.parseDouble(fields[2]) / 60) + Double.parseDouble(fields[1])) / 60) + Double.parseDouble(fields[0]);
	}

	public static void insertFreqBand(PreparedStatement pstmt, FrequencyBand fb) throws SQLException {
                int i = 1;
                try {
                        //pstmt.setInt(1, fb.getFreqId());
                        pstmt.setDouble(i++, fb.getFreqLow());
                        pstmt.setDouble(i++, fb.getFreqHigh());
                        pstmt.setDouble(i++, fb.getFreqEff());
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException in insertFreqBand() @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- Properties of object to be inserted: " + fb.getFreqEff());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
                        System.exit(1);
                }
        }

	public static void insertCat(PreparedStatement pstmt, Catalog cat) throws SQLException {
                int i = 1;
                try {
                        //pstmt.setInt(1, cat.getCatId());
                        pstmt.setString(i++, cat.getCatName());
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException in insertCat() @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- Properties of object to be inserted: " + cat.getCatName());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
                        System.exit(1);
                }
        }
	    
        public static void insertCatSrc(PreparedStatement pstmt, CatalogSource catsrc) throws SQLException {
                int i = 1;
                try {
                        //pstmt.setInt(1, catsrc.getCatSrcId());
                        pstmt.setByte(i++, catsrc.getClassId());
                        pstmt.setByte(i++, catsrc.getCatId());
                        pstmt.setInt(i++, catsrc.getFreqId());
                        pstmt.setDouble(i++, catsrc.getRA());
                        pstmt.setDouble(i++, catsrc.getDec());
                        pstmt.setDouble(i++, catsrc.getRaErr());
                        pstmt.setDouble(i++, catsrc.getDecErr());
                        pstmt.setDouble(i++, catsrc.getStokesI());
			if (catsrc.getStokesQ() != null) {
                        	pstmt.setDouble(i++, catsrc.getStokesQ());
			} else {
				pstmt.setNull(i++, java.sql.Types.DOUBLE);
			}
			if (catsrc.getStokesU() != null) {
                        	pstmt.setDouble(i++, catsrc.getStokesU());
			} else {
				pstmt.setNull(i++, java.sql.Types.DOUBLE);
			}
			if (catsrc.getStokesV() != null) {
                        	pstmt.setDouble(i++, catsrc.getStokesV());
			} else {
				pstmt.setNull(i++, java.sql.Types.DOUBLE);
			}
			if (catsrc.getStokesIErr() != null) {
                        	pstmt.setDouble(i++, catsrc.getStokesIErr());
			} else {
				pstmt.setNull(i++, java.sql.Types.DOUBLE);
			}
			if (catsrc.getStokesQErr() != null) {
                        	pstmt.setDouble(i++, catsrc.getStokesQErr());
			} else {
				pstmt.setNull(i++, java.sql.Types.DOUBLE);
			}
			if (catsrc.getStokesUErr() != null) {
                        	pstmt.setDouble(i++, catsrc.getStokesUErr());
			} else {
				pstmt.setNull(i++, java.sql.Types.DOUBLE);
			}
			if (catsrc.getStokesVErr() != null) {
                        	pstmt.setDouble(i++, catsrc.getStokesVErr());
			} else {
				pstmt.setNull(i++, java.sql.Types.DOUBLE);
			}
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException in insertCatSrc() @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- Properties of object to be inserted: " + catsrc.getRA() + ", " + catsrc.getDec());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
                        System.exit(1);
                }
        }
    
	public static void writeLog(StringBuffer query, String message) throws IOException {
		try {
			Format formatter;
			formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss:SSS");
			BufferedWriter log = new BufferedWriter(new FileWriter("loadwenss.log", true));
			log.write(" - " + formatter.format(new java.util.Date()) + " - " + message + "\n\t - " + query.toString() + "\n");
			log.close();
		} catch (IOException ioe) {
			System.err.println(ioe.getMessage());
			System.exit(1);
		}
	}

}
