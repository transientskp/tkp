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
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, 
 * USA.  
 *
 * [Java is a trademark or registered trademark of Sun Microsystems, Inc. 
 * in the United States and other countries.]
 *
 * ------------------
 * TPCHBenchmarkComparison.java
 * ------------------
 * (C) Copyright 2003-2005, by Object Refinery Limited and Contributors.
 *
 * Original Author:  David Gilbert (for Object Refinery Limited);
 * Contributor(s):   ;
 *
 * $Id: TPCHBenchmarkComparison.java,v 1.1.2.1 2005/10/25 20:41:32 mungady Exp $
 *
 * Changes
 * -------
 * 09-Mar-2005 : Version 1, copied from the demo collection that ships with
 *               the JFreeChart Developer Guide (DG);
 *
 */

//package org.jfree.chart.demo;
package org.lofar.plot;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.GradientPaint;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.CategoryAxis;
import org.jfree.chart.axis.CategoryLabelPositions;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.CategoryPlot;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.renderer.category.BarRenderer;
import org.jfree.data.category.CategoryDataset;
import org.jfree.data.category.DefaultCategoryDataset;
import org.jfree.ui.ApplicationFrame;
import org.jfree.ui.RefineryUtilities;

/**
 * A simple demonstration application showing how to create a bar chart.
 */
public class TPCHBenchmarkComparison extends ApplicationFrame {

    /**
     * Creates a new demo instance.
     *
     * @param title  the frame title.
     */
    public TPCHBenchmarkComparison(String title) {

        super(title);
        CategoryDataset dataset = createDataset();
        JFreeChart chart = createChart(dataset);
        ChartPanel chartPanel = new ChartPanel(chart, false);
        chartPanel.setPreferredSize(new Dimension(750, 270+135));
        setContentPane(chartPanel);

    }

    /**
     * Returns a sample dataset.
     * 
     * @return The dataset.
     */
    private static CategoryDataset createDataset() {
        
        // row keys...
        String db1 = "MonetDB5";
        String db2 = "PostgreSQL 8.1";
        String db3 = "MySQL 5.0";

        // column keys...
        String q1 = "Q1";
        String q2 = "Q2";
        String q3 = "Q3";
        String q4 = "Q4";
        String q5 = "Q5";
        String q6 = "Q6";
        String q7 = "Q7";
        String q8 = "Q8";
        String q9 = "Q9";
        String q10 = "Q10";
        String q11 = "Q11";
        String q12 = "Q12";
        String q13 = "Q13";
        String q14 = "Q14";
        String q15 = "Q15";
        String q16 = "Q16";
        String q17 = "Q17";
        String q18 = "Q18";
        String q19 = "Q19";
        String q20 = "Q20";
        String q21 = "Q21";
        String q22 = "Q22";
        String load = "Load";

        // create the dataset...
        DefaultCategoryDataset dataset = new DefaultCategoryDataset();

        dataset.addValue(Math.log10(2.8e3), db1, q1);
        dataset.addValue(Math.log10(73.7e3), db2, q1);
        dataset.addValue(Math.log10(17.6e3), db3, q1);

        dataset.addValue(Math.log10(0.6e3), db1, q2);
        dataset.addValue(Math.log10(4.6e3), db2, q2);
        dataset.addValue(Math.log10(230.7e3), db3, q2);

        dataset.addValue(Math.log10(0.5e3), db1, q3);
        dataset.addValue(Math.log10(42.2e3), db2, q3);
        dataset.addValue(Math.log10(23.3e3), db3, q3);

        dataset.addValue(Math.log10(0.7e3), db1, q4);
        dataset.addValue(Math.log10(3.4e3), db2, q4);
        dataset.addValue(Math.log10(2.1e3), db3, q4);

        dataset.addValue(Math.log10(0.6e3), db1, q5);
        dataset.addValue(Math.log10(1.6e3), db2, q5);
        dataset.addValue(Math.log10(20.2e3), db3, q5);

        dataset.addValue(Math.log10(0.4e3), db1, q6);
        dataset.addValue(Math.log10(6.9e3), db2, q6);
        dataset.addValue(Math.log10(5.9e3), db3, q6);

        dataset.addValue(Math.log10(1.4e3), db1, q7);
        dataset.addValue(Math.log10(13.9e3), db2, q7);
        dataset.addValue(Math.log10(6.0e3), db3, q7);

        dataset.addValue(Math.log10(0.7e3), db1, q8);
        dataset.addValue(Math.log10(9.9e3), db2, q8);
        dataset.addValue(Math.log10(1.4e3), db3, q8);

        dataset.addValue(Math.log10(1.1e3), db1, q9);
        dataset.addValue(Math.log10(143.9e3), db2, q9);
        dataset.addValue(Math.log10(9.9e3), db3, q9);

        dataset.addValue(Math.log10(1.4e3), db1, q10);
        dataset.addValue(Math.log10(1.5e3), db2, q10);
        dataset.addValue(Math.log10(13.3e3), db3, q10);

        dataset.addValue(Math.log10(0.2e3), db1, q11);
        dataset.addValue(Math.log10(2.2e3), db2, q11);
        dataset.addValue(Math.log10(1.3e3), db3, q11);

        dataset.addValue(Math.log10(1.5e3), db1, q12);
        dataset.addValue(Math.log10(9.1e3), db2, q12);
        dataset.addValue(Math.log10(6.6e3), db3, q12);

        dataset.addValue(Math.log10(4.0e3), db1, q13);
        dataset.addValue(Math.log10(13.8e3), db2, q13);
        //dataset.addValue(Math.log10(e3), db3, q13);

        dataset.addValue(Math.log10(0.1e3), db1, q14);
        dataset.addValue(Math.log10(5.9e3), db2, q14);
        dataset.addValue(Math.log10(30.6e3), db3, q14);

        /*dataset.addValue(Math.log10(0.3e3), db1, q15);
        dataset.addValue(Math.log10(6.2e3), db2, q15);
        //dataset.addValue(Math.log10(2643e3), db3, q15);

        dataset.addValue(Math.log10(0.7e3), db1, q16);
        dataset.addValue(Math.log10(15.6e3), db2, q16);
        dataset.addValue(Math.log10(8.4e3), db3, q16);

        dataset.addValue(Math.log10(0.7e3), db1, q17);
        //dataset.addValue(Math.log10(e3), db2, q17);
        dataset.addValue(Math.log10(1.1e3), db3, q17);

        dataset.addValue(Math.log10(2.0e3), db1, q18);
        dataset.addValue(Math.log10(15e3), db2, q18);
        //dataset.addValue(Math.log10(2643e3), db3, q18);

        dataset.addValue(Math.log10(3.1e3), db1, q19);
        dataset.addValue(Math.log10(12.7e3), db2, q19);
        dataset.addValue(Math.log10(0.4e3), db3, q19);

        dataset.addValue(Math.log10(0.8e3), db1, q20);
        //dataset.addValue(Math.log10(e3), db2, q20);
        dataset.addValue(Math.log10(0.6e3), db3, q20);

        dataset.addValue(Math.log10(4.3e3), db1, q21);
        dataset.addValue(Math.log10(49.4e3), db2, q21);
        dataset.addValue(Math.log10(5.5e3), db3, q21);

        dataset.addValue(Math.log10(0.9e3), db1, q22);
        //dataset.addValue(Math.log10(e3), db2, q22);
        dataset.addValue(Math.log10(0.5e3), db3, q22);*/

        dataset.addValue(Math.log10(118e3), db1, load);
        dataset.addValue(Math.log10(334e3), db2, load);
        dataset.addValue(Math.log10(158e3), db3, load);

        return dataset;
        
    }
    
    /**
     * Creates a sample chart.
     * 
     * @param dataset  the dataset.
     * 
     * @return The chart.
     */
    private static JFreeChart createChart(CategoryDataset dataset) {
        
        // create the chart...
        JFreeChart chart = ChartFactory.createBarChart(
            "TPC-H Benchmark Comparison, Scale Factor 1",         // chart title
            "Query",               // domain axis label
            "Log milliseconds",                  // range axis label
            dataset,                  // data
            PlotOrientation.VERTICAL, // orientation
            true,                     // include legend
            true,                     // tooltips?
            false                     // URLs?
        );

        // NOW DO SOME OPTIONAL CUSTOMISATION OF THE CHART...

        // set the background color for the chart...
        chart.setBackgroundPaint(Color.white);
	java.awt.Font fontje = new java.awt.Font("Lucinda", java.awt.Font.PLAIN, 18);
	chart.getLegend().setItemFont(fontje);

        // get a reference to the plot for further customisation...
        CategoryPlot plot = chart.getCategoryPlot();
        plot.setBackgroundPaint(Color.lightGray);
        plot.setDomainGridlinePaint(Color.white);
        plot.setDomainGridlinesVisible(true);
        plot.setRangeGridlinePaint(Color.white);

        // set the range axis to display integers only...
        final NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
        rangeAxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());
	rangeAxis.setLowerBound(1.9);
        rangeAxis.setUpperBound(6);
	rangeAxis.setLabelFont(fontje);
	rangeAxis.setTickLabelFont(fontje);

        // disable bar outlines...
        BarRenderer renderer = (BarRenderer) plot.getRenderer();
        renderer.setDrawBarOutline(false);
	renderer.setItemMargin(0);
        
        // set up gradient paints for inttime...
        /*GradientPaint gp0 = new GradientPaint(
            0.0f, 0.0f, Color.blue, 
            0.0f, 0.0f, new Color(0, 0, 64)
        );
        GradientPaint gp1 = new GradientPaint(
            0.0f, 0.0f, Color.green, 
            0.0f, 0.0f, new Color(0, 64, 0)
        );
        GradientPaint gp2 = new GradientPaint(
            0.0f, 0.0f, Color.red, 
            0.0f, 0.0f, new Color(64, 0, 0)
        );
        renderer.setSeriesPaint(0, gp0);
        renderer.setSeriesPaint(1, gp1);
        renderer.setSeriesPaint(2, gp2);*/

        CategoryAxis domainAxis = plot.getDomainAxis();
        //domainAxis.setCategoryLabelPositions(CategoryLabelPositions.createUpRotationLabelPositions(Math.PI/6));
        domainAxis.setCategoryLabelPositions(CategoryLabelPositions.createUpRotationLabelPositions(0));
	java.awt.Font fontje2 = new java.awt.Font("Lucinda", java.awt.Font.BOLD, 12);
	domainAxis.setLabelFont(fontje2);
	domainAxis.setTickLabelFont(fontje2);
        // OPTIONAL CUSTOMISATION COMPLETED.
        
        return chart;
        
    }
    
    /**
     * Starting point for the demonstration application.
     *
     * @param args  ignored.
     */
    public static void main(String[] args) {

        TPCHBenchmarkComparison demo = new TPCHBenchmarkComparison("TPC-H Benchmark Comparison");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}
