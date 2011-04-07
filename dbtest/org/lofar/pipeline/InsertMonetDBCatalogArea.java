package org.lofar.pipeline;

import java.io.*;
import java.sql.*;
import java.text.*;
import java.util.*;

import edu.jhu.htm.core.*;
import edu.jhu.htm.geometry.*;
import edu.jhu.skiplist.*;

import org.w3c.dom.Document;
import org.w3c.dom.*;

import org.xml.sax.SAXException;
import org.xml.sax.SAXParseException;

import VOTableUtil.*;
import org.lofar.data.*;
import org.lofar.data.catalog.*;
import org.lofar.services.*;
import org.lofar.util.DatabaseManager;

/** 
 *  This program is used to TEST performance of different types of databases in the CATALOG area
 *
 *  The input param is the database to test: either monetdb or mysql
 *
 *  A number of sources (Ns) is inserted, together with a number of measurements Nm = Ns * Nint,
 *  where Nint is the number of integrations (of 1second) that are kept in the pipeline area 
 *  before they are transferred to the catalog area
 *  The results (processing times) are written to a log file, named "monetdb | mysql + Ns(Ns)Nint(Nint) + .log",
 *  so in mysqlNs100Nint10000.log are the results of inserts of 
 *  
 */

/**
 * TODO: Input needed (from SExtractor) for frequency, stokes, logtime, observation, beam
 */
public class InsertMonetDBCatalogArea {
	
	private static String database;
	private static final int NfreqBands = 12;
	// Number of sources extracted in an image;
	private static final int Nsources = 10;
	// Number of 1second images that were kept in the pipeline area before transported;
	private static final int Nint = 10; 
	private static Format formatter = new SimpleDateFormat("yyyy-MM-dd-HH:mm:ss:SSS");
	protected static String insertObservation = "INSERT INTO observation  " +
                                                "(OBSID         " +
                                                ",TIME_S        " +
                                                ",TIME_E        " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";
	protected static String insertSoftwareVersion = "INSERT INTO softwareversions  " +
                                                "(SWVRSID       " +
                                                ",REPOSID       " +
                                                ",DBID          " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";

	/*protected static String maxFileId = "SELECT MAX(fileid) FROM files;";*/
	protected static String insertFiles = "INSERT INTO files  " +
                                                "(FILEID        " +
                                                ",FILETYPE      " +
                                                ",FILEIN        " +
                                                ",FILEOUT       " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";
	/*protected static String maxIntegrationStartId = "SELECT MAX(integrtime_sid) FROM integrationstarttimes;";*/
	protected static String insertIntegrationStartTimes = "INSERT INTO integrationstarttimes  " +
                                                "(INTEGRTIME_SID" +
                                                ",INTEGRTIME_S  " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ");";
	protected static String insertFrequencyBand = "INSERT INTO frequencybands " +
                                                "(FREQBANDID    " +
                                                ",FREQBAND1_S   " +
                                                ",FREQBAND1_E   " +
                                                ",FREQBAND2_S   " +
                                                ",FREQBAND2_E   " +
                                                ",FREQBAND3_S   " +
                                                ",FREQBAND3_E   " +
                                                ",FREQBAND4_S   " +
                                                ",FREQBAND4_E   " +
                                                ",FREQBAND5_S   " +
                                                ",FREQBAND5_E   " +
                                                ",FREQBAND6_S   " +
                                                ",FREQBAND6_E   " +
                                                ",FREQBAND7_S   " +
                                                ",FREQBAND7_E   " +
                                                ",FREQBAND8_S   " +
                                                ",FREQBAND8_E   " +
                                                ",FREQBAND9_S   " +
                                                ",FREQBAND9_E   " +
                                                ",FREQBAND10_S  " +
                                                ",FREQBAND10_E  " +
                                                ",FREQBAND11_S  " +
                                                ",FREQBAND11_E  " +
                                                ",FREQBAND12_S  " +
                                                ",FREQBAND12_E  " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
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
	protected static String insertEffectiveFrequency = "INSERT INTO effectivefrequency  " +
                                                "(FREQEFFID     " +
                                                ",BAND_ID       " +
                                                ",FREQ_EFF1     " +
                                                ",FREQ_EFF2     " +
                                                ",FREQ_EFF3     " +
                                                ",FREQ_EFF4     " +
                                                ",FREQ_EFF5     " +
                                                ",FREQ_EFF6     " +
                                                ",FREQ_EFF7     " +
                                                ",FREQ_EFF8     " +
                                                ",FREQ_EFF9     " +
                                                ",FREQ_EFF10    " +
                                                ",FREQ_EFF11    " +
                                                ",FREQ_EFF12    " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
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
	protected static String insertClassification = "INSERT INTO classification  " +
                                                "(CLASSID       " +
                                                ",TYPE          " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ");";
	protected static String insertSources = "INSERT INTO sources  " +
                                                "(              " +
                                                " SRCID         " +
                                                ",OBS_ID        " +
                                                ",CLASS_ID      " +
                                                ",HTMID         " +
                                                ",RA            " +
                                                ",DECL          " +
                                                ",RA_ERR        " +
                                                ",DECL_ERR      " +
                                                ",SP_INDX       " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(		" +
                                                " ?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";
	protected static String insertMeasurements_1s = "INSERT INTO measurements_1s  " +
                                                "(              " +
						//" XTRSRCID      " + ->auto_increment
                                                " SRC_ID          " +
                                                ",FREQEFF_ID      " +
                                                ",INTEGRTIME_S_ID " +
                                                ",FILE_ID         " +
                                                ",SWVRS_ID        " +
                                                ",I1              " +
                                                ",Q1              " +
                                                ",U1              " +
                                                ",V1              " +
                                                ",I2              " +
                                                ",Q2              " +
                                                ",U2              " +
                                                ",V2              " +
                                                ",I3              " +
                                                ",Q3              " +
                                                ",U3              " +
                                                ",V3              " +
                                                ",I4              " +
                                                ",Q4              " +
                                                ",U4              " +
                                                ",V4              " +
                                                ",I5              " +
                                                ",Q5              " +
                                                ",U5              " +
                                                ",V5              " +
                                                ",I6              " +
                                                ",Q6              " +
                                                ",U6              " +
                                                ",V6              " +
                                                ",I7              " +
                                                ",Q7              " +
                                                ",U7              " +
                                                ",V7              " +
                                                ",I8              " +
                                                ",Q8              " +
                                                ",U8              " +
                                                ",V8              " +
                                                ",I9              " +
                                                ",Q9              " +
                                                ",U9              " +
                                                ",V9              " +
                                                ",I10             " +
                                                ",Q10             " +
                                                ",U10             " +
                                                ",V10             " +
                                                ",I11             " +
                                                ",Q11             " +
                                                ",U11             " +
                                                ",V11             " +
                                                ",I12             " +
                                                ",Q12             " +
                                                ",U12             " +
                                                ",V12             " +
                                                ",I1_ERR          " +
                                                ",Q1_ERR          " +
                                                ",U1_ERR          " +
                                                ",V1_ERR          " +
                                                ",I2_ERR          " +
                                                ",Q2_ERR          " +
                                                ",U2_ERR          " +
                                                ",V2_ERR          " +
                                                ",I3_ERR          " +
                                                ",Q3_ERR          " +
                                                ",U3_ERR          " +
                                                ",V3_ERR          " +
                                                ",I4_ERR          " +
                                                ",Q4_ERR          " +
                                                ",U4_ERR          " +
                                                ",V4_ERR          " +
                                                ",I5_ERR          " +
                                                ",Q5_ERR          " +
                                                ",U5_ERR          " +
                                                ",V5_ERR          " +
                                                ",I6_ERR          " +
                                                ",Q6_ERR          " +
                                                ",U6_ERR          " +
                                                ",V6_ERR          " +
                                                ",I7_ERR          " +
                                                ",Q7_ERR          " +
                                                ",U7_ERR          " +
                                                ",V7_ERR          " +
                                                ",I8_ERR          " +
                                                ",Q8_ERR          " +
                                                ",U8_ERR          " +
                                                ",V8_ERR          " +
                                                ",I9_ERR          " +
                                                ",Q9_ERR          " +
                                                ",U9_ERR          " +
                                                ",V9_ERR          " +
                                                ",I10_ERR         " +
                                                ",Q10_ERR         " +
                                                ",U10_ERR         " +
                                                ",V10_ERR         " +
                                                ",I11_ERR         " +
                                                ",Q11_ERR         " +
                                                ",U11_ERR         " +
                                                ",V11_ERR         " +
                                                ",I12_ERR         " +
                                                ",Q12_ERR         " +
                                                ",U12_ERR         " +
                                                ",V12_ERR         " +
                                                ")                " +
                                        "VALUES                   " +
                                                "(		  " +
						//" ?             " +
                                                " ?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ",?               " +
                                                ");";


	/**
	 * main handles one votable file that consists of several extracted sources, 
	 * (Before beam, observation and frequencyband data is stored by an init
	 * (TODO: "observation, beams, resolution, frequencyband" tables)
	 * This method stores image meta data like the name of the file and integration
	 * start times and durations.
	 */
        public static void main(String[] args) throws IOException {
	
		if (args.length == 0) {
			System.err.println("Give the name of database system as an argument, either 'monetdb' or 'mysql'");
			System.exit(1);
		} else {
			database = args[0];
		}
		long start = System.currentTimeMillis();
		long end = 0, total = 0;
		long startHTM = 0, endHTM = 0, totalHTM = 0;
		long startDB = 0, endDB = 0, totalDB = 0;
		long startDBcon = 0, endDBcon = 0, totalDBcon = 0;
		long startDBins = 0, endDBins = 0, totalDBins = 0;
		long startDBsel = 0, endDBsel = 0, totalDBsel = 0;
		long startDBcls = 0, endDBcls = 0, totalDBcls = 0;
		long startStream = 0, endStream = 0, totalStream = 0, startIO = 0, endIO = 0, totalIO = 0;
		float subtotals = 0, totals = 0, totalHTMs = 0;
		float totalDBs = 0, totalDBscon = 0, totalDBsins = 0, totalDBssel = 0, totalDBscls = 0;
		float totalStreams = 0, totalIOs = 0;

		double ra = 0, dec = 0, flux_max = 0, flux_iso = 0, flux_isocor = 0, flux_aper = 0, flux_auto = 0, flux_quotient = 0;
		double dra = 0, ddec = 0, frms_max = 0, frms_iso = 0, frms_isocor = 0, frms_aper = 0, frms_auto = 0;
		double iso_areaf_image = 0;
		long htmid = 0L, htmIdNumber = 0L;
		int rangeLevel = 20;
		int lofarLevel = 10;
		
		try {
			
			startDB = System.currentTimeMillis();
			startDBcon = startDB;

	                Connection con = DatabaseManager.getConnection(database);
			endDBcon = System.currentTimeMillis();
			totalDBcon = endDBcon - startDBcon;

			Statement st = con.createStatement();

			PreparedStatement pstmtObservation = con.prepareStatement(insertObservation);
			PreparedStatement pstmtFil = con.prepareStatement(insertFiles);
			PreparedStatement pstmtIntST = con.prepareStatement(insertIntegrationStartTimes);
			PreparedStatement pstmtFreqBand = con.prepareStatement(insertFrequencyBand);
			PreparedStatement pstmtEffFreq = con.prepareStatement(insertEffectiveFrequency);
			PreparedStatement pstmtClass = con.prepareStatement(insertClassification);
			PreparedStatement pstmtSrc = con.prepareStatement(insertSources);
			PreparedStatement pstmtSwVrs = con.prepareStatement(insertSoftwareVersion);
			PreparedStatement pstmtMs = con.prepareStatement(insertMeasurements_1s);

			Observation obs = new Observation();
			obs.setObsId(1);
			obs.setTimeStart(20070124141724000L);
			obs.setTimeEnd(20070124170404000L);
			insertObservation(pstmtObservation, obs);
			
			FrequencyBands fb = new FrequencyBands();
			double[] bandStart = {10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120};
			double[] bandEnd = {15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 115, 125};
			fb.setFreqBandId(1);
			fb.setFreqBandStart(bandStart);
			fb.setFreqBandEnd(bandEnd);
			insertFrequencyBands(pstmtFreqBand ,fb);

			EffectiveFrequency ef = new EffectiveFrequency();
			ef.setFreqEffId(1);
			ef.setBandId(1);
			Double[] freqEff = {Double.valueOf(15), null, null, null, null, null, null, null, null, null, null, null};
			ef.setFreqEff(freqEff);
			insertEffectiveFrequency(pstmtEffFreq, ef);

			Classification cl = new Classification();
			cl.setClassId(1);
			short cltype = 1;
			cl.setType(cltype);
			insertClassification(pstmtClass, cl);

			SoftwareVersions swv = new SoftwareVersions();
			swv.setSwVrsId(1);
			swv.setReposId(1);
			swv.setDbId(1);
			insertSoftwareVersion(pstmtSwVrs, swv);
	
			IntegrationStartTimes ist = new IntegrationStartTimes();
			ist.setIntegrTimeStartId(1);
			ist.setIntegrTimeStart(20070124141724000L);
			
			// Every iteration (i) corresponds to a measurement made 
			// We set stokes params randomly
			Random rand = new Random();
			Double[] stokesI = new Double[12];
			Double[] stokesQ = new Double[12];
			Double[] stokesU = new Double[12];
			Double[] stokesV = new Double[12];
			Double[] stokesIErr = new Double[12];
			Double[] stokesQErr = new Double[12];
			Double[] stokesUErr = new Double[12];
			Double[] stokesVErr = new Double[12];
			int istId = 0;
			long istime = 20070124141724000L;
			// Lets say we observed Nsources sources in FOV with Ra: 50-56 degrees, and dec: 70-76degrees
			startDBins = System.currentTimeMillis();
			for (int i = 0; i < Nsources; i++) {
				org.lofar.data.catalog.Source src = new org.lofar.data.catalog.Source();
				src.setSrcId(i);
				src.setObsId(1);
				src.setClassId(1);
				ra = 50 + (6 * rand.nextDouble());
				dec = 70 + (6 * rand.nextDouble());
				// TODO: htmid should be calculated in other program...
				htmid = HtmServices.getHtmId(10, ra, dec);
				src.setHtmId(htmid);
				src.setRA(ra);
				src.setDec(dec);
				dra = 0.1 * rand.nextDouble();
                                ddec = 0.1 * rand.nextDouble();
				src.setRAErr(dra);
				src.setDecErr(ddec);
				insertSrc(pstmtSrc, src);
				// lets say Nint series of 1-second images were kept in the pipeline area
				for (int j = 0; j < Nint; j++) {
					Measurement ms = new Measurement();
					ms.setSrcId(src.getSrcId());
					ms.setFreqEffId(ef.getFreqEffId());
					//TODO: build another for loop
					istime = istime + 1000L;
					//System.out.println("j = " + j);
					insertIntegrationStartTimes(pstmtIntST, istId++, istime);
					//TODO: also insert effective frequencies 
					// every group of measurements (i.e. msids with the same integrtime_sid)
					// have the same freqeffid, but the next integrtime_id for these
					// sources might have a different freqeffid); as discussed with Ben and James
					ms.setIntegrTimeStartId(j);
					FitsFile f = new FitsFile();
			                f.setId((istId + 1000));
			                f.setType(2);
			                f.setIn("TKP" + istId + ".fits");
			                f.setOut(f.getIn());
			                insertFiles(pstmtFil, f);
					ms.setFileId(f.getId());
					f = null;
					ms.setSwVrsId(1);
					for (int k = 0; k < 12; k++) {
						//System.out.println("k = " + k);
						stokesI[k] = Double.valueOf(rand.nextDouble());
						stokesQ[k] = Double.valueOf(rand.nextDouble());
						stokesU[k] = Double.valueOf(rand.nextDouble());
						stokesV[k] = Double.valueOf(rand.nextDouble());
						stokesIErr[k] = Double.valueOf(rand.nextDouble());
						stokesQErr[k] = Double.valueOf(rand.nextDouble());
						stokesUErr[k] = Double.valueOf(rand.nextDouble());
						stokesVErr[k] = Double.valueOf(rand.nextDouble());
					}
					ms.setStokesI(stokesI);
					ms.setStokesQ(stokesQ);
					ms.setStokesU(stokesU);
					ms.setStokesV(stokesV);
					ms.setStokesIErr(stokesIErr);
					ms.setStokesQErr(stokesQErr);
					ms.setStokesUErr(stokesUErr);
					ms.setStokesVErr(stokesVErr);
					// Use Statement to insert measurement
					//insertMS(st, ms);
					// Use PreparedStatement to insert measurement
					insertMeasurements(pstmtMs, ms);
					ms = null;
				}
				src = null;
	                }
			endDBins = System.currentTimeMillis();
			totalDBins = totalDBins + (endDBins - startDBins);
			totalDBsins = totalDBins / 1000f;
			totalDBscon = totalDBcon / 1000f;
			//endIO = System.currentTimeMillis();
			//totalIO = totalIO + (endIO - startIO);
			//startDB = System.currentTimeMillis();
			//con.close();
			/*endDB = System.currentTimeMillis();
			totalDBcls = endDB - startDB;
			totalDB = totalDB + totalDBcls;

                        totalHTMs = totalHTM / 1000f;
                        totalDBscon = totalDBcon / 1000f;
                        totalDBssel = totalDBsel / 1000f;
                        totalDBsins = totalDBins / 1000f;
                        totalDBscls = totalDBcls / 1000f;
                        totalDBs = totalDB / 1000f;
                        totalStreams = totalStream / 1000f;
                        //totalIOs = totalIO / 1000f;
                        subtotals = totalStreams + totalHTMs + totalDBs;// + totalIOs;
                        end = System.currentTimeMillis();
                        total = total + (end - start);
                        totals = total / 1000f;*/
                        System.out.println("+-------------------------------------+");
                        System.out.println("|                                     |");
                        System.out.println("| PROCESSING TIMES                    |");
                        //System.out.println("| InputStream: " + totalStreams   + " s");
                        //System.out.println("| HTM        : " + totalHTMs      + " s");
                        System.out.println("| DB con     : " + totalDBscon    + " s");
                        //System.out.println("| DB sel     : " + totalDBssel    + " s");
                        System.out.println("| DB ins     : " + totalDBsins    + " s");
                        //System.out.println("| DB close   : " + totalDBscls    + " s");
                        //System.out.println("| DB tot     : " + totalDBs       + " s");
                        //System.out.println("| IO         : " + totalIOs       + " s");
                        //System.out.println("|              -------                |");
                        //System.out.println("|              " + subtotals      + " s");
                        //System.out.println("|                                     |");
                        //System.out.println("| TOTAL      : " + totals         + " s");
                        System.out.println("|                                     |");
                        System.out.println("+-------------------------------------+");
        		/*BufferedWriter out = new BufferedWriter(new FileWriter(logFile, true));
                        out.write(obsNumber + ";" + totalStreams + ";" + totalHTMs + ";" + 
				totalDBscon + ";" + totalDBssel + ";" + totalDBsins + ";" + totalDBscls + ";" + totalDBs + ";" + 
				subtotals + ";" + totals + "\n");
                        out.close();*/
			con.close();

		} catch (SQLException sqle) {
			System.err.println("SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("SQLException: " + sqle.getMessage());
			System.exit(1);
		} catch (HTMException e) {
                        System.err.println(e.getMessage());
			System.exit(1);
                /*} catch (IOException e) {
                        System.err.println("-------------------------------------------------------");
                        System.err.println("- IOException @ writeProcTimes");
                        System.err.println("- IOException Message: " + e.getMessage());
                        System.err.println("-------------------------------------------------------");
                        System.exit(1);*/
		} catch (Exception e) {
			System.err.println("Exception in main");
                        System.err.println(e.getMessage());
			System.exit(1);
		}
	}

        public static void insertFiles(PreparedStatement pstmt, FitsFile f) throws SQLException {
                int i = 1;
                try {
                        pstmt.setInt(i++, f.getId());
                        pstmt.setInt(i++, f.getType());
                        pstmt.setString(i++, f.getIn());
                        pstmt.setString(i++, f.getOut());
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertFiles");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- FitsFile Properties: " + f.getId() + "; " + f.getType() + "; " + f.getIn() + "; " + f.getOut());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertFrequencyBands(PreparedStatement pstmt, FrequencyBands fb) throws SQLException {
                int i = 1;
		double[] freqBandStart = fb.getFreqBandStart();
		double[] freqBandEnd = fb.getFreqBandEnd();
                try {
                        pstmt.setInt(i++, fb.getFreqBandId());
			for (int j = 0; j < freqBandStart.length; j++) {
	                        pstmt.setDouble(i++, freqBandStart[j]);
        	                pstmt.setDouble(i++, freqBandEnd[j]);
			}
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertFrequencyBands");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertEffectiveFrequency(PreparedStatement pstmt, EffectiveFrequency ef) throws SQLException {
                int i = 1;
		Double[] freqEff = ef.getFreqEff();
		/*System.out.println("freqEff.length = " + freqEff.length);
		for (int t = 0; t < freqEff.length; t++) {
			System.out.println("freqEff[" + t + "] = " + freqEff[t].doubleValue());
		}*/
                try {
                        pstmt.setInt(i++, ef.getFreqEffId());
                        pstmt.setInt(i++, ef.getBandId());
			for (int j = 0; j < freqEff.length; j++) {
	                        if (freqEff[j] != null) {
					pstmt.setDouble(i++, freqEff[j].doubleValue());
				} else {
					//pstmt.setNull(i++, java.sql.Types.DOUBLE, "");//NOT SUPPORTED
					pstmt.setNull(i++, java.sql.Types.DOUBLE);
					//pstmt.setDouble(i++, 0);
				}
			}
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertEffectiveFrequency");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertIntegrationStartTimes(PreparedStatement pstmt, int id, long starttime) throws SQLException {
                int i = 1;
                try {
                        pstmt.setInt(i++, id);
                        pstmt.setLong(i++, starttime);
                        pstmt.executeUpdate();
			//System.out.println("Inserted into intstarttimes: " + id + "; " + starttime);
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertIntegrationStartTimes");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- IntegrationStartTime Properties: " + id + "; " + starttime);
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertClassification(PreparedStatement pstmt, Classification cl) throws SQLException {
                int i = 1;
                try {
                        pstmt.setInt(i++, cl.getClassId());
                        pstmt.setShort(i++, cl.getType());
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertClassification");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertObservation(PreparedStatement pstmt, Observation obs) throws SQLException {
                int i = 1;
                try {
                        pstmt.setInt(i++, obs.getObsId());
                        pstmt.setLong(i++, obs.getTimeStart());
                        pstmt.setLong(i++, obs.getTimeEnd());
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertObservation");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertSoftwareVersion(PreparedStatement pstmt, SoftwareVersions swv) throws SQLException {
                int i = 1;
                try {
                        pstmt.setInt(i++, swv.getSwVrsId());
                        pstmt.setInt(i++, swv.getReposId());
                        pstmt.setInt(i++, swv.getDbId());
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertSoftwareVersion");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertSrc(PreparedStatement pstmt, org.lofar.data.catalog.Source src) throws SQLException {
		int i = 1;
                try {
                        pstmt.setInt(i++, src.getSrcId());
                        pstmt.setInt(i++, src.getObsId());
                        pstmt.setInt(i++, src.getClassId());
                        pstmt.setLong(i++, src.getHtmId());
                        pstmt.setDouble(i++, src.getRA());
                        pstmt.setDouble(i++, src.getDec());
                        pstmt.setDouble(i++, src.getRAErr());
                        pstmt.setDouble(i++, src.getDecErr());
                        pstmt.setDouble(i++, src.getSpectralIndex());
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertSrc");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertMeasurements(PreparedStatement pstmt, Measurement ms) throws SQLException {
                int i = 1;
		Double[] stokesI = ms.getStokesI();
		Double[] stokesQ = ms.getStokesQ();
		Double[] stokesU = ms.getStokesU();
		Double[] stokesV = ms.getStokesV();
		Double[] stokesIErr = ms.getStokesIErr();
		Double[] stokesQErr = ms.getStokesQErr();
		Double[] stokesUErr = ms.getStokesUErr();
		Double[] stokesVErr = ms.getStokesVErr();
                try {
                        //pstmt.setLong(i++, fb.getMsId());
                        pstmt.setInt(i++, ms.getSrcId());
                        pstmt.setInt(i++, ms.getFreqEffId());
                        pstmt.setInt(i++, ms.getIntegrTimeStartId());
                        pstmt.setInt(i++, ms.getFileId());
                        pstmt.setInt(i++, ms.getSwVrsId());
			for (int j = 0; j < stokesI.length; j++) {
				//System.out.println("j = " + j);
	                        pstmt.setDouble(i++, stokesI[j].doubleValue());
				if (stokesQ != null && stokesQ[j] != null) {
                                        pstmt.setDouble(i++, stokesQ[j].doubleValue());
                                } else {
                                        //pstmt.setNull(i++, java.sql.Types.DOUBLE, "");//NOT SUPPORTED TODO: MonetDB
                                        pstmt.setDouble(i++, 0);
                                }
				if (stokesU != null && stokesU[j] != null) {
                                        pstmt.setDouble(i++, stokesU[j].doubleValue());
                                } else {
                                        //pstmt.setNull(i++, java.sql.Types.DOUBLE, "");
                                        pstmt.setDouble(i++, 0);
                                }
				if (stokesV != null && stokesV[j] != null) {
                                        pstmt.setDouble(i++, stokesV[j].doubleValue());
                                } else {
                                        //pstmt.setNull(i++, java.sql.Types.DOUBLE, "");
                                        pstmt.setDouble(i++, 0);
                                }
        	                pstmt.setDouble(i++, stokesIErr[j].doubleValue());
				if (stokesQErr != null && stokesQErr[j] != null) {
                                        pstmt.setDouble(i++, stokesQErr[j].doubleValue());
                                } else {
                                        //pstmt.setNull(i++, java.sql.Types.DOUBLE, "");
                                        pstmt.setDouble(i++, 0);
                                }
				if (stokesUErr != null && stokesUErr[j] != null) {
                                        pstmt.setDouble(i++, stokesUErr[j].doubleValue());
                                } else {
                                        //pstmt.setNull(i++, java.sql.Types.DOUBLE, "");
                                        pstmt.setDouble(i++, 0);
                                }
				if (stokesVErr != null && stokesVErr[j] != null) {
                                        pstmt.setDouble(i++, stokesVErr[j].doubleValue());
                                } else {
                                        //pstmt.setNull(i++, java.sql.Types.DOUBLE, "");
                                        pstmt.setDouble(i++, 0);
                                }
			}
			//for (int k = 0; k < ms.getProps().length; k++) {
				//System.out.println("ms.getProps()[" + k + "] = " + ms.getProps()[k]);
			//}
                        int eu = pstmt.executeUpdate();
			//System.out.println("eu = " + eu);
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertMeasurements");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

	private static void doFiles(PreparedStatement ps, int fileId, String inname) throws SQLException {
		FitsFile f = new FitsFile();
		f.setId(fileId);
		f.setType(2);
		f.setIn(inname);
		f.setOut(null);//TODO: but for now is sufficient
		insertFiles(ps, f);
	}

	public static int insertMS(Statement st, Measurement ms) 
	throws SQLException {

		int inserted = 0;
	        StringBuffer query = new StringBuffer();

        	try {
                	query.append("INSERT INTO measurements_1s  " +
                                                "(              " +
                                                " SRC_ID          " +
                                                ",FREQEFF_ID      " +
                                                ",INTEGRTIME_S_ID " +
                                                ",FILE_ID         " +
                                                ",SWVRS_ID        " +
                                                ",I1              " +
                                                ",Q1              " +
                                                ",U1              " +
                                                ",V1              " +
                                                ",I2              " +
                                                ",Q2              " +
                                                ",U2              " +
                                                ",V2              " +
                                                ",I3              " +
                                                ",Q3              " +
                                                ",U3              " +
                                                ",V3              " +
                                                ",I4              " +
                                                ",Q4              " +
                                                ",U4              " +
                                                ",V4              " +
                                                ",I5              " +
                                                ",Q5              " +
                                                ",U5              " +
                                                ",V5              " +
                                                ",I6              " +
                                                ",Q6              " +
                                                ",U6              " +
                                                ",V6              " +
                                                ",I7              " +
                                                ",Q7              " +
                                                ",U7              " +
                                                ",V7              " +
                                                ",I8              " +
                                                ",Q8              " +
                                                ",U8              " +
                                                ",V8              " +
                                                ",I9              " +
                                                ",Q9              " +
                                                ",U9              " +
                                                ",V9              " +
                                                ",I10             " +
                                                ",Q10             " +
                                                ",U10             " +
                                                ",V10             " +
                                                ",I11             " +
                                                ",Q11             " +
                                                ",U11             " +
                                                ",V11             " +
                                                ",I12             " +
                                                ",Q12             " +
                                                ",U12             " +
                                                ",V12             " +
                                                ",I1_ERR          " +
                                                ",Q1_ERR          " +
                                                ",U1_ERR          " +
                                                ",V1_ERR          " +
                                                ",I2_ERR          " +
                                                ",Q2_ERR          " +
                                                ",U2_ERR          " +
                                                ",V2_ERR          " +
                                                ",I3_ERR          " +
                                                ",Q3_ERR          " +
                                                ",U3_ERR          " +
                                                ",V3_ERR          " +
                                                ",I4_ERR          " +
                                                ",Q4_ERR          " +
                                                ",U4_ERR          " +
                                                ",V4_ERR          " +
                                                ",I5_ERR          " +
                                                ",Q5_ERR          " +
                                                ",U5_ERR          " +
                                                ",V5_ERR          " +
                                                ",I6_ERR          " +
                                                ",Q6_ERR          " +
                                                ",U6_ERR          " +
                                                ",V6_ERR          " +
                                                ",I7_ERR          " +
                                                ",Q7_ERR          " +
                                                ",U7_ERR          " +
                                                ",V7_ERR          " +
                                                ",I8_ERR          " +
                                                ",Q8_ERR          " +
                                                ",U8_ERR          " +
                                                ",V8_ERR          " +
                                                ",I9_ERR          " +
                                                ",Q9_ERR          " +
                                                ",U9_ERR          " +
                                                ",V9_ERR          " +
                                                ",I10_ERR         " +
                                                ",Q10_ERR         " +
                                                ",U10_ERR         " +
                                                ",V10_ERR         " +
                                                ",I11_ERR         " +
                                                ",Q11_ERR         " +
                                                ",U11_ERR         " +
                                                ",V11_ERR         " +
                                                ",I12_ERR         " +
                                                ",Q12_ERR         " +
                                                ",U12_ERR         " +
                                                ",V12_ERR         " +
                                                ")                " +
                                        "VALUES                   " +
                                                "(		  ");
	                query.append(ms.getSrcId() + 
					", " + ms.getFreqEffId() + 
					", " + ms.getIntegrTimeStartId() + 
					", " + ms.getFileId() + 
					", " + ms.getSwVrsId());
			for (int i = 0; i < ms.getStokesI().length; i++) {
				query.append(", " + ms.getStokesI()[i].doubleValue());
			}
			for (int i = 0; i < ms.getStokesQ().length; i++) {
				query.append(", " + ms.getStokesQ()[i].doubleValue());
			}
			for (int i = 0; i < ms.getStokesU().length; i++) {
				query.append(", " + ms.getStokesU()[i].doubleValue());
			}
			for (int i = 0; i < ms.getStokesV().length; i++) {
				query.append(", " + ms.getStokesV()[i].doubleValue());
			}
			for (int i = 0; i < ms.getStokesIErr().length; i++) {
				query.append(", " + ms.getStokesIErr()[i].doubleValue());
			}
			for (int i = 0; i < ms.getStokesQErr().length; i++) {
				query.append(", " + ms.getStokesQErr()[i].doubleValue());
			}
			for (int i = 0; i < ms.getStokesUErr().length; i++) {
				query.append(", " + ms.getStokesUErr()[i].doubleValue());
			}
			for (int i = 0; i < ms.getStokesVErr().length; i++) {
				query.append(", " + ms.getStokesVErr()[i].doubleValue());
			}
			query.append(");");
                	st.executeUpdate(query.toString());
                	inserted++;
			//System.out.println("Query: " + query.toString() + " correctly inserted");
	        } catch (SQLException sqle) {
        		System.err.println("-------------------------------------------------------");
                	System.err.println("- SQLException @ query: " + query.toString());
                        System.err.println("- SQLException ErrorCode: " + sqle.getErrorCode());
	                System.err.println("- SQLException SQLState: " + sqle.getSQLState());
        	        System.err.println("- SQLException Message: " + sqle.getMessage());
                	System.err.println("- This query will not be inserted");
                        System.err.println("-------------------------------------------------------");
			System.exit(1);
	                //throw new Exception("query: " + query.toString() + "cannot be inserted \n See errorlog");
	        }
        	return inserted;

	}


}
