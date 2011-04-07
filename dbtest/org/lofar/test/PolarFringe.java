/* ===========================================================
 * JFreeChart : a free chart library for the Java(tm) platform
 * ===========================================================
 *
 * (C) Copyright 2000-2005, by Object Refinery Limited and Contributors.
 *
 * Project Info:  http://www.jfree.org/jfreechart/index.html
 *
 * This library is free software; you can redistribute it and/or modify it 
 * under the terms of the GNU Lesser General Public License as published by 
 * the Free Software Foundation; either version 2.1 of the License, or 
 * (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful, but 
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY 
 * or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public 
 * License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License 
 * along with this library; if not, write to the Free Software Foundation, 
 * Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 *
 * [Java is a trademark or registered trademark of Sun Microsystems, Inc. 
 * in the United States and other countries.]
 *
 * -------------------------
 * TimeSeriesChartDemo1.java
 * -------------------------
 * (C) Copyright 2003-2005, by Object Refinery Limited and Contributors.
 *
 * Original Author:  David Gilbert (for Object Refinery Limited);
 * Contributor(s):   ;
 *
 * $Id: TimeSeriesChartDemo1.java,v 1.2 2005/03/28 19:38:45 mungady Exp $
 *
 * Changes
 * -------
 * 09-Mar-2005 : Version 1, copied from the demo collection that ships with
 *               the JFreeChart Developer Guide (DG);
 *
 */

package org.lofar.test;

import java.awt.Color;
import java.text.SimpleDateFormat;

import javax.swing.JPanel;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.CategoryAxis;
import org.jfree.chart.axis.DateAxis;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.PolarPlot;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.PolarItemRenderer;
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

/**
 * An example of a time series chart.  For the most part, default settings are 
 * used, except that the renderer is modified to show filled shapes (as well as 
 * lines) at each data point.
 */
public class PolarFringe extends ApplicationFrame {

    /**
     * A demonstration application showing how to create a simple time series 
     * chart.  This example uses monthly data.
     *
     * @param title  the frame title.
     */
    public PolarFringe(String title) {
        super(title);
        XYDataset dataset = createDataset();
        JFreeChart chart = createChart(dataset);
        ChartPanel chartPanel = new ChartPanel(chart, false);
        chartPanel.setPreferredSize(new java.awt.Dimension(600, 600));
        chartPanel.setMouseZoomable(true, false);
        setContentPane(chartPanel);
    }

    /**
     * Creates a chart.
     * 
     * @param dataset  a dataset.
     * 
     * @return A chart.
     */
    private static JFreeChart createChart(XYDataset dataset) {
        
        JFreeChart chart = ChartFactory.createXYLineChart(
            "Fringe Pattern",  // title
            "x", 
            "y", 
            dataset,            // data
            PlotOrientation.VERTICAL,
            false,               // create legend?
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
    
    /**
     * Creates a dataset, consisting of two series of monthly data.
     *
     * @return The dataset.
     */
    private static XYDataset createDataset() {
        
        double thetaFirst = 0;
        double thetaLast = 2*Math.PI;
        int steps = 1000;
        double dTheta = (thetaLast - thetaFirst) / steps;
        System.out.println("thetaFirst = " + thetaFirst + "; thetaLast= " + thetaLast + "; dTheta = " + dTheta);

        double[] x = new double[steps + 1];
        double[] y = new double[steps + 1];
        double[] r = new double[steps + 1];
        double[] th = new double[steps + 1];
        double[] degree = new double[steps + 1];
        double[] f1 = new double[steps + 1];
        double[] f2 = new double[steps + 1];
        double[] f3 = new double[steps + 1];
        double er = 0;
        double theta = thetaFirst;
        double iks = 0;
        double ij = 0;
        double q = 1.6E-19;
        double c = 3.0E8;
        double constant = (q * q) / (4 * Math.PI * c * c * c);

        XYSeries xy1 = new XYSeries("Fringe function", false, true);
        XYSeries xy2 = new XYSeries("Fringe function", false, true);
        XYSeries xy3 = new XYSeries("Fringe function", false, true);
        XYSeries xy4 = new XYSeries("Fringe function", false, true);
        XYSeries xy5 = new XYSeries("Fringe function", false, true);
        XYSeries xy6 = new XYSeries("Line", false, true);

        for (int i = 0; i <= steps; i++) {
            th[i] = theta;
            degree[i] = theta * 180 / Math.PI;
            //f1[i] = 1 - 0.5 * Math.cos(theta);
            //f2[i] = Math.sin(theta) * Math.sin(theta);
            r[i] = 1;
            x[i] = r[i] * Math.cos(theta);
            y[i] = r[i] * Math.sin(theta);
            xy1.add(x[i], y[i]);
            
            r[i] = 2;
            x[i] = r[i] * Math.cos(theta);
            y[i] = r[i] * Math.sin(theta);
            xy2.add(x[i], y[i]);
            
            r[i] = 5;
            x[i] = r[i] * Math.cos(theta);
            y[i] = r[i] * Math.sin(theta);
            xy3.add(x[i], y[i]);
            
            r[i] = 10;
            x[i] = r[i] * Math.cos(theta);
            y[i] = r[i] * Math.sin(theta);
            xy4.add(x[i], y[i]);
            
            r[i] = 20;
            x[i] = r[i] * Math.cos(theta);
            y[i] = r[i] * Math.sin(theta);
            xy5.add(x[i], y[i]);
            
	    x[i] = i;
	    y[i] = i;
	    xy6.add(x[i], y[i]);
	    
            theta = theta + dTheta;
            System.out.println("degree[" + i + "] = " + degree[i]
                                + "; th[" + i + "] = " + th[i] 
                                + "; r[" + i + "] = " + r[i] 
                                + "; x[" + i + "] = " + x[i] 
                                + "; y[" + i + "] = " + y[i]);
        }
        
        
        //XYDataset dataset = new XYSeriesCollection(xy1);
        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(xy1);
        dataset.addSeries(xy2);
        dataset.addSeries(xy3);
        dataset.addSeries(xy4);
        dataset.addSeries(xy5);
        dataset.addSeries(xy6);
        
        return dataset;
        
        /*
        double xFirst = -1.0;
        double xLast = 1.0;
        int steps = 1000;
        double dx = (xLast - xFirst) / steps;
        System.out.println("xFirst = " + xFirst + "; xLast= " + xLast + "; dx = " + dx);

        double[] y = new double[steps + 1];
        double[] iks = new double[steps + 1];
        //double[] r = new double[steps + 1];
        //double[] theta = new double[steps + 1];
        double x = xFirst;

        XYSeries xy1 = new XYSeries("Fringe function");
        for (int i = 0; i <= steps; i++) {
            iks[i] = x;
            //y[i] = 2 * Math.exp(-2 * Math.PI * Math.PI * x * x) * Math.cos(2 * Math.PI * 6 * x);
            y[i] = Math.sqrt(1 - x * x);
            xy1.add(iks[i], y[i]);
            x = x + dx;
            System.out.println("iks[" + i + "] = " + iks[i] + "; y[" + i + "] = " + y[i]);
        }
        
        /*x = xFirst;
        XYSeries xy2 = new XYSeries("Fringe function");
        
        for (int i = 0; i <= steps; i++) {
            iks[i] = x;
            y[i] = 2 * Math.exp(-2 * Math.PI * Math.PI * x * x);
            xy2.add(iks[i], y[i]);
            x = x + dx;
            System.out.println("iks[" + i + "] = " + iks[i] + "; y[" + i + "] = " + y[i]);
        }
        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(xy1);
        //dataset.addSeries(xy2);
        
        return dataset;
        */

    }

    /**
     * Creates a panel for the demo (used by SuperDemo.java).
     * 
     * @return A panel.
     */
    public static JPanel createDemoPanel() {
        JFreeChart chart = createChart(createDataset());
        return new ChartPanel(chart);
    }
    
    /**
     * Starting point for the demonstration application.
     *
     * @param args  ignored.
     */
    public static void main(String[] args) {

        PolarFringe demo = new PolarFringe("Fringe Function");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

    
}
