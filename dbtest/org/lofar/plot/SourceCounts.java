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

public class SourceCounts extends ApplicationFrame {

    public SourceCounts(String title) {
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
            "LOFAR Transient Database\nSource counts and Row number to be expected for LBA Full Array",  // title
            "Frequency [MHz]",             // x-axis label
            "log N",   // y-axis label
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
                
        NumberAxis x_axis = (NumberAxis) plot.getDomainAxis();
	x_axis.setLowerBound(0.);
	x_axis.setUpperBound(100.);
        
	NumberAxis y_axis = (NumberAxis) plot.getRangeAxis();
	y_axis.setLowerBound(0.);
	y_axis.setUpperBound(5.);
	
        return chart;
    }
    
    private static XYDataset createDataset() {

	//1s timeseries
        XYSeries s1 = new XYSeries("1s");
	s1.add(30, Math.log10(787));
	s1.add(75, Math.log10(94));
	
	//100s timeseries
        XYSeries s2 = new XYSeries("100s");
	s2.add(30, Math.log10(4287));
	s2.add(75, Math.log10(533));
	
	//10000s timeseries
        XYSeries s3 = new XYSeries("10000s");
	s3.add(30, Math.log10(29830));
	s3.add(75, Math.log10(3367));
	
	//Number of rows in major table
        XYSeries s4 = new XYSeries("Number of rows");
	s4.add(0, 0.037);
	s4.add(50, 0.036);
	
	XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(s1);
        dataset.addSeries(s2);
        dataset.addSeries(s3);
        //dataset.addSeries(s4);

        return dataset;
    }

    public static JPanel createDemoPanel() {
        JFreeChart chart = createChart(createDataset());
        return new ChartPanel(chart);
    }
    
    public static void main(String[] args) {

        SourceCounts demo = new SourceCounts("Source counts for LBA Full Array");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}

