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
import org.jfree.chart.axis.LogarithmicAxis;
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

public class PlotTelescopesSens extends ApplicationFrame {

    public PlotTelescopesSens(String title) {
        super(title);
        XYDataset dataset = createDataset();
        JFreeChart chart = createChart(dataset);
        ChartPanel chartPanel = new ChartPanel(chart, false);
        chartPanel.setPreferredSize(new java.awt.Dimension(512, 356));
        chartPanel.setMouseZoomable(true, false);
        setContentPane(chartPanel);
    }

    private static JFreeChart createChart(XYDataset dataset) {

        JFreeChart chart = ChartFactory.createScatterPlot(
            "LOFAR, WSRT, VLA and GMRT Sensitivities Compared",  // title
            "Frequency (MHz)",             // x-axis label
            "Sensitivity (1\u03c3, 12h integration)",   // y-axis label
            dataset,            // data
	    PlotOrientation.VERTICAL,
            true,               // create legend?
            false,               // generate tooltips?
            false               // generate URLs?
        );

        chart.setBackgroundPaint(Color.white);

        XYPlot plot = (XYPlot) chart.getPlot();
        //plot.setBackgroundPaint(Color.lightGray);
        plot.setBackgroundPaint(Color.white);
        //plot.setDomainGridlinePaint(Color.white);
        //iplot.setRangeGridlinePaint(Color.white);
        plot.setDomainGridlinePaint(Color.lightGray);
        plot.setRangeGridlinePaint(Color.lightGray);
        plot.setAxisOffset(new RectangleInsets(5.0, 5.0, 5.0, 5.0));
        plot.setDomainCrosshairVisible(true);
        plot.setRangeCrosshairVisible(true);
        
        XYItemRenderer r = plot.getRenderer();
        if (r instanceof XYLineAndShapeRenderer) {
            XYLineAndShapeRenderer renderer = (XYLineAndShapeRenderer) r;
            //renderer.setDefaultShapesVisible(true);
            //renderer.setDefaultShapesFilled(true);
		renderer.setSeriesPaint(2, Color.black, true);
        }
	//r.setSeriesStroke();
        
        NumberAxis x_axis = (NumberAxis) plot.getDomainAxis();
	NumberAxis y_axis = new LogarithmicAxis("Sensitivity (1\u03c3, 12h integration) (mJy/B)");
	plot.setDomainAxis(x_axis);
	plot.setRangeAxis(y_axis);
	x_axis.setRange(20, 240);
	y_axis.setRange(0.01, 20);
        return chart;
    }
    
    private static XYDataset createDataset() {
	XYSeries s1 = new XYSeries("LOFAR");
	s1.add(30, 0.56);
	s1.add(75, 0.38);
	s1.add(120, 0.02);
	s1.add(200, 0.018);
	XYSeries s2 = new XYSeries("WSRT");
	s2.add(150, 4);
	XYSeries s3 = new XYSeries("VLA");
	s3.add(74, 15);
	XYSeries s4 = new XYSeries("GMRT");
	s4.add(150, 1);
	s4.add(230, 0.75);

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

        PlotTelescopesSens demo = new PlotTelescopesSens("LOFAR sensitivities compared");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}

