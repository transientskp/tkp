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

public class GRB2007Regis extends ApplicationFrame {

	private static XYSeriesCollection ds;

	public GRB2007Regis(String title) {
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
			
			String file = "../grb2007/db/grb2007.db";
     			BufferedReader in = new BufferedReader(new FileReader(file));
		        String str;
			int lineNr = 0;
			String inputStr;
			String patternStr = ";";
			String[] fields;
			String dateStr = "/";
			String[] dateFields;
			//String[] fields = inputStr.split(patternStr);
			XYSeries s1 = new XYSeries("Flux Data");
		        while ((str = in.readLine()) != null) {
				lineNr++;
				inputStr = str;
				fields = inputStr.split(patternStr);
				dateFields = fields[1].split(dateStr);
				Calendar dateOfReg = new GregorianCalendar(dateFields[2], dateFields[1], dateFields[0]);
				System.out.println("" + fields[0] + "; " + dateFields[0] + " / " + dateFields[1] + " / " + dateFields[2]);
		        }
		        in.close();
			/*ds = new XYSeriesCollection();
	                ds.addSeries(s1);

		        GRB2007Regis demo = new GRB2007Regis("Input vs. SExtractorRA");
		        demo.pack();
		        RefineryUtilities.centerFrameOnScreen(demo);
		        demo.setVisible(true);*/


		} catch (IOException e) {
			System.out.println("IOException: " + e.getMessage());
		} catch (Exception e) {
			System.out.println("Exception: " + e.getMessage());
		}

	}

}
