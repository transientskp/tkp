/* -------------------------
 * XYErrorRendererDemo2.java
 * -------------------------
 * (C) Copyright 2007, by Object Refinery Limited.
 *
 */

package org.lofar.plot;

import java.awt.Color;

import javax.swing.JPanel;

import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYErrorRenderer;
import org.jfree.data.xy.IntervalXYDataset;
import org.jfree.data.xy.YIntervalSeries;
import org.jfree.data.xy.YIntervalSeriesCollection;
import org.jfree.ui.ApplicationFrame;
import org.jfree.ui.RefineryUtilities;

/**
 * A line chart with error bars.
 */
public class XYErrorRendererDemo2 extends ApplicationFrame {

    /**
     * Constructs the demo application.
     *
     * @param title  the frame title.
     */
    public XYErrorRendererDemo2(String title) {
        super(title);
        JPanel chartPanel = createDemoPanel();
        chartPanel.setPreferredSize(new java.awt.Dimension(500, 270));
        setContentPane(chartPanel);
    }
   
    /**
     * Creates a chart.
     *
     * @param dataset  the dataset.
     *
     * @return The chart.
     */
    private static JFreeChart createChart(IntervalXYDataset dataset) {
        NumberAxis xAxis = new NumberAxis("X");
        NumberAxis yAxis = new NumberAxis("Y");
        XYErrorRenderer renderer = new XYErrorRenderer();
        renderer.setBaseLinesVisible(true);
        renderer.setBaseShapesVisible(false);
        XYPlot plot = new XYPlot(dataset, xAxis, yAxis, renderer);
       
        plot.setBackgroundPaint(Color.lightGray);
        plot.setDomainGridlinePaint(Color.white);
        plot.setRangeGridlinePaint(Color.white);
       
        JFreeChart chart = new JFreeChart("XYErrorRenderer Demo 2", plot);
        chart.setBackgroundPaint(Color.white);
       
        return chart;
    }
   
    /**
     * Creates a sample dataset.
     */
    private static IntervalXYDataset createDataset() {
        YIntervalSeriesCollection dataset = new YIntervalSeriesCollection();
        YIntervalSeries s1 = new YIntervalSeries("Series 1");
        s1.add(1.0, 10.0, 9.0, 11.0);
        s1.add(10.0, 6.1, 4.34, 7.54);
        s1.add(17.8, 4.5, 3.1, 5.8);
        YIntervalSeries s2 = new YIntervalSeries("Series 2");
        s2.add(3.0, 7.0, 6.0, 8.0);
        s2.add(13.0, 13.0, 11.5, 14.5);
        s2.add(24.0, 16.1, 14.34, 17.54);
        dataset.addSeries(s1);
        dataset.addSeries(s2);
        return dataset;
    }
   
    /**
     * Creates a panel for the demo.
     * 
     * @return A panel.
     */
    public static JPanel createDemoPanel() {
        return new ChartPanel(createChart(createDataset()));
    }
   
    /**
     * Starting point for the demonstration application.
     *
     * @param args  ignored.
     */
    public static void main(String[] args) {
        XYErrorRendererDemo2 demo = new XYErrorRendererDemo2(
                "JFreeChart: XYErrorRendererDemo2");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);
    }

}
