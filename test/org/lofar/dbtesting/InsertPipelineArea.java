package org.lofar.dbtesting;

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
import org.lofar.data.pipeline.*;
import org.lofar.services.*;
import org.lofar.util.DatabaseManager;

/** 
 *  This program creates simulated data to be loaded into the pipeline area;
 *  For each table a file is created with data to be loaded
 *  Processing times are recorded in log files in dirs 
 *  files/dbtests/pipeline/dbname/infile
 *  files/dbtests/pipeline/dbname/insert
 *  HtmIds for these sources will be calculated 
 */

/**
 * TODO: Input needed (from SExtractor) for frequency, stokes, logtime, observation, beam
 */
public class InsertPipelineArea {
	
	// We assume 1 image per second
	private static int Nimages = 0; 
	// Every image has Nbands, so the number of rows in frequencyband are Nimages * Nbands
	private static int Nbands = 0;
	private static int Nbeams = 0;
	// Number of sources are per image, so in the end we have Nsources * Nbands * Nimages rows in extractedsources
	private static int Nsources = 0;
	private static byte logid = 1;
	private static boolean writeToFile = true;
	private static String database = null;
	private static String testdir = null;


	private static BufferedWriter outBeams;
	private static BufferedWriter outExtractedsources; 
	private static BufferedWriter outFiles; 
	private static BufferedWriter outFrequencyband; 
	private static BufferedWriter outIntegrationtimes; 
	private static BufferedWriter outObservation;
	private static BufferedWriter outResolution; 

	private static Format formatter = new SimpleDateFormat("yyyy-MM-dd-HH:mm:ss:SSS");
	protected static String maxObsId = "SELECT MAX(obsid) FROM observation;";
	protected static String insertObservation = "INSERT INTO observation  " +
                                                //"(OBSID         " +
                                                "(TIME_S        " +
                                                //",TIME_E        " +
                                                ")              " +
                                        "VALUES                 " +
                                                //"(?             " +
                                                "(?             " +
                                                //",?             " +
                                                ");";
	protected static String insertObservationMonetDB = "INSERT INTO observation  " +
                                                "(OBSID         " +
                                                ",TIME_S        " +
                                                //",TIME_E        " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                //",?             " +
                                                ");";
	protected static String insertResolution = "INSERT INTO resolution  " +
                                                "(RESID         " +
                                                ",MAJOR         " +
                                                ",MINOR         " +
                                                ",PA            " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";

	protected static String maxFileId = "SELECT MAX(fileid) FROM files;";
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
	protected static String insertBeams = "INSERT INTO beams  " +
                                                "(BEAMID        " +
                                                ",OBSERVATION_ID" +
                                                ",RESOLUTION_ID " +
                                                //",FILEID        " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                               // ",?             " +
                                                ");";
	/*protected static String maxIntegrationStartId = "SELECT MAX(integrtime_sid) FROM integrationstarttimes;";
	protected static String insertIntegrationStartTimes = "INSERT INTO integrationstarttimes  " +
                                                //"(INTEGRTIME_SID" +
                                                "(INTEGRTIME_S  " +
                                                ")              " +
                                        "VALUES                 " +
                                                //"(?             " +
                                                "(?             " +
                                                ");";*/
	protected static String maxIntegrId = "SELECT MAX(integrid) FROM integrationtimes;";
	protected static String insertIntegrationTimes = "INSERT INTO integrationtimes  " +
                                                "(INTEGRID      " +
                                                ",FILE_ID       " +
                                                //",LOGSERIES     " +
                                                ",TIME_S        " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                //",?             " +
                                                ",?             " +
                                                ");";
	protected static String maxFreqId = "SELECT MAX(freqid) FROM frequencyband;";
	protected static String insertFrequencyBand = "INSERT INTO frequencyband  " +
                                                "(FREQID        " +
                                                ",FREQ_S        " +
                                                ",FREQ_E        " +
                                                ",FREQ_EFF      " +
                                                ")              " +
                                        "VALUES                 " +
                                                "(?             " +
                                                ",?             " +
                                                ",?             " +
                                                ",?             " +
                                                ");";
	protected static String insertExtractedSources = "INSERT INTO extractedsources" +
                                                "(              " +
						//" XTRSRCID      " +
                                                " BEAM_ID       " +
                                                ",FREQ_ID       " +
                                                ",INTEGR_ID     " +
                                                ",LOGID         " +
                                                ",HTMID         " +
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
                                                "(		" +
						//" ?             " +
                                                " ?             " +
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


	/**
	 * main handles one votable file that consists of several extracted sources, 
	 * (Before beam, observation and frequencyband data is stored by an init
	 * (TODO: "observation, beams, resolution, frequencyband" tables)
	 * This method stores image meta data like the name of the file and integration
	 * start times and durations.
	 */
        public static void main(String[] args) throws IOException {
	
		database = args[0];
		testdir = args[1];
		writeToFile = Boolean.parseBoolean(args[2]);
		Nimages = Integer.parseInt(args[3]);
		Nbands = Integer.parseInt(args[4]);
		Nbeams = Integer.parseInt(args[5]);
		Nsources = Integer.parseInt(args[6]);

                System.out.println("+-------------------------------------+");
                System.out.println("|                                     |");
                if (writeToFile) System.out.println("| data is written to INFILEs          |");
                if (writeToFile) System.out.println("|                                     |");
                System.out.println("| Nimages  = " + Nimages  + "         |");
                System.out.println("| Nbands   = " + Nbands   + "         |");
                System.out.println("| Nbeams   = " + Nbeams   + "         |");
                System.out.println("| Nsources = " + Nsources + "         |");
                System.out.println("|                                     |");
                System.out.println("| PROCESSING TIMES                    |");

		long start = System.currentTimeMillis();
		long end = 0, total = 0;
		long startHTM = 0, endHTM = 0, totalHTM = 0;
		long startDB = 0, endDB = 0, totalDB = 0;
		long startDBcon = 0, endDBcon = 0, totalDBcon = 0;
		long startDBins = 0, endDBins = 0, totalDBins = 0;
		long startDBsel = 0, endDBsel = 0, totalDBsel = 0;
		long startDBcls = 0, endDBcls = 0, totalDBcls = 0;
		long startFromInfile = 0, endFromInfile = 0, totalFromInfile = 0;
		long startStream = 0, endStream = 0, totalStream = 0, startIO = 0, endIO = 0, totalIO = 0;
		float subtotals = 0, totals = 0, totalHTMs = 0;
		float totalDBs = 0, totalDBscon = 0, totalDBsins = 0, totalDBssel = 0, totalDBscls = 0, totalFromInfiles = 0;
		float totalStreams = 0, totalIOs = 0;
		int obsNumber = 0;
		int nBeams = 0, nObservation = 0, nFiles = 0, nIntegrationtimes = 0, nFrequencyband = 0, nResolution = 0, nExtractedsources = 0;

		double ra = 0, dec = 0, flux_max = 0, flux_iso = 0, flux_isocor = 0, flux_aper = 0, flux_auto = 0, flux_quotient = 0;
		double dra = 0, ddec = 0, frms_max = 0, frms_iso = 0, frms_isocor = 0, frms_aper = 0, frms_auto = 0;
		double iso_areaf_image = 0;
		long htmid = 0L, htmIdNumber = 0L;
		int rangeLevel = 20;
		int lofarLevel = 10;

		int freqId = 0, integrId = 0, highFreqId = 0;
		
		try {
			/**
			 * De basedir is the current working directory
			 */
			//String basedir = "files/dbtests/pipeline/";
			String basedir = System.getProperty("user.dir");
			//String databasedir = basedir + database + "/"; // either mysql or monetdb
			String databasedir = basedir + "/" + getDir(database);
			/*String testdir;
			if (writeToFile) {
				testdir = databasedir + "/";
			} else {
				testdir = databasedir + "insert/";
			}*/
			//And create this this testing dir
			String params = "Nimg" + Nimages + "-Nf" + Nbands + "-Nbm" + Nbeams + "-Ns" + Nsources;
			String paramdir = testdir + params + "/";
			String logFile = testdir + params + ".log";

			//String fromFile = paramdir + "insert.pipeline.sql";
			
			(new File(paramdir)).mkdirs();
			String beamsFile = paramdir + "beams.txt";
			String extractedsourcesFile = paramdir + "extractedsources.txt";
			String filesFile = paramdir + "files.txt";
			String frequencybandFile = paramdir + "frequencyband.txt";
			String integrationtimesFile = paramdir + "integrationtimes.txt";
			String observationFile = paramdir + "observation.txt";
			String resolutionFile = paramdir + "resolution.txt";

			//Delete old, existing files
			//(new File(logFile)).delete();
			(new File(beamsFile)).delete();
			(new File(extractedsourcesFile)).delete();
			(new File(filesFile)).delete();
			(new File(frequencybandFile)).delete();
			(new File(integrationtimesFile)).delete();
			(new File(observationFile)).delete();
			(new File(resolutionFile)).delete();
			System.out.println("After all files deleted");

			/*String indir = null;
			if ("mysql".equals(database)) {
				indir = "../../../java/";
			} else {
				indir = "/scratch/bscheers/java/";
			}
			String inBeams = indir + beamsFile;
			String inExtractedsources = indir + extractedsourcesFile;
			String inFiles = indir + filesFile;
			String inFrequencyband = indir + frequencybandFile;
			String inIntegrationtimes = indir + integrationtimesFile;
			String inObservation = indir + observationFile;
			String inResolution = indir + resolutionFile;*/

			String inBeams = beamsFile;
			String inExtractedsources = extractedsourcesFile;
			String inFiles = filesFile;
			String inFrequencyband = frequencybandFile;
			String inIntegrationtimes = integrationtimesFile;
			String inObservation = observationFile;
			String inResolution = resolutionFile;

			//outFromFile = new BufferedWriter(new FileWriter(fromFile, true));
			outBeams = new BufferedWriter(new FileWriter(beamsFile, true));
			outExtractedsources = new BufferedWriter(new FileWriter(extractedsourcesFile, true));
			outFiles = new BufferedWriter(new FileWriter(filesFile, true));
			outFrequencyband = new BufferedWriter(new FileWriter(frequencybandFile, true));
			outIntegrationtimes = new BufferedWriter(new FileWriter(integrationtimesFile, true));
			outObservation = new BufferedWriter(new FileWriter(observationFile, true));
			outResolution = new BufferedWriter(new FileWriter(resolutionFile, true));
			//System.out.println("After all files created");

			startDB = System.currentTimeMillis();
			startDBcon = startDB;
	                Connection con = DatabaseManager.getConnection(database);
			//boolean b = con.isClosed();
			//System.out.println("Connection made");
			endDBcon = System.currentTimeMillis();
			totalDBcon = endDBcon - startDBcon;
			Statement st = con.createStatement();
			//System.out.println("Statement made");

			PreparedStatement pstmtMaxObsId = con.prepareStatement(maxObsId);
			PreparedStatement pstmtMaxFilId = con.prepareStatement(maxFileId);
			//PreparedStatement pstmtMaxIntSTId = con.prepareStatement(maxIntegrationStartId);
			PreparedStatement pstmtMaxIntTId = con.prepareStatement(maxIntegrId);
			PreparedStatement pstmtMaxFreqId = con.prepareStatement(maxFreqId);
			//System.out.println("Nearly all prepared statements");

			PreparedStatement pstmtObs = con.prepareStatement(insertObservation);
			//System.out.println("Nearly all prepared statements 1a");
			PreparedStatement pstmtObsMonetDB = con.prepareStatement(insertObservationMonetDB);
			//System.out.println("Nearly all prepared statements 1b");
			PreparedStatement pstmtRes = con.prepareStatement(insertResolution);
			//System.out.println("Nearly all prepared statements 2");
			PreparedStatement pstmtBeam = con.prepareStatement(insertBeams);
			//System.out.println("Nearly all prepared statements 3");
			PreparedStatement pstmtFil = con.prepareStatement(insertFiles);
			//System.out.println("Nearly all prepared statements 4");
			PreparedStatement pstmtIntT = con.prepareStatement(insertIntegrationTimes);
			//System.out.println("Nearly all prepared statements 5");
			PreparedStatement pstmtFreqBand = con.prepareStatement(insertFrequencyBand);
			//System.out.println("Nearly all prepared statements 6");

			PreparedStatement pstmtXtrSrc = con.prepareStatement(insertExtractedSources);
			//System.out.println("All prepared statements");

			Random rand = new Random();

			startDBsel = System.currentTimeMillis();
			int obsId = selectObsId(pstmtMaxObsId);
			int fileId = selectFileId(pstmtMaxFilId);
			int maxIntegrId = selectIntegrId(pstmtMaxIntTId);
			//int maxFreqId = selectFreqId(pstmtMaxFreqId);
			endDBsel = System.currentTimeMillis();
			totalDBsel = totalDBsel + (endDBsel - startDBsel);
			if (writeToFile) {
				obsId = 1;
				fileId = 1;
				maxIntegrId = 1;
			}

			long obsTimeStart = 20070207095921000L;
			if ("mysql".equals(database)) setFKeyCheck(st, 0);
			Observation obs = new Observation();
			obs.setObsId(1);
			obs.setTimeStart(obsTimeStart); 
			
			startDBins = System.currentTimeMillis();
			//System.out.println("Before insert Obs");
			if ("monetdb".equals(database)) {
				insertObservation(pstmtObsMonetDB, obs, writeToFile);
			} else if ("monetdb64".equals(database)) {
				insertObservation(pstmtObsMonetDB, obs, writeToFile);
			} else if ("mysql".equals(database)) {
				insertObservation(pstmtObs, obs, writeToFile);
			} 
			nObservation = 1;
			//System.out.println("After insert Obs");
			endDBins = System.currentTimeMillis();
			totalDBins = totalDBins + (endDBins - startDBins);
			//TODO: implement Resolution in Beam;
			Resolution res = new Resolution();
			res.setResId(1);
			res.setMajor(1);
			res.setMinor(1);
			res.setPA(1);
			startDBins = System.currentTimeMillis();
			insertResolution(pstmtRes, res, writeToFile);
			nResolution = 1;
			endDBins = System.currentTimeMillis();
			totalDBins = totalDBins + (endDBins - startDBins);
			//int Nbeams = 20;
			Beam bm;
			//System.out.println("Before loop Beams");
			for (int i = 0; i < Nbeams; i++) {
				bm = new Beam();
				bm.setBeamId(i);
				bm.setObsId(obs.getObsId());
				bm.setResId(res.getResId());
				startDBins = System.currentTimeMillis();
				//System.out.println("Before insert Beams");
				insertBeams(pstmtBeam, bm, writeToFile);
				//System.out.println("After insert Beams");
				endDBins = System.currentTimeMillis();
				totalDBins = totalDBins + (endDBins - startDBins);
			}
			nBeams = Nbeams;

			FitsFile f;
			String fin = "LFR";
			IntegrationTimes it;
			ExtractedSource xsrc;
			FrequencyBand fb;
			StringBuffer sb;
			long intTimeStart = obsTimeStart + 3000L;
			int xsrcid = 0;
			// We will process Nimages images
			highFreqId = 0;
			//System.out.println("Before loop");
			for (int i = 0; i < Nimages; i++) {
				f = new FitsFile();
		                f.setId(i);
        		        f.setType(2);
				sb = new StringBuffer(fin);
				sb.append(i);
                		f.setIn(sb.toString());
		                f.setOut(null);
				startDBins = System.currentTimeMillis();
				insertFiles(pstmtFil, f, writeToFile);
				endDBins = System.currentTimeMillis();
				totalDBins = totalDBins + (endDBins - startDBins);
				intTimeStart += 1000L;
				integrId = maxIntegrId + i;
				it = new IntegrationTimes();
				it.setIntegrId(integrId);
				it.setFileId(f.getId());
				//it.setLogseries((short)1);
				it.setTimeStart(intTimeStart);
				startDBins = System.currentTimeMillis();
				insertIntegrationTimes(pstmtIntT, it, writeToFile);
				endDBins = System.currentTimeMillis();
				totalDBins = totalDBins + (endDBins - startDBins);
				// We assume to have Nbands frequency bands
				if (writeToFile) {
					highFreqId++;
				} else {
					highFreqId = selectFreqId(pstmtMaxFreqId);
				}
				//byte[] b = new byte[1];
				for (int j = 0; j < Nbands; j++) {
					if (writeToFile) {
						highFreqId++;
						freqId = highFreqId;
					} else {
						freqId = highFreqId + j;
					}
					fb = new FrequencyBand();
					fb.setFreqId(freqId);
					// Of course these values mean nothing!
					fb.setFreqStart(rand.nextDouble());
					fb.setFreqEnd(rand.nextDouble());
					fb.setFreqEff(rand.nextDouble());
					startDBins = System.currentTimeMillis();
					insertFrequencyBand(pstmtFreqBand, fb, writeToFile);
					endDBins = System.currentTimeMillis();
					totalDBins = totalDBins + (endDBins - startDBins);
					// And for every band Nsources sources
					//System.out.println("Before inner loop");
					for (int k = 0; k < Nsources; k++) {
						xsrc = new ExtractedSource();
						//outBeams.close(); 
						//outExtractedsources.close(); 
						//outFiles.close(); 
						//outFrequencyband.close(); 
						//outIntegrationtimes.close(); 
						//outObservation.close(); 
						//outResolution.close();
						xsrc.setXtrSrcId(xsrcid++);
						xsrc.setBeamId(rand.nextInt(Nbeams));
	                                        xsrc.setFreqId(fb.getFreqId());
        	                                xsrc.setIntegrId(it.getIntegrId());
                	                        xsrc.setLogId(logid);
                	                        xsrc.setHtmId(Math.abs(rand.nextLong()));
                        	                xsrc.setRA(50 + (6 * rand.nextDouble()));
                                	        xsrc.setDec(70 + (6 * rand.nextDouble()));
                                        	xsrc.setRaErr(0.1 * rand.nextDouble());
	                                        xsrc.setDecErr(0.1 * rand.nextDouble());
        	                                xsrc.setStokesI(rand.nextDouble());
                	                        xsrc.setStokesQ(rand.nextDouble());
                        	                xsrc.setStokesU(rand.nextDouble());
                                	        xsrc.setStokesV(rand.nextDouble());
                                        	xsrc.setStokesIErr(rand.nextDouble());
	                                        xsrc.setStokesQErr(rand.nextDouble());
        	                                xsrc.setStokesUErr(rand.nextDouble());
                	                        xsrc.setStokesVErr(rand.nextDouble());
						startDBins = System.currentTimeMillis();
						insertXtrSrc(pstmtXtrSrc, xsrc, writeToFile);
						endDBins = System.currentTimeMillis();
						totalDBins = totalDBins + (endDBins - startDBins);
					}
				}
				
			}
			nFiles = Nimages;
			nIntegrationtimes = Nimages;
			nFrequencyband = Nimages * Nbands; 
			nExtractedsources = Nsources * Nimages * Nbands;

			if ("mysql".equals(database)) setFKeyCheck(st, 1);

			//System.out.println("Before all close");
			outBeams.close(); 
                        outExtractedsources.close(); 
                        outFiles.close(); 
                        outFrequencyband.close(); 
                        outIntegrationtimes.close(); 
                        outObservation.close(); 
                        outResolution.close();
			//System.out.println("After all close");

			//Here: execute mysql -pcs1 < insert.pipeline.sql
			//System.out.println("Before fromFile");
			/*String file = "../databases/design/sql/insert.pipelineInnoDB.sql";
			BufferedReader fromfile = new BufferedReader(new FileReader(file));
			String str;
			String fromFileStr = null;
		        while ((str = fromfile.readLine()) != null) {
                		fromFileStr = str;
				startFromInfile = System.currentTimeMillis();
				insertFromInfile(st, fromFileStr);
				endFromInfile = System.currentTimeMillis();
				totalFromInfile = totalFromInfile + (endFromInfile - startFromInfile);
			}
			fromfile.close();*/

			startFromInfile = System.currentTimeMillis();
			String loadBeams = loadDataInFile(inBeams, database, nBeams, "beams");
			String loadObservation = loadDataInFile(inObservation, database, nObservation, "observation");
			String loadFiles = loadDataInFile(inFiles, database, nFiles, "files");
			String loadIntegrationtimes = loadDataInFile(inIntegrationtimes, database, nIntegrationtimes, "integrationtimes");
			String loadFrequencyband = loadDataInFile(inFrequencyband, database, nFrequencyband, "frequencyband");
			String loadResolution = loadDataInFile(inResolution, database, nResolution, "resolution");
			String loadExtractedsources = loadDataInFile(inExtractedsources, database, nExtractedsources, "extractedsources");
			if ("mysql".equals(database)) {
				setFKeyCheck(st, 0);
				insertFromInfile(st, loadBeams);
				insertFromInfile(st, loadObservation);
				insertFromInfile(st, loadFiles);
				insertFromInfile(st, loadIntegrationtimes);
				insertFromInfile(st, loadFrequencyband);
				insertFromInfile(st, loadResolution);
				insertFromInfile(st, loadExtractedsources);
				setFKeyCheck(st, 1);
			} else if ("monetdb".equals(database) | "monetdb64".equals(database)) {
				StringBuffer copies = new StringBuffer();
				copies.append(loadObservation );
				copies.append("\n");
				copies.append(loadResolution);
				copies.append("\n");
				copies.append(loadBeams);
				copies.append("\n");
				copies.append(loadFiles);
				copies.append("\n");
				copies.append(loadIntegrationtimes);
				copies.append("\n");
				copies.append(loadFrequencyband);
				copies.append("\n");
				copies.append(loadExtractedsources);
				copies.append("\n");
				insertTransaction(st, copies);
			}
			endFromInfile = System.currentTimeMillis();
			totalFromInfile = totalFromInfile + (endFromInfile - startFromInfile);
			
			System.out.println("(new File(beamsFile)).length(): " + (new File(beamsFile)).length() + " Byte");
			System.out.println("(new File(extractedsourcesFile)).length(): " + (new File(extractedsourcesFile)).length() + " Byte");
			System.out.println("(new File(filesFile)).length(): " + (new File(filesFile)).length() + " Byte");
			System.out.println("(new File(frequencybandFile)).length(): " + (new File(frequencybandFile)).length() + " Byte");
			System.out.println("(new File(integrationtimesFile)).length(): " + (new File(integrationtimesFile)).length() + " Byte");
			System.out.println("(new File(observationFile)).length(): " + (new File(observationFile)).length() + " Byte");
			System.out.println("(new File(resolutionFile)).length(): " + (new File(resolutionFile)).length() + " Byte");

			/*(new File(beamsFile)).delete();
                        (new File(extractedsourcesFile)).delete();
                        (new File(filesFile)).delete();
                        (new File(frequencybandFile)).delete();
                        (new File(integrationtimesFile)).delete();
                        (new File(observationFile)).delete();
                        (new File(resolutionFile)).delete();
                        (new File(paramdir)).delete();*/
			
                        totalHTMs = totalHTM / 1000f;
                        totalDBscon = totalDBcon / 1000f;
                        totalDBssel = totalDBsel / 1000f;
                        totalDBsins = totalDBins / 1000f;
                        totalDBscls = totalDBcls / 1000f;
                        totalDBs = totalDB / 1000f;
                        totalStreams = totalStream / 1000f;
			totalFromInfiles = totalFromInfile / 1000f;
                        //totalIOs = totalIO / 1000f;
                        subtotals = totalStreams + totalHTMs + totalDBs;// + totalIOs;
                        end = System.currentTimeMillis();
                        total = total + (end - start);
                        totals = total / 1000f;
                        //System.out.println("| InputStream: " + totalStreams   + " s");
                        //System.out.println("| HTM        : " + totalHTMs      + " s");
                        //System.out.println("| DB con     : " + totalDBscon    + " s");
                        //System.out.println("| DB sel     : " + totalDBssel    + " s");
                        //if (writeToFile) {
	                //        System.out.println("| totalFromInfiles  : " + totalFromInfiles    + " s");
			//} else {
				System.out.println("| DB      : " + database       + "  ");
				System.out.println("| DB ins  : " + totalDBsins    + " s");
			//}
                        //System.out.println("| DB close   : " + totalDBscls    + " s");
                        //System.out.println("| DB tot     : " + totalDBs       + " s");
                        //System.out.println("| IO         : " + totalIOs       + " s");
                        //System.out.println("|              -------                |");
                        //System.out.println("|              " + subtotals      + " s");
                        //System.out.println("|                                     |");
                        System.out.println("| TOTAL      : " + totals         + " s");
                        System.out.println("|                                     |");
                        System.out.println("| See results in: " + logFile);
                        //System.out.println("| TOTAL      : " + totals         + " s");
                        System.out.println("|                                     |");
                        System.out.println("+-------------------------------------+\n");
        		BufferedWriter out = new BufferedWriter(new FileWriter(logFile, true));
                        //out.write("Nimages ; Nbands ; Nbeams ; Nsources/image ; InsertTime (sec)\n");
                        out.write(Nimages + "\t" + Nbands + "\t" + Nbeams + "\t" + Nsources + "\t" + totalDBsins + "\n");
                        out.close();
			con.close();

		} catch (SQLException sqle) {
			System.err.println("SQLException in main");
			System.err.println("SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("SQLException: " + sqle.getMessage());
			System.exit(1);
		/*} catch (HTMException e) {
                        System.err.println(e.getMessage());
			System.exit(1);*/
                } catch (IOException e) {
                        System.err.println("-------------------------------------------------------");
                        System.err.println("- IOException @ writeProcTimes");
                        System.err.println("- IOException Message: " + e.getMessage());
                        System.err.println("-------------------------------------------------------");
                        System.exit(1);
		}
	}

	public static String getDir(String database) {
		Format formatter = new SimpleDateFormat("yyyy-MM-dd-HH:mm");
		java.util.Date date = new java.util.Date();
		String dirext = formatter.format(date);
		return database + dirext;
	}

        public static void insertFiles(PreparedStatement pstmt, FitsFile f, boolean writeToFile) throws SQLException {
                int i = 1;
                try {
			if (writeToFile) {
				outFiles.write("" + f.getId() + "," + f.getType() + "," + f.getIn() + "," + f.getOut() + "\n");
			} else {
		                pstmt.setInt(i++, f.getId());
        		        pstmt.setInt(i++, f.getType());
                	        pstmt.setString(i++, f.getIn());
                      		pstmt.setString(i++, f.getOut());
		                pstmt.executeUpdate();
			}
                } catch (IOException ioe) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- IOException @ insertFiles()");
                        sb.append("\n- IOException @ int i: " + i);
                        sb.append("\n- IOException Cause     : " + ioe.getCause());
                        sb.append("\n- IOException Message   : " + ioe.getMessage());
                        sb.append("\n- IOException StackTrace: " + ioe.getStackTrace());
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ insertFiles()");
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

        /*public static void insertIntegrationStartTimes(PreparedStatement pstmt, long startTime) throws SQLException, IOException {
                int i = 1;
                try {
                        //pstmt.setInt(i++, id);
                        pstmt.setLong(i++, startTime);
                        pstmt.executeUpdate();
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- IntegrationStartTime Properties: " + startTime);
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }*/

        public static void insertIntegrationTimes(PreparedStatement pstmt, IntegrationTimes it, boolean writeToFile) throws SQLException {
                int i = 1;
                try {
			if (writeToFile) {
				outIntegrationtimes.write("" + it.getIntegrId() + "," + it.getFileId() + "," + it.getTimeStart() + "\n");
			} else {
	                        pstmt.setInt(i++, it.getIntegrId());
        	                pstmt.setInt(i++, it.getFileId());
                	        //pstmt.setShort(i++, it.getLogseries());
                        	pstmt.setLong(i++, it.getTimeStart());
	                        pstmt.executeUpdate();
			}
                } catch (IOException ioe) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- IOException @ insertIntegratioTimes()");
                        sb.append("\n- IOException @ int i: " + i);
                        sb.append("\n- IOException Cause     : " + ioe.getCause());
                        sb.append("\n- IOException Message   : " + ioe.getMessage());
                        sb.append("\n- IOException StackTrace: " + ioe.getStackTrace());
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- IntegrationtTime Properties: " + it.getIntegrId() + "; " + it.getFileId() + "; " + it.getLogseries() + "; " + it.getTimeStart());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        public static void insertXtrSrc(PreparedStatement pstmt, ExtractedSource src, boolean writeToFile) throws SQLException {
		int i = 1;
                try {
			if ("monetdb64".equals(database) || "monetdb".equals(database)) {
				if (writeToFile) {
					outExtractedsources.write("" + 
							src.getXtrSrcId() + "," + 
							src.getBeamId() + "," + 
							src.getFreqId() + "," +
							src.getIntegrId() + "," +
							src.getLogId() + "," +
							src.getHtmId() + "," +
							src.getRA() + "," +
							src.getDec() + "," +
							src.getRaErr() + "," +
							src.getDecErr() + "," +
							src.getStokesI() + "," +
							src.getStokesQ() + "," +
							src.getStokesU() + "," +
							src.getStokesV() + "," +
							src.getStokesIErr() + "," +
							src.getStokesQErr() + "," +
							src.getStokesUErr() + "," +
							src.getStokesVErr() + "\n");
				} else {
	                        	pstmt.setInt(i++, src.getXtrSrcId());
	        	                pstmt.setInt(i++, src.getBeamId());
        	        	        pstmt.setInt(i++, src.getFreqId());
	        	                pstmt.setInt(i++, src.getIntegrId());
        	        	        pstmt.setByte(i++, src.getLogId());
                	        	pstmt.setLong(i++, src.getHtmId());
	                        	pstmt.setDouble(i++, src.getRA());
		                        pstmt.setDouble(i++, src.getDec());
        		                pstmt.setDouble(i++, src.getRaErr());
                		        pstmt.setDouble(i++, src.getDecErr());
                        		pstmt.setDouble(i++, src.getStokesI());
		                        pstmt.setDouble(i++, src.getStokesQ());
        		                pstmt.setDouble(i++, src.getStokesU());
                		        pstmt.setDouble(i++, src.getStokesV());
                        		pstmt.setDouble(i++, src.getStokesIErr());
		                	pstmt.setDouble(i++, src.getStokesQErr());
	                  	        pstmt.setDouble(i++, src.getStokesUErr());
		                        pstmt.setDouble(i++, src.getStokesVErr());
        		                pstmt.executeUpdate();
				}
			} else if ("mysql".equals(database)) {
				if (writeToFile) {
                                        outExtractedsources.write("" +
                                                        //src.getXtrSrcId() + "," +
                                                        src.getBeamId() + "," +
                                                        src.getFreqId() + "," +
                                                        src.getIntegrId() + "," +
                                                        src.getLogId() + "," +
                                                        src.getHtmId() + "," +
                                                        src.getRA() + "," +
                                                        src.getDec() + "," +
                                                        src.getRaErr() + "," +
                                                        src.getDecErr() + "," +
                                                        src.getStokesI() + "," +
                                                        src.getStokesQ() + "," +
                                                        src.getStokesU() + "," +
                                                        src.getStokesV() + "," +
                                                        src.getStokesIErr() + "," +
                                                        src.getStokesQErr() + "," +
                                                        src.getStokesUErr() + "," +
                                                        src.getStokesVErr() + "\n");
                                } else {
                                        //pstmt.setInt(1, src.getXtrSrcId());
                                        pstmt.setInt(i++, src.getBeamId());
                                        pstmt.setInt(i++, src.getFreqId());
                                        pstmt.setInt(i++, src.getIntegrId());
                                        pstmt.setByte(i++, src.getLogId());
                                        pstmt.setLong(i++, src.getHtmId());
                                        pstmt.setDouble(i++, src.getRA());
                                        pstmt.setDouble(i++, src.getDec());
                                        pstmt.setDouble(i++, src.getRaErr());
                                        pstmt.setDouble(i++, src.getDecErr());
                                        pstmt.setDouble(i++, src.getStokesI());
                                        pstmt.setDouble(i++, src.getStokesQ());
                                        pstmt.setDouble(i++, src.getStokesU());
                                        pstmt.setDouble(i++, src.getStokesV());
                                        pstmt.setDouble(i++, src.getStokesIErr());
                                        pstmt.setDouble(i++, src.getStokesQErr());
                                        pstmt.setDouble(i++, src.getStokesUErr());
                                        pstmt.setDouble(i++, src.getStokesVErr());
                                        pstmt.executeUpdate();
				}
			}
                } catch (IOException ioe) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- IOException @ insertXtrSrc()");
                        sb.append("\n- IOException @ int i: " + i);
                        sb.append("\n- IOException Cause     : " + ioe.getCause());
                        sb.append("\n- IOException Message   : " + ioe.getMessage());
                        sb.append("\n- IOException StackTrace: " + ioe.getStackTrace());
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ insertXtrSrc");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- ExtractedSource logid: " + src.getLogId());
                        sb.append("\n- ExtractedSource Properties: " + src.getProps());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                }
        }

        private static int selectFileId(PreparedStatement ps) throws SQLException {
		int fileMaxId = 0;
                try {
                        ResultSet rs = ps.executeQuery();
                        while (rs.next()) {
                                fileMaxId = rs.getInt(1);
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

                return fileMaxId + 1;
        }

        private static int selectIntegrId(PreparedStatement ps) throws SQLException {
                int integrId = 0;
                try {
                        ResultSet rs = ps.executeQuery();
                        while (rs.next()) {
                                integrId = rs.getInt(1);
                        }
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ selectMaxIntegrId()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

                return integrId + 1;
        }

	private static int selectFreqId(PreparedStatement ps) throws SQLException {
                int freqId = 0;
                try {
                        ResultSet rs = ps.executeQuery();
                        while (rs.next()) {
                                freqId = rs.getInt(1);
                        }
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ selectMaxFreqId()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

                return freqId + 1;
        }

	private static int selectObsId(PreparedStatement ps) throws SQLException {
                int obsId = 0;
                try {
                        ResultSet rs = ps.executeQuery();
                        while (rs.next()) {
                                obsId = rs.getInt(1);
                        }
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ selectMaxObsId()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

                return obsId + 1;
        }

        private static int selectStartId(PreparedStatement ps) throws SQLException {
                int startId = 0;
                try {
                        ResultSet rs = ps.executeQuery();
                        while (rs.next()) {
                                startId = rs.getInt(1);
                        }
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ selectMaxStartId()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

                return startId + 1;
        }
 
	public static void insertObservation(PreparedStatement pstmt, Observation obs, boolean writeToFile) throws SQLException {
                int i = 1;
                try {
			if ("monetdb64".equals(database)) {
				if (writeToFile) {
					outObservation.write("" + obs.getObsId() + "," + obs.getTimeStart() + ",");
				} else {
	                	        pstmt.setInt(i++, obs.getObsId());
        	                	pstmt.setLong(i++, obs.getTimeStart());
	                	        //pstmt.setLong(i++, obs.getTimeEnd());
					//System.out.println("test: " + pstmt.toString());
	        	                pstmt.executeUpdate();
				}
			} else if ("mysql".equals(database)) {
				if (writeToFile) {
					outObservation.write("" + obs.getTimeStart());
				} else {
	                	        //pstmt.setInt(i++, obs.getObsId());
        	                	pstmt.setLong(i++, obs.getTimeStart());
	                	        //pstmt.setLong(i++, obs.getTimeEnd());
					//System.out.println("test: " + pstmt.toString());
	        	                pstmt.executeUpdate();
				}
			}
                } catch (IOException ioe) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- IOException @ insertObservation()");
                        sb.append("\n- IOException @ int i: " + i);
                        sb.append("\n- IOException Cause     : " + ioe.getCause());
                        sb.append("\n- IOException Message   : " + ioe.getMessage());
                        sb.append("\n- IOException StackTrace: " + ioe.getStackTrace());
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
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

 	public static void insertResolution(PreparedStatement pstmt, Resolution res, boolean writeToFile) throws SQLException {
                int i = 1;
                try {
			if (writeToFile) {
				outResolution.write("" + res.getResId() + "," + res.getMajor() + "," + res.getMinor() + "," + res.getPA() + "\n");
			} else {
	                        pstmt.setInt(i++, res.getResId());
        	                pstmt.setDouble(i++, res.getMajor());
                	        pstmt.setDouble(i++, res.getMinor());
                        	pstmt.setDouble(i++, res.getPA());
	                        pstmt.executeUpdate();
			}
                } catch (IOException ioe) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- IOException @ insertResolution()");
                        sb.append("\n- IOException @ int i: " + i);
                        sb.append("\n- IOException Cause     : " + ioe.getCause());
                        sb.append("\n- IOException Message   : " + ioe.getMessage());
                        sb.append("\n- IOException StackTrace: " + ioe.getStackTrace());
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertResolution");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- SQLException ResId: " + res.getResId() + ", " + res.getMajor() + ", " + res.getMinor() + ", " + res.getPA() );
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
                        System.exit(1);
                }
        }

	public static void insertBeams(PreparedStatement pstmt, Beam bm, boolean writeToFile) throws SQLException {
                int i = 1;
                try {
			if (writeToFile) {
				outBeams.write("" + bm.getBeamId() + "," + bm.getObsId() + "," + bm.getResId() + "\n");
			} else {
	                        pstmt.setInt(i++, bm.getBeamId());
        	                pstmt.setInt(i++, bm.getObsId());
                	        pstmt.setInt(i++, bm.getResId());
                        	pstmt.executeUpdate();
			}
                } catch (IOException ioe) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- IOException @ insertBeams()");
                        sb.append("\n- IOException @ int i: " + i);
                        sb.append("\n- IOException Cause     : " + ioe.getCause());
                        sb.append("\n- IOException Message   : " + ioe.getMessage());
                        sb.append("\n- IOException StackTrace: " + ioe.getStackTrace());
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertBeams");
                        sb.append("\n- SQLException @ int i: " + i);
                        sb.append("\n- SQLException ErrorCode: " + sqle.getErrorCode());
                        sb.append("\n- SQLException SQLState: " + sqle.getSQLState());
                        sb.append("\n- SQLException Message: " + sqle.getMessage());
                        sb.append("\n- SQLException Beam: " + bm.getBeamId() + ", " +  bm.getObsId() + ", " + bm.getResId());
                        sb.append("\n- This query will not be inserted");
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
                        System.exit(1);
                }
        }

	public static void insertFrequencyBand(PreparedStatement pstmt, FrequencyBand fb, boolean writeToFile) throws SQLException {
                int i = 1;
                try {
			if (writeToFile) {
				outFrequencyband.write("" + fb.getFreqId() + "," + fb.getFreqStart() + "," + fb.getFreqEnd() + "," + fb.getFreqEff() + "\n");
			} else {
	                        pstmt.setInt(i++, fb.getFreqId());
        	                pstmt.setDouble(i++, fb.getFreqStart());
                	        pstmt.setDouble(i++, fb.getFreqEnd());
                        	pstmt.setDouble(i++, fb.getFreqEff());
	                        pstmt.executeUpdate();
			}
                } catch (IOException ioe) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- IOException @ insertFrequencyBand()");
                        sb.append("\n- IOException @ int i: " + i);
                        sb.append("\n- IOException Cause     : " + ioe.getCause());
                        sb.append("\n- IOException Message   : " + ioe.getMessage());
                        sb.append("\n- IOException StackTrace: " + ioe.getStackTrace());
                        sb.append("\n-------------------------------------------------------");
                        System.err.println(sb.toString());
			System.exit(1);
                } catch (SQLException sqle) {
                        StringBuffer sb = new StringBuffer();
                        sb.append("\n-------------------------------------------------------");
                        sb.append("\n- SQLException @ method: insertFrequencyBand");
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

	private static void setFKeyCheck(Statement st, int check) throws SQLException {
                int done = 0;
                String query = "SET FOREIGN_KEY_CHECKS = " + check + ";";
                try {
                        st.executeUpdate(query);
                        done++;
                        //System.out.println("Done: " + query);
                } catch (SQLException sqle) {
                        System.err.println("+-------------------------------------------------------");
                        System.err.println("| SQLException @ setFKeyCheck()");
                        System.err.println("| SQLException ErrorCode: " + sqle.getErrorCode());
                        System.err.println("| SQLException SQLState: " + sqle.getSQLState());
                        System.err.println("| SQLException Message: " + sqle.getMessage());
                        System.err.println("| ------------------------------------------------------");
                        System.exit(1);
                }

        }

	public static int insertFromInfile(Statement st, String fromFile) throws SQLException {

		int inserted = 0;
	        StringBuffer query = new StringBuffer();
		//String file = "../databases/design/sql/insert.pipelineInnoDB.sql";

        	try {
                	query.append(fromFile);
                	//query.append(file);
                	//query.append(";");
			//if (!(new File(file)).exists()) throw new SQLException("File does not exist");
			//System.out.println("Query: " + query.toString());
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

        public static int insertTransaction(Statement st, StringBuffer copies) throws SQLException {

                int inserted = 0;
                StringBuffer query = new StringBuffer();

                try {
                        query.append("START TRANSACTION; \n");
                        query.append(copies.toString());
                        query.append("COMMIT;");
                        //System.out.println("Query: " + query.toString());
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


	public static String loadDataInFile(String file, String database, int Nrecs, String table) throws IOException {
		StringBuffer sb = new StringBuffer();
		String query = null;
		if ("mysql".equals(database)) {
			query = "LOAD DATA INFILE " + 
				"'" + file + "' " +
				"INTO TABLE " + table + " " +
				"FIELDS TERMINATED BY ',' " + 
				"LINES TERMINATED BY '\\n' ";
		} else if ("monetdb64".equals(database)) {
			query = "COPY " + 
				Nrecs + " RECORDS " + 
				"INTO " + table + " " + 
				"FROM '" + file + "' " + 
				"USING DELIMITERS ',', '\\n'";
		}
		sb.append(query);
		if ("observation".equals(table) && "mysql".equals(database)) sb.append("(time_s)");
		if ("extractedsources".equals(table) && "mysql".equals(database)) sb.append("(beam_id,freq_id,integr_id,logid,htmid,ra,decl,ra_err,decl_err,I,Q,U,V,I_err,Q_err,U_err,V_err)");
		sb.append(";");
		return sb.toString();
	}



}
