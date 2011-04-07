package org.lofar.plot;

import java.awt.Color;
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

public class Lightcurves extends ApplicationFrame {

    public Lightcurves(String title) {
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
            "The LOFAR Transient Pipeline - Processing times\nSTDOUT SExtractor data on 3GHz processor 1GB RAM, 7.5\u03c3 detection threshhold",  // title
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

	// number of sources in the images
	int ns[] = {7,8,7,10,10,9,9,9,9,10,12,12,12,13,15,17,17,18,20,20,21};

	//Total processing time
        XYSeries s1 = new XYSeries("Total processing time");
	s1.add(0, 1.82);
	s1.add(50, 1.69);
	s1.add(100, 1.59);
	s1.add(150, 1.90);
	s1.add(200, 1.93);
	s1.add(250, 1.85);
	s1.add(300, 1.81);
	s1.add(350, 1.83);
	s1.add(400, 1.82);
	s1.add(450, 1.90);
	s1.add(500, 2.10);
	s1.add(550, 2.10);
	s1.add(600, 2.15);
	s1.add(650, 2.27);
	s1.add(700, 2.46);
	s1.add(750, 3.44);
	s1.add(800, 2.58);
	s1.add(850, 2.80);
	s1.add(900, 3.27);
	s1.add(950, 2.93);
	s1.add(1000, 2.99);
	
	//Total java time
        XYSeries s2 = new XYSeries("Total transient detection (java) time");
	s2.add(0, 1.433);    // 7
	s2.add(50, 1.548);   // 8
	s2.add(100, 1.441);  // 7
	s2.add(150, 1.737);  //10
	s2.add(200, 1.732);  //10
	s2.add(250, 1.66);   // 9 --> one less, because it decayed
	s2.add(300, 1.659);  // 9
	s2.add(350, 1.664);  // 9
	s2.add(400, 1.64);   // 9
	s2.add(450, 1.744);  //10 sources
	s2.add(500, 1.969);  //12 
	s2.add(550, 1.964);  //12
	s2.add(600, 2.0);    //12
	s2.add(650, 2.135);  //13
	s2.add(700, 2.329);  //15
	s2.add(750, 3.181);  //17
	s2.add(800, 2.44);   //17
	s2.add(850, 2.631);  //18
	s2.add(900, 3.072);  //20
	s2.add(950, 2.762);  //20
	s2.add(1000, 2.841); //21
	
	//Total HTM time
        XYSeries s3 = new XYSeries("Total HTM lookup time");
	s3.add(0, 0.787);
	s3.add(50, 0.786);
	s3.add(100, 0.696);
	s3.add(150, 0.961);
	s3.add(200, 0.97);
	s3.add(250, 0.884);
	s3.add(300, 0.864);
	s3.add(350, 0.877);
	s3.add(400, 0.875);
	s3.add(450, 0.977);
	s3.add(500, 1.148);
	s3.add(550, 1.15);
	s3.add(600, 1.157);
	s3.add(650, 1.274);
	s3.add(700, 1.448);
	s3.add(750, 2.106);
	s3.add(800, 1.591);
	s3.add(850, 1.783);
	s3.add(900, 2.18);
	s3.add(950, 1.88);
	s3.add(1000, 1.967);
	
	//Total DB time
        XYSeries s4 = new XYSeries("Total DB time");
	s4.add(0, 0.037);
	s4.add(50, 0.036);
	s4.add(100, 0.031);
	s4.add(150, 0.034);
	s4.add(200, 0.043);
	s4.add(250, 0.038);
	s4.add(300, 0.04);
	s4.add(350, 0.031);
	s4.add(400, 0.03);
	s4.add(450, 0.036);
	s4.add(500, 0.048);
	s4.add(550, 0.047);
	s4.add(600, 0.049);
	s4.add(650, 0.059);
	s4.add(700, 0.05);
	s4.add(750, 0.088);
	s4.add(800, 0.064);
	s4.add(850, 0.069);
	s4.add(900, 0.085);
	s4.add(950, 0.072);
	s4.add(1000, 0.082);
	
	XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(s1);
        dataset.addSeries(s2);
        dataset.addSeries(s3);
        dataset.addSeries(s4);

        return dataset;
    }

    public static JPanel createDemoPanel() {
        JFreeChart chart = createChart(createDataset());
        return new ChartPanel(chart);
    }
    
    public static void main(String[] args) {

        Lightcurves demo = new Lightcurves("Pipeline processing times");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}

