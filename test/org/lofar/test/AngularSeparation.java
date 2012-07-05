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

public class AngularSeparation extends ApplicationFrame {

	private static XYSeriesCollection ds;

	public AngularSeparation(String title) {
        	super(title);
	        //double[][] coord = getWenssCoordinates();
        	//XYDataset dataset = createDataset();
		// comment for
        	//XYDataset dataset = ds;

		SimpleHistogramDataset dataset = new SimpleHistogramDataset("Series 1");
	        SimpleHistogramBin bin1 = new SimpleHistogramBin(0.0, 1.0, true, false);
	        SimpleHistogramBin bin2 = new SimpleHistogramBin(1.0, 2.0, true, false);
        	SimpleHistogramBin bin3 = new SimpleHistogramBin(2.0, 3.0, true, false);
	        SimpleHistogramBin bin4 = new SimpleHistogramBin(3.0, 4.0, true, true);
        	// set the bin counts manually (an alternative is to use the
	        // addObservation() or addObservations() methods)
	        bin1.setItemCount(1);
	        bin2.setItemCount(10);
	        bin3.setItemCount(15);
	        bin4.setItemCount(20);
	        dataset.addBin(bin1);
	        dataset.addBin(bin2);
       		dataset.addBin(bin3);
	        dataset.addBin(bin4);

	        JFreeChart chart = createChart(dataset);
        	ChartPanel chartPanel = new ChartPanel(chart, false);
	        chartPanel.setPreferredSize(new java.awt.Dimension(1024, 712));
        	chartPanel.setMouseZoomable(true, false);
	        setContentPane(chartPanel);
	}

	//private static JFreeChart createChart(XYDataset dataset) {
	private static JFreeChart createChart(SimpleHistogramDataset dataset) {

        	//JFreeChart chart = ChartFactory.createScatterPlot(
        	JFreeChart chart = ChartFactory.createHistogram(
	            "SExtractor results",  // title
        	    "Real Right Ascension",             // x-axis label
	            "SExtracted Right Ascension",   // y-axis label
        	    dataset,            // data
	            PlotOrientation.VERTICAL,
        	    true,               // create legend?
	            false,               // generate tooltips?
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
			// a1, d1 from the generated sources in the txt file
			double a1 = 0, d1 = 0;
			// a2, d2 from the extracted sources by SExtractor in the database
			double a2 = 0, d2 = 0;
			double f1 = 0, f2 = 0;
			int bn1 = 0, bn2 = 0, bn3 = 0, bn4 = 0, bn5 = 0, bn6 = 0, bn7 = 0, bn8 = 0, bn9 = 0, bn10 = 0, bn11 = 0;
			String time1 = null, sign = null;
			int records = 0;
			//System.out.println("Time\ta1\t\t\td1\t\t\tflux\tangsep(\")\t\tdflux(%) ");
			String header = "Time\ta1\t\t\td1\t\t\tflux\tangsep(\")\t\tdflux(%)";
			BufferedWriter out = new BufferedWriter(new FileWriter("files/sources/source_decay_parms_photoastrom.txt", true));
			XYSeries s1 = new XYSeries("Flux Data");
                        out.write(header + "\n");
		        while ((str = in.readLine()) != null) {
				lineNr++;
		        	if (lineNr != 1) {
					time1 = str.substring(0, 4);
					f1 = Double.parseDouble(str.substring(5, 15));
					a1 = Conversion.fromRAToRadians(str.substring(36, 47));
					sign = str.substring(48,49);
					d1 = Conversion.fromDECToRadians(str.substring(49, 60));
					if (sign.equals("-")) d1 = d1 * -1;
					//System.out.println(lineNr + "; time1 = " + time1 + "; a1 = " + a1 + "; sign = " + sign + "; d1 = " + d1);
					/*rs = st.executeQuery("SELECT (ra*PI()/180) " + 
							     "	    ,(decl*PI()/180) " + 
							     "	    ,flux " +
							     "	    ,MIN(ABS(flux - " + f1 + ")) " + 
							     "	    ,TRUNCATE(SUBSTRING(comment, 1, 3), 0) AS img " + 
							     "  FROM lofar " + 
							     " WHERE TRUNCATE(SUBSTRING(comment, 1, 3), 0) = " + time1 +
							     " GROUP BY img;");
								//"   AND TRUNCATE(SUBSTRING(comment, 1, 3), 0) != 465;");*/

					String sel = 
						"SELECT (ra*PI()/180)                         AS radeg " +
						"      ,(decl*PI()/180)                       AS decdeg " + 
						"      ,flux " + 
						"      ,ABS(flux - " + f1 + ")                AS df " + 
						"      ,TRUNCATE(SUBSTRING(comment, 1, 3), 0) AS img " + 
						"  FROM lofar " + 
						" WHERE TRUNCATE(SUBSTRING(comment, 1, 3), 0) = " + time1 + 
						"   AND abs(flux - " + f1 + ")                = (SELECT MIN(T1.df) " + 
						"                                                  FROM (SELECT ABS(flux - " + f1 + ") AS df " + 
						"                                                          FROM lofar " + 
						"                                                         WHERE TRUNCATE(SUBSTRING(comment, 1, 3), 0) = " +
																	time1 + 
                                                "					        	) T1 " +  
                                                " 						);";
					rs = st.executeQuery(sel);
					records = 0;
					while (rs.next()) {
						a2 = rs.getDouble(1);
						d2 = rs.getDouble(2);
						f2 = rs.getDouble(3);
						records++;
					}
					String line;
					if (records > 0) {
						//System.out.println(lineNr + "; a2 = " + a2 + "; d2 = " + d2);
						double teller1 = Math.cos(d2) * Math.cos(d2) * Math.sin(a2 - a1) * Math.sin(a2 - a1);
						double teller2 = Math.pow(Math.cos(d1) * Math.sin(d2) - 
									Math.sin(d1) * Math.cos(d2) * Math.cos(a2 - a1), 2);
						double teller = Math.sqrt(teller1 + teller2);
						double arg = Math.sin(d1) * Math.sin(d2) + Math.cos(d1) * Math.cos(d2) * Math.cos(a1 - a2);
				               	double angsep = Math.acos(arg);
						double angsep2 = Math.abs(Math.atan(teller/arg)) * 206265;
						double df = f1 - f2;
						double dfperc = (df / f1) * 100;
					               /*System.out.println(time1 + 
								"; a1 = " + a1 + 
								"; d1 = " + d1 + 
								"; f1 = " + f1 + 
								"..::.. a2 = " + a2 + 
								"; d2 = " + d2 +
								"; f2 = " + f2);*/
							//"\t; angsep = " + angsep + " rad" + "\t; angsep = " + (angsep * 206265) + "\"");
					                //System.out.println(time1 + "\t" + a1 + " \t" + d1 + " \t" + f1 + " \t" + 
							//		Math.abs(angsep2) * 206265 + "\t" + Math.abs(dfperc) );
						line = time1 + "\t" + a1 + " \t" + d1 + " \t" + f1 + " \t" + 
							angsep2 + "\t" + Math.abs(dfperc);
						if (angsep2 < 1.0) bn1++;
						if (angsep2 >= 1.0 & angsep2 < 2.0) bn2++;
						if (angsep2 >= 2.0 & angsep2 < 3.0) bn4++;
						if (angsep2 >= 3.0 & angsep2 < 4.0) bn5++;
						if (angsep2 >= 4.0 & angsep2 < 5.0) bn6++;
						if (angsep2 >= 5.0 & angsep2 < 6.0) bn7++;
						if (angsep2 >= 6.0 & angsep2 < 7.0) bn8++;
						if (angsep2 >= 7.0 & angsep2 < 8.0) bn9++;
						if (angsep2 >= 8.0 & angsep2 < 9.0) bn10++;
						if (angsep2 >= 9.0) bn11++;
						s1.add(f1, f2);
					} else {
						//System.out.println(time1 + "");
						line = time1 + "";
					}
					out.write(line + "\n");
					//s1.add
				}
		        }
			out.close();
		        in.close();
			con.close();
			ds = new XYSeriesCollection();
	                ds.addSeries(s1);
			System.out.println("bins: " + bn1 + "; " + bn2 + "; " + bn3 + "; " + bn4 + "; " + 
						bn5 + "; " + bn6 + "; " + bn7 + "; " + bn8 + "; " + bn9 + "; " + bn10 + "; " + bn11);

		        AngularSeparation demo = new AngularSeparation("Input vs. SExtractorRA");
		        demo.pack();
		        RefineryUtilities.centerFrameOnScreen(demo);
		        demo.setVisible(true);


		} catch (IOException e) {
			System.out.println("IOException: " + e.getMessage());
		} catch (Exception e) {
			System.out.println("Exception: " + e.getMessage());
		}

	//	System.out.println("This is the cos(2pi/3) = " + Math.cos(2*Math.PI/3));
	}

	/*public static void writeLog(StringBuffer query, String message) throws IOException {
        	try {
                	BufferedWriter out = new BufferedWriter(new FileWriter("readwenss.log", true));
	                out.write(line + "\n");
        	        out.close();
        	} catch (IOException ioe) {
                	System.err.println(ioe.getMessage());
	                System.exit(1);
        	}
	}*/

	/*public static void process(String str) {
		String line = str;
		String time = line.substring(0, 4);
		//String peak = line.substring(5, 15);
		//String tau = line.substring(16, 23);
		//String xpix = line.substring(25, 28);
		//String ypix = line.substring(31, 34);
		String ra = line.substring(36, 47);
		String sign = line.substring(48, 49);
		String absdec = line.substring(49, 60);
		String dec = sign + absdec;

		
		

		System.out.println("'" + time + "':'" +
		//		"':'" + peak + "':'" +
		//		"':" + tau + "':'" +
		//		"':'" + xpix + "':'" +
		//		"':'" + ypix + "':'" +
				"':'" + ra + "':'" +
				"':'" + Conversion.fromRAToDegrees(ra) + "':'" +
				"':'" + Conversion.fromRAToRadians(ra) + "':'" +
				"':'" + sign + "':'" +
				"':'" + dec + "':.." +
				"':'" + Conversion.fromDECToDegrees(dec) + "':'" +
				"':'" + Conversion.fromDECToRadians(dec) + "':'" 
				);
		
	}*/
}
