package org.lofar.plot;

import java.awt.Color;
import java.sql.*;
import java.text.NumberFormat;
import java.text.SimpleDateFormat;

import javax.swing.JPanel;

import org.jfree.chart.*;
import org.jfree.chart.axis.*;
import org.jfree.chart.plot.*;
import org.jfree.chart.renderer.xy.*;
import org.jfree.data.time.*;
import org.jfree.data.xy.*;
import org.jfree.ui.*;

public class PlotLogNuFlux extends ApplicationFrame {

    public PlotLogNuFlux(String title) {
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
            "The LOFAR Transient Pipeline - Number of sources to be expected",  // title
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

        //NumberAxis axis = (NumberAxis) plot.getDomainAxis();
	NumberAxis domainAxis = new LogarithmicAxis("S (mJy)");
	NumberAxis rangeAxis = new LogarithmicAxis("(dN/dS)/S^-2.5 (Jy^1.5 sr^-1)");// array om links en rechts waarden te displayen!
	plot.setDomainAxis(domainAxis);
	plot.setRangeAxis(rangeAxis);
	//rangeAxis.setRange(1, 1000);
	//domainAxis.setRange(0.01, 10000);
        return chart;
    }
    
    private static XYDataset createDataset() {

        XYSeries s1 = new XYSeries("Radio Source Counts");
        XYSeries s2 = new XYSeries("minus one");
        XYSeries s3 = new XYSeries("minus two");
	double sum = 0;
	double Smin = 0.01;
	double Smax = 10000;
	double dS = Smin;
	double numin = 10;
	double dnu = 1;
	double numax = 90;
	double nu = 0, nufirst = 0;
	double nuMHz = 0;
	double y = 0;
	double S = 0, Sfirst = 0, S2 = 0, S3 = 0;
	int block = 0;
	//double[] a = {0.841, 0.540, 0.364, -0.063, -0.107, 0.052, -0.007};
	//while (nu <= numax) {
		//nufirst = numin * Math.pow(10, block);
		//dnu = nufirst;
		//S = Sfirst;
		nufirst = numin;
		nuMHz = nufirst * 1000000;
		for (int i = 0; i < 100; i++) {
			S = Math.pow(nuMHz, -0.7);
			S2 = Math.pow(nuMHz, -1.0);
			S3 = Math.pow(nuMHz, -2.0);
			s1.add(nuMHz, S);
			s2.add(nuMHz, S2);
			s3.add(nuMHz, S3);
			//System.out.println("i = " + i + ", nu = " + nu);
			nu = nu + dnu;
			nuMHz = nu * 1000000;
		}
		//block++;
	//}
	//System.out.println("Smax, S = " + Smax + ", " + S);

	XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(s1);
        dataset.addSeries(s2);
        dataset.addSeries(s3);

        return dataset;
    }

    public static JPanel createDemoPanel() {
        JFreeChart chart = createChart(createDataset());
        return new ChartPanel(chart);
    }
    
    public static void main(String[] args) {

        PlotLogNuFlux demo = new PlotLogNuFlux("Pipeline processing times");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}

