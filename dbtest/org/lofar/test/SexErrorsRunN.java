package org.lofar.test;

import java.awt.Color;
import java.io.*;
import java.sql.*;
import java.text.NumberFormat;
import java.text.SimpleDateFormat;

import javax.swing.JPanel;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.DateAxis;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.renderer.xy.XYItemRenderer;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.data.statistics.SimpleHistogramBin;
import org.jfree.data.statistics.SimpleHistogramDataset;
import org.jfree.data.time.Month;
import org.jfree.data.time.TimeSeries;
import org.jfree.data.time.TimeSeriesCollection;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.ui.ApplicationFrame;
import org.jfree.ui.RectangleInsets;
import org.jfree.ui.RefineryUtilities;

import org.lofar.services.Conversion;

public class SexErrorsRunN extends ApplicationFrame {

	// type = 1: see f.ex.: /scratch/bscheers/java/org/lofar/test/source_decay_parms.txt
	// type = 2: see f.ex.: /scratch/bscheers/java/org/lofar/test/run08/source_decay_parms.txt
	private final static byte formatType = 1;
	private final static String runid = "run90";
	private final static String lofarTable = "lofarrun90cat";
	private final static double stn = 9.0;
	private final static String sigma = stn + "\u03c3";
	private final static String flux = "FLUX_MAX";
	
	private final static String astroTitle = "SExtractor results on astrometry for " + runid;
	private final static String photoTitle = "SExtractor results on photometry for " + runid;
	private final static String legenda = "SExtractor params for " + runid + ": " + flux + ", " + sigma;
	
	private final static int binmin = 0;
	private final static int binmax = 25;
	private final static double binsize = 1.;

	private final static double fluxbinmin = -2.2;
	private final static double fluxbinmax = 2.2;
	private final static double fluxbinsize = 0.2;

	private final static double beamsize = 300.;

	// Histogram
	public SexErrorsRunN(SimpleHistogramDataset shdataset, String title, String type) {
        	super(title);
	        JFreeChart chart = createChart(shdataset, type);
        	ChartPanel chartPanel = new ChartPanel(chart, false);
	        chartPanel.setPreferredSize(new java.awt.Dimension(1024, 712));
        	chartPanel.setMouseZoomable(true, false);
	        setContentPane(chartPanel);
	}

	// XYDataset
        public SexErrorsRunN(XYDataset dataset, String title, String type) {
                super(title);
                JFreeChart chart = createChart(dataset, type);
                ChartPanel chartPanel = new ChartPanel(chart, false);
                chartPanel.setPreferredSize(new java.awt.Dimension(1024, 712));
                chartPanel.setMouseZoomable(true, false);
                setContentPane(chartPanel);
        }

	private static JFreeChart createChart(SimpleHistogramDataset dataset, String type) {
		
		String title = astroTitle;
                String x_axis = "Angular Separation (in arcsec)";
                String y_axis = "Number";
                if ("P".equals(type.substring(0, 1))) {
                        title = photoTitle; //"SExtractor results on photometry for " + runid + " (" + sigma + ")";
                        x_axis = "Flux Error [(Measured - True) / RMS]";
                        //y_axis = "Flux Error (Measured - True) / rms";
                }

        	JFreeChart chart = ChartFactory.createHistogram(
	            title,  		// title
        	    x_axis,             // x-axis label
	            y_axis,   		// y-axis label
        	    dataset,            // data
	            PlotOrientation.VERTICAL,
        	    true,               // create legend?
	            true,               // generate tooltips?
        	    false               // generate URLs?
			);

	        chart.setBackgroundPaint(Color.white);

	        XYPlot plot = (XYPlot) chart.getPlot();
        	plot.setBackgroundPaint(Color.lightGray);
	        plot.setDomainGridlinePaint(Color.white);
	        plot.setRangeGridlinePaint(Color.white);
        	plot.setAxisOffset(new RectangleInsets(5.0, 5.0, 5.0, 5.0));
	        //plot.setDomainCrosshairVisible(true);
        	//plot.setRangeCrosshairVisible(true);

	        XYItemRenderer r = plot.getRenderer();
        	if (r instanceof XYLineAndShapeRenderer) {
		        XYLineAndShapeRenderer renderer = (XYLineAndShapeRenderer) r;
		        //renderer.setDefaultShapesVisible(true);
		        //renderer.setDefaultShapesFilled(true);
	        }

	        NumberAxis axis = (NumberAxis) plot.getDomainAxis();
        	return chart;
	}

        private static JFreeChart createChart(XYDataset dataset, String type) {

                String title = astroTitle;
                String x_axis = "S/N (True flux / RMS)";
                String y_axis = "Angular separation (in arcsec)";
                if ("P".equals(type.substring(0, 1))) {
                        title = photoTitle; //"SExtractor results on photometry for " + runid + " (" + sigma + ")";
                        //x_axis = "S/N (True flux / RMS)";
                        y_axis = "Flux Error (Measured - True) / RMS";
                }

                //XYSeries xys = dataset.getSeries(1);

                /*JFreeChart chart = ChartFactory.createScatterPlot(
                    title,              // title
                    x_axis,             // x-axis label
                    y_axis,             // y-axis label
                    dataset,            // data
                    PlotOrientation.VERTICAL,
                    true,               // create legend?
                    true,               // generate tooltips?
                    false               // generate URLs?
                        );*/
		
                JFreeChart chart = ChartFactory.createXYLineChart(
                    title,              // title
                    x_axis,             // x-axis label
                    y_axis,             // y-axis label
                    dataset,            // data
                    PlotOrientation.VERTICAL,
                    true,               // create legend?
                    true,               // generate tooltips?
                    false               // generate URLs?
                        );
		

                chart.setBackgroundPaint(Color.white);

                XYPlot plot = (XYPlot) chart.getPlot();
                plot.setBackgroundPaint(Color.lightGray);
                plot.setDomainGridlinePaint(Color.white);
                plot.setRangeGridlinePaint(Color.white);
                plot.setAxisOffset(new RectangleInsets(5.0, 5.0, 5.0, 5.0));
                //plot.setDomainCrosshairVisible(true);
                //plot.setRangeCrosshairVisible(true);
		XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer();
		// "0" is the scatter plot 
		renderer.setSeriesLinesVisible(0, false); 
		renderer.setSeriesShapesVisible(0, true); 
		// "1" is the line plot 
		renderer.setSeriesLinesVisible(1, true); 
		renderer.setSeriesShapesVisible(1, false); 
		// all invisible
		//renderer.setLinesVisible(false);
		plot.setRenderer(renderer); 
                //NumberAxis axis = (NumberAxis) plot.getDomainAxis();
                return chart;
        }



	public static void main(String[] args) {

		try {
			
			Class.forName("com.mysql.jdbc.Driver");
                        Connection con = DriverManager.getConnection("jdbc:mysql://acamar.science.uva.nl:3306/lofar?user=lofar&password=cs1");
			Statement st = con.createStatement();
			ResultSet rs;

			//String file = "../../../files/sources/source_decay_parms.txt";
			String file = "files/sources/source_decay_parms.txt";
			switch (formatType) {
                        	case 2:
					file = "org/lofar/test/" + runid + "/source_decay_parms.txt";
                                        break;
                        }
     			BufferedReader in = new BufferedReader(new FileReader(file));
		        String str;
			int lineNr = 0;
			// a1, d1, f1 := 'true' values from the generated sources in the txt file
			double a1 = 0, d1 = 0, f1 = 0;
			// a2, d2, f2 := 'measured values by SExtractor and now stored in the database
			// Values end at 2 to indicate measured values
			double a2 = 0, d2 = 0, 
			f_max2 = 0, f_iso2 = 0, f_isocor2 = 0, f_auto2 = 0, f_aper2 = 0,
			frms_max2 = 0, frms_iso2 = 0, frms_isocor2 = 0, frms_auto2 = 0, frms_aper2 = 0,
			isoareaf_image2 = 0, f_isoadj2 = 0;

			String time1 = null, sign = null;
			int records = 0;
			//System.out.println("Time\ta1\t\t\td1\t\t\tflux\tangsep(\")\t\tdflux(%) ");
			String header = "Time\ta1\t\t\td1\t\t\tflux\tangsep(\")\t\tdflux(%)";
			//BufferedWriter out = new BufferedWriter(new FileWriter("files/sources/source_decay_parms_photoastrom.txt", true));

			//String lofarTable[] = new String["lofar", "lofarcat2"];
			//String lofarTable = "lofarcatfluxen";

			//+-----------------------
			// XY Stuff on Photometry
			//XYSeries s1 = new XYSeries("SExtractor params: FLUX_MAX, 10\u03c3");
			//XYSeries smax1 = new XYSeries("SExtractor params: FLUX_MAX");
			XYSeries smax1 = new XYSeries(legenda);
			XYSeries siso1 = new XYSeries("SExtractor params: FLUX_ISO");
			XYSeries sisocor1 = new XYSeries("SExtractor params: FLUX_ISOCOR");
			XYSeries sauto1 = new XYSeries("SExtractor params: FLUX_AUTO");
			XYSeries saper1 = new XYSeries("SExtractor params: FLUX_APER");
			XYSeries sisoadj1 = new XYSeries("SExtractor params: FLUX_ISOADJ");
			XYSeries limit = new XYSeries("Theoretical limit: Synthesized beamsize / Signal-to-Noise");

			//XYSeries s2 = new XYSeries("SExtractor params: FLUX_MAX, 10\u03c3, ALPHAWIN_J2000, DECWIN_J2000");

			//XYSeries as1 = new XYSeries("SExtractor params: FLUX_MAX, 10\u03c3, ALPHA_J2000, DEC_J2000");

			//+-----------------------
			// XY Stuff on Astrometry
			XYSeries as1 = new XYSeries(legenda + ", pdf");
			XYSeries as2 = new XYSeries(legenda + ", AngSep small");
			XYSeries as3 = new XYSeries(legenda + ", AngSep large");
			//XYSeries l1 = new XYSeries("Limit: FLUX_MAX, 10\u03c3, ALPHAWIN_J2000, DECWIN_J2000");

			// Histogram stuff on Photometry
			int fluxnumberOfBins = (int)Math.round((fluxbinmax - fluxbinmin) / fluxbinsize);
			double fluxlowerBound = 0, fluxupperBound = 0;
			SimpleHistogramBin fluxbins1[] = new SimpleHistogramBin[fluxnumberOfBins];
			//SimpleHistogramBin bins2[] = new SimpleHistogramBin[numberOfBins];
			for (int i = 0; i < fluxnumberOfBins; i++) {
				fluxlowerBound = fluxbinmin + (i * fluxbinsize);
				fluxupperBound = fluxbinmin + ((i + 1) * fluxbinsize);
				fluxbins1[i] = new SimpleHistogramBin(fluxlowerBound, fluxupperBound, true, false);
				//bins2[i] = new SimpleHistogramBin(lowerBound, upperBound, true, false);
			}

			// Histogram stuff on Astrometry
			int numberOfBins = (int)Math.round((binmax - binmin) / binsize);
			double lowerBound = 0, upperBound = 0;
			SimpleHistogramBin bins1[] = new SimpleHistogramBin[numberOfBins];
			SimpleHistogramBin bins2[] = new SimpleHistogramBin[numberOfBins];
			for (int i = 0; i < numberOfBins; i++) {
				lowerBound = binmin + (i * binsize);
				upperBound = binmin + ((i + 1) * binsize);
				bins1[i] = new SimpleHistogramBin(lowerBound, upperBound, true, false);
				bins2[i] = new SimpleHistogramBin(lowerBound, upperBound, true, false);
			}

                        //out.write(header + "\n");
		        while ((str = in.readLine()) != null) {
				lineNr++;
				//System.out.println("Regelnr in file: " + lineNr);
				// lineNr = 1 => header
		        	if (lineNr != 1) {
					switch (formatType) {
						case 2:
							time1 = str.substring(0, 7);
							f1 = Double.parseDouble(str.substring(8, 18));
							// TODO: Replace with Java's Math internal method
							a1 = Conversion.fromRAToRadians(str.substring(38, 49));
							sign = str.substring(50, 51);
							d1 = Conversion.fromDECToRadians(str.substring(51, 62));
							if (sign.equals("-")) d1 = d1 * -1;
							break;
						default: 
							time1 = str.substring(0, 4);
		                                        f1 = Double.parseDouble(str.substring(5, 15));
		                                        // TODO: Replace with Java's Math internal method
		                                        a1 = Conversion.fromRAToRadians(str.substring(36, 47));
		                                        sign = str.substring(48, 49);
		                                        d1 = Conversion.fromDECToRadians(str.substring(49, 60));
		                                        if (sign.equals("-")) d1 = d1 * -1;
							//System.out.println("a1 = " + a1 + "; d1 = " + d1);
							break;
					}

                                        String sel = getQuery(lofarTable, f1, time1);
                                        rs = st.executeQuery(sel);
                                        records = 0;
                                        while (rs.next()) {
                                                a2 = rs.getDouble(1);
                                                d2 = rs.getDouble(2);
						//System.out.println("a2 = " + a2 + "; d2 = " + d2);
                                                f_max2 = rs.getDouble(3);
                                                f_iso2 = rs.getDouble(4);
                                                f_isocor2 = rs.getDouble(5);
                                                f_auto2 = rs.getDouble(6);
                                                f_aper2 = rs.getDouble(7);
                                                frms_max2 = rs.getDouble(8);
                                                frms_iso2 = rs.getDouble(9);
                                                frms_isocor2 = rs.getDouble(10);
                                                frms_auto2 = rs.getDouble(11);
                                                frms_aper2 = rs.getDouble(12);
                                                f_isoadj2 = rs.getDouble(13);
						isoareaf_image2 = rs.getDouble(14);
                                                records++;
                                        }
                                        String line;
                                        if (records > 0) {
                                                //double angsep1 = getPosError(a1, d1, a2, d2);
                                                //double angsep2 = getAngSepSmall(a1, d1, a2, d2);
                                                double angsep = getAngSep(a1, d1, a2, d2);
                                                double fluxmaxerr = getFluxError(f1, f_max2);
                                                double fluxisoerr = getFluxError(f1, f_iso2);
                                                double fluxisocorerr = getFluxError(f1, f_isocor2);
                                                double fluxautoerr = getFluxError(f1, f_auto2);
                                                double fluxapererr = getFluxError(f1, f_aper2);
                                                double fluxisoadjerr = getFluxError(f1, f_isoadj2);
                                                /*line = time1 + "\t" + a1 + " \t" + d1 + " \t" + f1 
							+ " \t" + angsep + "\t" + f_max2 + "\t" + f_iso2 + "\t" + f_isocor2 
							+ "\t" + f_auto2 + "\t" + f_aper2 + "\t" + fluxmaxerr;*/
                                                line = time1 + "\t" + angsep //+ " \t" + angsep2 + " \t" 
							 + " \t" + fluxisoerr + "\t" + fluxisocorerr 
							 + "\t" + fluxautoerr + "\t" + fluxapererr;
						//System.out.println(line);

						int nobin = 0;
                                                for (int i = 0; i < bins1.length; i++) {
                                                        if (bins1[i].accepts(angsep)) {
								bins1[i].setItemCount(bins1[i].getItemCount() + 1);
								nobin++;
							} 
                                                }
						// if angsep does not fit into any bin add it to the last bin
						if (nobin == 0) bins1[bins1.length - 1].setItemCount(bins1[bins1.length - 1].getItemCount() + 1);

						int nofluxbin = 0;
                                                for (int i = 0; i < fluxbins1.length; i++) {
                                                        if (fluxbins1[i].accepts((fluxmaxerr / frms_max2))) {
								fluxbins1[i].setItemCount(fluxbins1[i].getItemCount() + 1);
								nofluxbin++;
							} 
                                                }
						// if angsep does not fit into any bin add it to the last bin
						if (nofluxbin == 0) {
							if (fluxmaxerr / frms_max2 < fluxbins1[0].getLowerBound()) { 
								fluxbins1[0].setItemCount(fluxbins1[0].getItemCount() + 1);
							} else {
								fluxbins1[fluxbins1.length - 1]
									.setItemCount(fluxbins1[fluxbins1.length - 1].getItemCount() + 1);
							}
						}



						// If clause is dirty but quick
						//if (f1 > 10.) {
                                                	as1.add(f1 / frms_max2, angsep);
                                                	//as2.add(f1 / frms_max2, angsep2);
                                                	//as3.add(f1 / frms_max2, angsep3);
                                                	smax1.add(f1 / frms_max2, fluxmaxerr / frms_max2);
	                                                siso1.add(f1, fluxisoerr);
        	                                        sisocor1.add(f1, fluxisocorerr);
                	                                sauto1.add(f1, fluxautoerr);
                        	                        saper1.add(f1, fluxapererr);
                        	                        sisoadj1.add(f1, fluxisoadjerr);
							//limit.add(f1 / frms_max2, beamsize * frms_max2 / f1);
						//}
                                        } else {
                                                //System.out.println(time1 + "");
                                                line = time1 + "";
                                        }

					//getQuery("lofarcat2", f1, time1);
					/*
					rs = st.executeQuery(getQuery("lofarcatrun09", f1, time1));
					records = 0;
					while (rs.next()) {
						a2 = rs.getDouble(1);
						d2 = rs.getDouble(2);
						f_max2 = rs.getDouble(3);
                                                f_iso2 = rs.getDouble(4);
                                                f_isocor2 = rs.getDouble(5);
                                                f_auto2 = rs.getDouble(6);
                                                f_aper2 = rs.getDouble(7);
						records++;
					}
					//String line;
					if (records > 0) {
						double angsep = getPosError(a1, d1, a2, d2);
						double fluxmaxerr = getFluxError(f1, f_max2);
						line = time1 + "\t" + a1 + " \t" + d1 + " \t" + f1 + " \t" + angsep + "\t" + fluxmaxerr;
						System.out.println(line);
						for (int i = 0; i < bins2.length; i++) {
							if (bins2[i].accepts(angsep)) bins2[i].setItemCount(bins2[i].getItemCount() + 1);
						}
						as2.add(f1, angsep);
						s2.add(f1, fluxmaxerr);
					} else {
						//System.out.println(time1 + "");
						line = time1 + "";
					}
					l1.add(f1, 40/f1);
					*/
					//out.write(line + "\n");
				}
		        }
			//out.close();
		        in.close();
			con.close();

			double dsn = 0.1;
			double snmin = (double) stn;
			double snmax = 82.;
			double sn = snmin;
			for (int i = 0; i < snmax/dsn; i++) {
				sn = sn + dsn;
				limit.add(sn, beamsize/sn);
			}

			XYSeriesCollection asds = new XYSeriesCollection();
	                asds.addSeries(as1);
	                //asds.addSeries(as2);
	                //asds.addSeries(as3);
	                //asds.addSeries(as2);
			//asds.addSeries(l1);
	                asds.addSeries(limit);

			XYSeriesCollection ds = new XYSeriesCollection();
	                ds.addSeries(smax1);
	                /*ds.addSeries(siso1);
	                ds.addSeries(sisocor1);
	                ds.addSeries(sauto1);
	                ds.addSeries(saper1);
	                ds.addSeries(sisoadj1);
			*/
	                //ds.addSeries(s2);

			SimpleHistogramDataset astrohistods = new SimpleHistogramDataset(legenda);
			astrohistods.setAdjustForBinSize(false);
			for (int i = 0; i < bins1.length; i++) {
				astrohistods.addBin(bins1[i]);
			}

			SimpleHistogramDataset fluxhistods = new SimpleHistogramDataset(legenda);
			fluxhistods.setAdjustForBinSize(false);
			for (int i = 0; i < fluxbins1.length; i++) {
				fluxhistods.addBin(fluxbins1[i]);
			}
			
		        SexErrorsRunN astrohisto = new SexErrorsRunN(astrohistods, astroTitle, "A");
		        astrohisto.pack();
		        RefineryUtilities.centerFrameOnScreen(astrohisto);
		        astrohisto.setVisible(true);

		        SexErrorsRunN astro = new SexErrorsRunN(asds, astroTitle, "A");
		        astro.pack();
		        RefineryUtilities.centerFrameOnScreen(astro);
		        astro.setVisible(true);
			
		        SexErrorsRunN fluxhisto = new SexErrorsRunN(fluxhistods, photoTitle, "P");
		        fluxhisto.pack();
		        RefineryUtilities.centerFrameOnScreen(fluxhisto);
		        fluxhisto.setVisible(true);

		        SexErrorsRunN photo = new SexErrorsRunN(ds, photoTitle, "P");
		        photo.pack();
		        RefineryUtilities.centerFrameOnScreen(photo);
		        photo.setVisible(true);
			
		} catch (IOException e) {
			System.out.println("IOException: " + e.getMessage());
		} catch (Exception e) {
			System.out.println("Exception: " + e.getMessage());
		}

	}

	/**
	 * This query retrieves the record that is equal to the observation time 
	 * (this is a sequence number given by the file name) and
	 * that is closest by in flux value
	 */
	public static String getQuery(String lofarTable, double f1, String time1) {
		String query = "SELECT (ra*PI()/180)                         AS radeg " +
                               "      ,(decl*PI()/180)                       AS decdeg " +
                               "      ,flux_max " +
                               "      ,flux_iso " +
                               "      ,flux_isocor " +
                               "      ,flux_auto " +
                               "      ,flux_aper " +
                               "      ,dflux_max " +
                               "      ,dflux_iso " +
                               "      ,dflux_isocor " +
                               "      ,dflux_auto " +
                               "      ,dflux_aper " +
                               "      ,flux_isoadj " +
                               "      ,isoareaf_image " +
                               "      ,ABS(flux_max - " + f1 + ")                AS df " +
                               "      ,TRUNCATE(SUBSTRING(comment, 1, 3), 0) AS img " +
                               "  FROM " + lofarTable +
                               " WHERE TRUNCATE(SUBSTRING(comment, 1, 3), 0) = " + time1 +
                               "   AND ABS(flux_max - " + f1 + ") = (SELECT MIN(T1.df) " +
                               "                                       FROM (SELECT ABS(flux_max - " + f1 + ") AS df " +
                               "                                               FROM " + lofarTable +
                               "                                  WHERE TRUNCATE(SUBSTRING(comment, 1, 3), 0) = " + time1 +
                               "                                                       ) T1 " +
                               "                                               );";
		return query;
	}

	public static double getFluxError(double trueFlux, double measuredFlux) {
		//return measuredFlux / trueFlux;
		return measuredFlux - trueFlux;
	}
	
	/**
	 * Calculates the angular separation for objects according to formula from url
	 * a1, ..., d2 in radians, result in arcsecs
	 * From http://www.skythisweek.info/angsep.pdf
	 */
	public static double getPosError(double a1, double d1, double a2, double d2) {
		double teller1 = Math.cos(d2) * Math.cos(d2) * Math.sin(a2 - a1) * Math.sin(a2 - a1);
                double teller2 = Math.pow(Math.cos(d1) * Math.sin(d2) - Math.sin(d1) * Math.cos(d2) * Math.cos(a2 - a1), 2);
                double teller = Math.sqrt(teller1 + teller2);
                double arg = Math.sin(d1) * Math.sin(d2) + Math.cos(d1) * Math.cos(d2) * Math.cos(a1 - a2);
                //double angsep = Math.acos(arg);
                return Math.abs(Math.atan(teller/arg)) * 206265;
	}

	/**
	 * Calculates the angular separation for objects close together
	 * a1, ..., d2 in radians, result in arcsecs
	 * Meeus J., Astronomical Algorithms, Ch.16 Angular Separation, Willmann-Bell Inc., 1991
	 */
	public static double getAngSepSmall(double a1, double d1, double a2, double d2) {
		double dd = d2 - d1;
                double da = a2 - a1;
		double d = (d1 + d2) / 2;
		//double arg = (da * Math.cos(d)) * (da * Math.cos(d)) + (dd) * (dd);
                //return Math.sqrt(arg);
		double arg = (da * Math.cos(d)) * (da * Math.cos(d)) + (dd) * (dd);
                return Math.sqrt(arg) * 206265;
	}

	/**
	 * Calculates the angular separation for objects
	 * a1, ..., d2 in radians, result in arcsecs
	 * Meeus J., Astronomical Algorithms, Ch.16 Angular Separation, Willmann-Bell Inc., 1991
	 */
	public static double getAngSep(double a1, double d1, double a2, double d2) {
                return Math.acos(Math.sin(d1) * Math.sin(d2) + Math.cos(d1) * Math.cos(d2) * Math.cos(a1 - a2)) * 206265;
	}


}

