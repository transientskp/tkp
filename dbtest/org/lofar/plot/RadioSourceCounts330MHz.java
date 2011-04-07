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

public class RadioSourceCounts330MHz extends ApplicationFrame {

    public RadioSourceCounts330MHz(String title) {
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
	rangeAxis.setRange(1, 1000);
	//domainAxis.setRange(0.01, 10000);
        return chart;
    }
    
    private static XYDataset createDataset() {

        double sum = 0;
        double Smin = 0.00001;
        double Smax = 10;
        double dS = Smin;
        double fac = 0;
        double y = 0;
	double N = 0, Nfirst = 0, Nsecond = 0;
	double eS = 0, eSfirst = 0, eSsecond = 0;
        double S = 0, Sfirst = 0, SmJy = 0;
        int block = 0;
        final double[] a = {0.841, 0.540, 0.364, -0.063, -0.107, 0.052, -0.007};

        XYSeries s1 = new XYSeries("Extragalactic Source Counts at 1.4GHz");
	System.out.println("i \t S \t\t SmJy \t\t sum \t\t y" /*\t\t Nfirst \t\t Nsecond \t\t N\t\t"*/);
	System.out.println("-------");
        while (S <= Smax) {
                Sfirst = Smin * Math.pow(10, block);
                dS = Sfirst;
                S = Sfirst;
		N = Nfirst;
                for (int i = 0; i < 10; i++) {
                        sum = 0;
                        for (int j = 0; j < a.length; j++) {
                                fac = a[j] * (Math.pow(Math.log10(S * 1000), j));
                                sum = sum + fac;
                        }
			y = Math.pow(10, sum);
			SmJy = S * 1000;
			s1.add(SmJy, y);
                        System.out.println(i + "\t" + S + "\t" + SmJy + "\t" + sum + "\t" + y + "\t" /*+ Nfirst + "\t" + Nsecond + "\t" + N*/);
                        S = S + dS;
                }
                block++;
        }

        sum = 0;
        Smin = 0.00001;
        Smax = 10;
        dS = Smin;
        fac = 0;
        y = 0;
	N = 0; Nfirst = 0; Nsecond = 0;
	eS = 0; eSfirst = 0; eSsecond = 0;
        S = 0; Sfirst = 0; SmJy = 0;
        block = 0;
	double S330 = 0;

	double scaleFactor = Math.pow((3.30/14.00), -0.7);

        XYSeries s2 = new XYSeries("Extragalactic Source Counts at 330MHz");
	System.out.println("i \t S \t\t S330 \t\t SmJy \t\t sum \t\t y" /*\t\t Nfirst \t\t Nsecond \t\t N\t\t"*/);
	System.out.println("-------");
        while (S <= Smax) {
                Sfirst = Smin * Math.pow(10, block);
                dS = Sfirst;
                S = Sfirst;
		N = Nfirst;
		S330 = scaleFactor * S;
                for (int i = 0; i < 10; i++) {
                        sum = 0;
                        for (int j = 0; j < a.length; j++) {
                                fac = a[j] * (Math.pow(Math.log10(S330 * 1000), j));
                                sum = sum + fac;
                        }
			y = Math.pow(10, sum);
			SmJy = S330 * 1000;
			s2.add(SmJy, y);
                        System.out.println(i + "\t" + S + "\t" + S330 + "\t" + SmJy + "\t" + sum + "\t" + y + "\t" /*+ Nfirst + "\t" + Nsecond + "\t" + N*/);
                        S = S + dS;
                }
                block++;
        }

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

        RadioSourceCounts330MHz demo = new RadioSourceCounts330MHz("Source counts");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}

