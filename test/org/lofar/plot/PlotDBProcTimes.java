package org.lofar.plot;

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
import org.jfree.data.time.Month;
import org.jfree.data.time.TimeSeries;
import org.jfree.data.time.TimeSeriesCollection;
import org.jfree.data.xy.XYDataset;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;
import org.jfree.ui.ApplicationFrame;
import org.jfree.ui.RectangleInsets;
import org.jfree.ui.RefineryUtilities;

public class PlotDBProcTimes extends ApplicationFrame {

    static String dblog;
    public PlotDBProcTimes(String title) {
        super(title);
	//double[][] coord = getWenssCoordinates();
        XYDataset dataset = createDataset();
        JFreeChart chart = createChart(dataset);
        ChartPanel chartPanel = new ChartPanel(chart, false);
        chartPanel.setPreferredSize(new java.awt.Dimension(1024, 712));
        chartPanel.setMouseZoomable(true, false);
        setContentPane(chartPanel);
    }

    private static JFreeChart createChart(XYDataset dataset) {

        //JFreeChart chart = ChartFactory.createScatterPlot(
        JFreeChart chart = ChartFactory.createXYLineChart(
            "The TKP Pipeline - Database processing times\nSTDOUT SExtractor data on 3GHz processor 1GB RAM, 7.5\u03c3 detection threshhold",  // title
            "Image number",             // x-axis label
            "seconds",   // y-axis label
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
        //plot.setDomainCrosshairVisible(true);
        //plot.setRangeCrosshairVisible(true);
        
        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer();
        //renderer.setDefaultShapesVisible(true);
        //renderer.setDefaultShapesFilled(true);
	plot.setRenderer(renderer);
                
        NumberAxis axis = (NumberAxis) plot.getDomainAxis();
        return chart;
    }
    
    private static XYDataset createDataset() {

        XYSeries s1 = new XYSeries("InputStream");
        XYSeries s2 = new XYSeries("HTM");
        XYSeries s3 = new XYSeries("DB");
        XYSeries s4 = new XYSeries("subtotals");
        XYSeries s5 = new XYSeries("totals");

        try {
                BufferedReader in = new BufferedReader(new FileReader(dblog));
                String str;
		int row = 0;
                while ((str = in.readLine()) != null) {
                        String[] fields = str.split(";");
                        for (int i = 0; i < fields.length; i++) {
				if (Integer.parseInt(fields[0]) % 50 == 0) {
	                                s1.add(Integer.parseInt(fields[0]), Double.parseDouble(fields[1]));
        	                        s2.add(Integer.parseInt(fields[0]), Double.parseDouble(fields[2]));
                	                s3.add(Integer.parseInt(fields[0]), Double.parseDouble(fields[3]));
                        	        s4.add(Integer.parseInt(fields[0]), Double.parseDouble(fields[4]));
                                	s5.add(Integer.parseInt(fields[0]), Double.parseDouble(fields[5]));
				}
                        }
                }
        } catch (IOException e) {
                System.err.println("IOException: " + e.getMessage());
                System.exit(1);
        }
	
	XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(s1);
        dataset.addSeries(s2);
        dataset.addSeries(s3);
        dataset.addSeries(s4);
        dataset.addSeries(s5);

        return dataset;
    }

    public static JPanel createDemoPanel() {
        JFreeChart chart = createChart(createDataset());
        return new ChartPanel(chart);
    }
    
    public static void main(String[] args) {

	dblog = args[0];
        PlotDBProcTimes demo = new PlotDBProcTimes("TKP pipeline database processing times");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}

