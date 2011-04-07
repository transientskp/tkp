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

public class SexErrors extends ApplicationFrame {

	public SexErrors(SimpleHistogramDataset shdataset, String title) {
        	super(title);
	        JFreeChart chart = createChart(shdataset);
        	ChartPanel chartPanel = new ChartPanel(chart, false);
	        chartPanel.setPreferredSize(new java.awt.Dimension(1024, 712));
        	chartPanel.setMouseZoomable(true, false);
	        setContentPane(chartPanel);
	}


        public SexErrors(XYDataset dataset, String title, String type) {
                super(title);
                JFreeChart chart = createChart(dataset, type);
                ChartPanel chartPanel = new ChartPanel(chart, false);
                chartPanel.setPreferredSize(new java.awt.Dimension(1024, 712));
                chartPanel.setMouseZoomable(true, false);
                setContentPane(chartPanel);
        }

	private static JFreeChart createChart(SimpleHistogramDataset dataset) {

        	JFreeChart chart = ChartFactory.createHistogram(
	            "SExtractor results on Position Errors",  // title
        	    "Angular Separation (in arcsec)",             // x-axis label
	            "Number",   // y-axis label
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
	        plot.setDomainCrosshairVisible(true);
        	plot.setRangeCrosshairVisible(true);

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

		String title = "SExtractor results on Position Errors";
		String x_axis = "True flux (in Jy)";
		String y_axis = "Position Error (in arcsec)";
		if ("F".equals(type)) {
			title = "SExtractor results on Flux Errors";
			x_axis = "True flux (in Jy)";
			y_axis = "Flux Error | (Measured - True) / True |";
		}

                JFreeChart chart = ChartFactory.createScatterPlot(
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
                plot.setDomainCrosshairVisible(true);
                plot.setRangeCrosshairVisible(true);

                XYItemRenderer r = plot.getRenderer();
                if (r instanceof XYLineAndShapeRenderer) {
                        XYLineAndShapeRenderer renderer = (XYLineAndShapeRenderer) r;
                        //renderer.setDefaultShapesVisible(true);
                        //renderer.setDefaultShapesFilled(true);
                }

                NumberAxis axis = (NumberAxis) plot.getDomainAxis();
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
     			BufferedReader in = new BufferedReader(new FileReader(file));
		        String str;
			int lineNr = 0;
			// a1, d1, f1 := 'true' values from the generated sources in the txt file
			double a1 = 0, d1 = 0, f1 = 0;
			// a2, d2, f2 := 'measured values by SExtractor and now stored in the database
			double a2 = 0, d2 = 0, f_max2 = 0, f_iso2 = 0, f_isocor2 = 0, f_auto2 = 0, f_aper2 = 0;
			String time1 = null, sign = null;
			int records = 0;
			//System.out.println("Time\ta1\t\t\td1\t\t\tflux\tangsep(\")\t\tdflux(%) ");
			String header = "Time\ta1\t\t\td1\t\t\tflux\tangsep(\")\t\tdflux(%)";
			BufferedWriter out = new BufferedWriter(new FileWriter("files/sources/source_decay_parms_photoastrom.txt", true));

			//String lofarTable[] = new String["lofar", "lofarcat2"];
			//String lofarTable = "lofarcatfluxen";

			// XY Stuff
			//XYSeries s1 = new XYSeries("SExtractor params: FLUX_MAX, 10\u03c3");
			XYSeries smax1 = new XYSeries("SExtractor params: FLUX_MAX, 10\u03c3, ALPHA_J2000, DEC_J2000");
			XYSeries siso1 = new XYSeries("SExtractor params: FLUX_ISO, 10\u03c3, ALPHA_J2000, DEC_J2000");
			XYSeries sisocor1 = new XYSeries("SExtractor params: FLUX_ISOCOR, 10\u03c3, ALPHA_J2000, DEC_J2000");
			XYSeries sauto1 = new XYSeries("SExtractor params: FLUX_AUTO, 10\u03c3, ALPHA_J2000, DEC_J2000");
			XYSeries saper1 = new XYSeries("SExtractor params: FLUX_APER, 10\u03c3, ALPHA_J2000, DEC_J2000");

			XYSeries s2 = new XYSeries("SExtractor params: FLUX_MAX, 10\u03c3, ALPHAWIN_J2000, DECWIN_J2000");

			XYSeries as1 = new XYSeries("SExtractor params: FLUX_MAX, 10\u03c3, ALPHA_J2000, DEC_J2000");
			XYSeries as2 = new XYSeries("SExtractor params: FLUX_MAX, 10\u03c3, ALPHAWIN_J2000, DECWIN_J2000");
			XYSeries l1 = new XYSeries("Limit: FLUX_MAX, 10\u03c3, ALPHAWIN_J2000, DECWIN_J2000");

			// Histogram stuff
			int binmin = 0, binmax = 25;
			double binsize = 0.5;
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

                        out.write(header + "\n");
		        while ((str = in.readLine()) != null) {
				lineNr++;
				//System.out.println("Regelnr in file: " + lineNr);
		        	if (lineNr != 1) {
					time1 = str.substring(0, 4);
					f1 = Double.parseDouble(str.substring(5, 15));
					a1 = Conversion.fromRAToRadians(str.substring(36, 47));
					sign = str.substring(48,49);
					d1 = Conversion.fromDECToRadians(str.substring(49, 60));
					if (sign.equals("-")) d1 = d1 * -1;

                                        String sel = getQuery("lofarcatfluxen", f1, time1);
                                        rs = st.executeQuery(sel);
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
                                        String line;
                                        if (records > 0) {
                                                double angsep = getPosError(a1, d1, a2, d2);
                                                double fluxmaxerr = getFluxMaxError(f1, f_max2);
                                                double fluxisoerr = getFluxIsoError(f1, f_iso2);
                                                double fluxisocorerr = getFluxIsocorError(f1, f_isocor2);
                                                double fluxautoerr = getFluxAutoError(f1, f_auto2);
                                                double fluxapererr = getFluxAperError(f1, f_aper2);
                                                //line = time1 + "\t" + a1 + " \t" + d1 + " \t" + f1 + " \t" + angsep + "\t" + f_max2 + "\t" + f_iso2 + "\t" + f_isocor2 + "\t" + f_auto2 + "\t" + f_aper2 + "\t" + fluxmaxerr;
                                                line = time1 + "\t" + a1 + " \t" + d1 + " \t" + fluxmaxerr + " \t" + fluxisoerr + "\t" + fluxisocorerr + "\t" + fluxautoerr + "\t" + fluxapererr;
						//System.out.println(line);

                                                for (int i = 0; i < bins1.length; i++) {
                                                        if (bins1[i].accepts(angsep)) bins1[i].setItemCount(bins1[i].getItemCount() + 1);
                                                }
                                                as1.add(f1, angsep);
                                                smax1.add(f1, fluxmaxerr);
                                                siso1.add(f1, fluxisoerr);
                                                sisocor1.add(f1, fluxisocorerr);
                                                sauto1.add(f1, fluxautoerr);
                                                saper1.add(f1, fluxapererr);
                                        } else {
                                                //System.out.println(time1 + "");
                                                line = time1 + "";
                                        }

					//getQuery("lofarcat2", f1, time1);
					rs = st.executeQuery(getQuery("lofarcatfluxen2", f1, time1));
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
						double fluxmaxerr = getAbsFluxMaxError(f1, f_max2);
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

					out.write(line + "\n");
				}
		        }
			out.close();
		        in.close();
			con.close();

			XYSeriesCollection asds = new XYSeriesCollection();
	                asds.addSeries(as1);
	                asds.addSeries(as2);
			//asds.addSeries(l1);

			XYSeriesCollection ds = new XYSeriesCollection();
	                ds.addSeries(smax1);
	                //ds.addSeries(siso1);
	                //ds.addSeries(sisocor1);
	                //ds.addSeries(sauto1);
	                //ds.addSeries(saper1);
	                //ds.addSeries(s2);

			SimpleHistogramDataset shds1 = new SimpleHistogramDataset("SExtractor params: FLUX_MAX, 10\u03c3");
			shds1.setAdjustForBinSize(false);
			for (int i = 0; i < bins1.length; i++) {
				shds1.addBin(bins1[i]);
			}

			SimpleHistogramDataset shds2 = new SimpleHistogramDataset("SExtractor params: FLUX_MAX, 10\u03c3");
			shds2.setAdjustForBinSize(false);
			for (int i = 0; i < bins2.length; i++) {
				shds2.addBin(bins2[i]);
			}

		        SexErrors demo1 = new SexErrors(asds, "Plot on Position Error w/ FLUX_MAX", "P");
		        demo1.pack();
		        RefineryUtilities.centerFrameOnScreen(demo1);
		        demo1.setVisible(true);

		        SexErrors demo2 = new SexErrors(ds, "Plot on Flux Error w/ FLUX_MAX", "F");
		        demo2.pack();
		        RefineryUtilities.centerFrameOnScreen(demo2);
		        demo2.setVisible(true);

		        SexErrors histodemo1 = new SexErrors(shds1, "Histogram on Position Error w/ FLUX_MAX J2000");
		        histodemo1.pack();
		        RefineryUtilities.centerFrameOnScreen(histodemo1);
		        histodemo1.setVisible(true);

		        SexErrors histodemo2 = new SexErrors(shds2, "Histogram on Position Error w/ FLUX_MAX WIN_J2000");
		        histodemo2.pack();
		        RefineryUtilities.centerFrameOnScreen(histodemo2);
		        histodemo2.setVisible(true);

		} catch (IOException e) {
			System.out.println("IOException: " + e.getMessage());
		} catch (Exception e) {
			System.out.println("Exception: " + e.getMessage());
		}

	}

	public static String getQuery(String lofarTable, double f1, String time1) {
		String query = "SELECT (ra*PI()/180)                         AS radeg " +
                               "      ,(decl*PI()/180)                       AS decdeg " +
                               "      ,flux_max " +
                               "      ,flux_iso " +
                               "      ,flux_isocor " +
                               "      ,flux_auto " +
                               "      ,flux_aper " +
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

	public static double getFluxMaxError(double trueFlux, double measuredFlux) {
		return measuredFlux / trueFlux ;
	}

	public static double getAbsFluxMaxError(double trueFlux, double measuredFlux) {
		return Math.abs(measuredFlux / trueFlux - 1);
	}

	public static double getFluxIsoError(double trueFlux, double measuredFlux) {
		return measuredFlux / trueFlux;
	}

	public static double getAbsFluxIsoError(double trueFlux, double measuredFlux) {
		return Math.abs(measuredFlux / trueFlux - 1);
	}

	public static double getFluxIsocorError(double trueFlux, double measuredFlux) {
		return measuredFlux / trueFlux;
	}

	public static double getAbsFluxIsocorError(double trueFlux, double measuredFlux) {
		return Math.abs(measuredFlux / trueFlux - 1);
	}

	public static double getFluxAutoError(double trueFlux, double measuredFlux) {
		return measuredFlux / trueFlux;
	}

	public static double getAbsFluxAutoError(double trueFlux, double measuredFlux) {
		return Math.abs(measuredFlux / trueFlux - 1);
	}

	public static double getFluxAperError(double trueFlux, double measuredFlux) {
		return measuredFlux / trueFlux;
	}

	public static double getAbsFluxAperError(double trueFlux, double measuredFlux) {
		return Math.abs(measuredFlux / trueFlux - 1);
	}

	public static double getPosError(double a1, double d1, double a2, double d2) {
		double teller1 = Math.cos(d2) * Math.cos(d2) * Math.sin(a2 - a1) * Math.sin(a2 - a1);
                double teller2 = Math.pow(Math.cos(d1) * Math.sin(d2) - Math.sin(d1) * Math.cos(d2) * Math.cos(a2 - a1), 2);
                double teller = Math.sqrt(teller1 + teller2);
                double arg = Math.sin(d1) * Math.sin(d2) + Math.cos(d1) * Math.cos(d2) * Math.cos(a1 - a2);
                //double angsep = Math.acos(arg);
                return Math.abs(Math.atan(teller/arg)) * 206265;
	}


}
