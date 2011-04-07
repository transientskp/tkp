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

public class PlotXYNumberOfSourcesExpected extends ApplicationFrame {

    public PlotXYNumberOfSourcesExpected(String title) {
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

        /*XYSeries s1 = new XYSeries("Extragalactic Source Counts at 1.4GHz");
	double sum = 0;
	double Smin = 0.01;
	double Smax = 10000;
	double dS = Smin;
	double fac = 0;
	double y = 0;
	double S = 0, Sfirst = 0;
	//double S[] = {290, 200, 118, 80};
	int block = 0;
	double[] a = {0.841, 0.540, 0.364, -0.063, -0.107, 0.052, -0.007};
	while (S <= Smax) {
		Sfirst = Smin * Math.pow(10, block);
		dS = Sfirst;
		S = Sfirst;
		for (int i = 0; i < 10; i++) {
			sum = 0;
			for (int j = 0; j < a.length; j++) {
				fac = a[j] * (Math.pow(Math.log10(S), j));
				//if (S > 999 & S < 1001) 
				//System.out.println("i = "  + i + ", j = " + j + ", fac = " + fac);
				sum = sum + fac;
			}
			if (sum > 0) {
				y = Math.pow(10, sum);
				s1.add(S, y);
			}
			//if (S >= 0.02) 
			//System.out.println("i = " + i + ", dS = " + dS + ", S = " + S + ", sum = " + sum + ", y = " + y);
			S = S + dS;
		}
		block++;
	}*/

        XYSeries s1 = new XYSeries("Extragalactic Source Counts at 1.4GHz");
        double sum = 0;
        double Smin = 0.01;
        double Smax = 10000;
        double dS = Smin;
        double fac = 0;
        double y = 0;
	double N = 0, Nfirst = 0, Nsecond = 0;
	double eS = 0, eSfirst = 0, eSsecond = 0;
        double S = 0, Sfirst = 0;
        //double S[] = {290, 200, 118, 80};
        int block = 0;
        double[] a = {0.841, 0.540, 0.364, -0.063, -0.107, 0.052, -0.007};
        while (S <= Smax) {
                Sfirst = Smin * Math.pow(10, block);
                dS = Sfirst;
                S = Sfirst;
		N = Nfirst;
                for (int i = 0; i < 10; i++) {
                        sum = 0;
                        for (int j = 0; j < a.length; j++) {
                                fac = a[j] * (Math.pow(Math.log10(S), j));
                                //if (S > 999 & S < 1001)
                                //System.out.println("i = "  + i + ", j = " + j + ", fac = " + fac);
                                sum = sum + fac;
                        }
			//if (S >= 354) {//30MHz
			if (S >= 240) {//75MHz
				Nsecond = Nfirst;
				//Nsecond = Nfirst;
                        	y = Math.pow((S / 1000), -2.5) * Math.pow(10, sum) * Math.pow((1400/75), -0.7);
				Nfirst = y;
                        	s1.add(S, y);
				//Nfirst = y;
				N = (Nsecond + Nfirst) / 2;
			}
                        //if (S >= 0.02)
                        System.out.println("i = " + i /*+ ", dS = " + dS*/ + ", S = " + S /*+ ", sum = " + sum*/ + ", y = " + y + ", Nfirst = " + Nfirst + ", Nsecond = " + Nsecond + ", N = " + N);
                        S = S + dS;
                }
                block++;
        }

        /*XYSeries s1 = new XYSeries("Extragalactic Source Counts at 1.4GHz (Huynh)");
        double sum = 0;
        double Smin = 0.1;
        double Smax = 10;
        double dS = Smin;
        double fac = 0;
        double y = 0;
        double S = 0, Sfirst = 0;
        //double S[] = {290, 200, 118, 80};
        int block = 0;
        double[] a = {0.841, 0.540, 0.364, -0.063, -0.107, 0.052, -0.007};
        while (S <= Smax) {
                Sfirst = Smin * Math.pow(10, block);
                dS = Sfirst;
                S = Sfirst;
                for (int i = 0; i < 10; i++) {
                        y = S * S;
                        s1.add(S, y);
                        //if (S >= 0.02)
                        System.out.println("i = " + i + ", dS = " + dS + ", S = " + S + ", sum = " + sum + ", y = " + y);
                        S = S + dS;
                }
                block++;
        }*/

	
	/*for (int i = 0; i < a.length; i++) {
		sum = sum + a[i] * Math.pow(Math.log10(S / 1000), i)
	}*/



        /*XYSeries s2 = new XYSeries("More");
        sum = 0;
        Smin = 0.1;
        Smax = 1000;
        dS = Smin;
        fac = 0;
        y = 0;
        S = 0; Sfirst = 0;
        //double S[] = {290, 200, 118, 80};
        block = 0;
        //double[] a = {0.841, 0.540, 0.364, -0.063, -0.107, 0.052, -0.007};
        while (S <= Smax) {
                Sfirst = Smin * Math.pow(10, block);
                dS = Sfirst;
                S = Sfirst;
                for (int i = 0; i < 10; i++) {
                        sum = 0;
                        for (int j = 0; j < a.length; j++) {
                                fac = a[j] * (Math.pow(Math.log10(S), j));
                                System.out.println("fac = " + fac);
                                sum = sum + fac;
                        }
                        y = Math.pow((S/1000), -2.5) * Math.pow(10, sum);
                        s2.add(S, y);
                        System.out.println("i = " + i + ", dS = " + dS + ", S = " + S + ", sum = " + sum + ", y = " + y);
                        S = S + dS;
                }
                block++;
        }*/
        //System.out.println("Smax, S = " + Smax + ", " + S);




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

        PlotXYNumberOfSourcesExpected demo = new PlotXYNumberOfSourcesExpected("Pipeline processing times");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}

