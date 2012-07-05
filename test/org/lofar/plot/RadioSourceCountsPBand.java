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

public class RadioSourceCountsPBand extends ApplicationFrame {

    public RadioSourceCountsPBand(String title) {
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
            "dN/dS (sr^-1)",
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

        //NumberAxis domainAxis = (NumberAxis) plot.getDomainAxis();
        //NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
	NumberAxis domainAxis = new LogarithmicAxis("S");
	NumberAxis rangeAxis = new LogarithmicAxis("dN/dS (sr^-1)");// array om links en rechts waarden te displayen!
	plot.setDomainAxis(domainAxis);
	plot.setRangeAxis(rangeAxis);
	//rangeAxis.setRange(0.001, 1000);
	//domainAxis.setRange(0.01, 100);
        return chart;
    }
    
    private static XYDataset createDataset() {

        double S = 0, Smin = 0.001, Smax = 10, Sfirst = 0;
        double dS = 0;
	double N = 0;
	final double[] a = {0.841, 0.540, 0.364, -0.063, -0.107, 0.052, -0.007};
	double fac = 0, sum = 0;
	int block = 0;
	double noem = 0;

        XYSeries s1 = new XYSeries("Extragalactic Source Counts at 1.4GHz");
	System.out.println("\t S \t N(S) \t fac \t sum \t noem");
	System.out.println("---------------------------");

	S = Smin;
        while (S <= Smax) {
		Sfirst = Smin * Math.pow(10, block);
		dS = Sfirst;
		S = Sfirst;
		for (int l = 0; l < 9 & S <= Smax; l++) {
			sum = 0;
			for (int i = 0; i < a.length; i++) {
				fac = a[i] * (Math.pow(Math.log10(S * 1000), i));
				sum = sum + fac;
			}
			noem = Math.pow(S, 2.5);
			N = Math.pow(10, sum) / noem;
			System.out.println("\t" + S + "\t" + N + "\t" + fac + "\t" + sum + "\t" + noem);
			s1.add(S, N);
        	        S = S + dS;
		}
		block++;
        }

	// En hier integreren
	// aannemende dat er geen rand is...
	/*System.out.println("dS \t mdS \t dN \t N"); 
	dS = dS / 100;
	double mdS = Smin; 
	N = 0;
	double dN = 0;
	while (mdS < Smax) {
		dN = 3 * mdS * mdS * dS;
		N += dN;
		System.out.println(dS + "\t" + mdS + "\t" + dN + "\t" + N); 
		mdS = mdS + dS;
	}
	System.out.println("Laatste waarden: " + dS + "\t" + mdS + "\t" + dN + "\t" + N); */

	

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

        RadioSourceCountsPBand demo = new RadioSourceCountsPBand("Source counts");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}

