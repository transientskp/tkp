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

public class RadioSourceCountsTest extends ApplicationFrame {

    public RadioSourceCountsTest(String title) {
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
            "Source counts at 1.4 GHz [Huynh et al. (2005)]",  // title
            "S",
            "N",
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

        NumberAxis domainAxis = (NumberAxis) plot.getDomainAxis();
        NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
	//NumberAxis domainAxis = new LogarithmicAxis("S");
	//NumberAxis rangeAxis = new LogarithmicAxis("N");// array om links en rechts waarden te displayen!
	plot.setDomainAxis(domainAxis);
	plot.setRangeAxis(rangeAxis);
	//rangeAxis.setRange(0.001, 1000);
	//domainAxis.setRange(0.01, 100);
        return chart;
    }
    
    private static XYDataset createDataset() {

        double sum = 0;
        double Smin = -5;
        double Smax = 5;
        double dS = (Smax - Smin) / 100;
        double fac = 0;
        double y = 0;
	double N = 0, Nfirst = 0, Nsecond = 0;
	double eS = 0, eSfirst = 0, eSsecond = 0;
        double S = 0, Sfirst = 0, SmJy = 0;
        int block = 0;

        XYSeries s1 = new XYSeries("Extragalactic Source Counts at 1.4GHz");
	System.out.println("\t S \t N(S)");
	System.out.println("---------------------------");

	S = Smin;
        while (S <= Smax) {
                N = 3 * S * S;
		System.out.println("\t" + S + "\t" + N);
		s1.add(S, N);
                S = S + dS;
        }

	// En hier integreren
	// aannemende dat er geen rand is...
	System.out.println("dS \t mdS \t dN \t N"); 
	dS = dS / 100;
	// midden van een stukje dS
	double mdS = Smin; 
	N = 0;
	double dN = 0;
	while (mdS < Smax) {
		dN = 3 * mdS * mdS * dS;
		N += dN;
		System.out.println(dS + "\t" + mdS + "\t" + dN + "\t" + N); 
		mdS = mdS + dS;
	}
	System.out.println("Laatste waarden: " + dS + "\t" + mdS + "\t" + dN + "\t" + N); 

	

	XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(s1);
        //dataset.addSeries(s2);

        return dataset;
    }

    public static JPanel createDemoPanel() {
        JFreeChart chart = createChart(createDataset());
        return new ChartPanel(chart);
    }
    
    public static void main(String[] args) {

        RadioSourceCountsTest demo = new RadioSourceCountsTest("Source counts");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}

