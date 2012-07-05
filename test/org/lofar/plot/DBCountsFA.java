package org.lofar.plot;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.GradientPaint;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.*;
import org.jfree.chart.axis.*;
import org.jfree.chart.axis.*;
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
public class DBCountsFA extends ApplicationFrame {

    /**
     * Creates a new demo instance.
     *
     * @param title  the frame title.
     */
    public DBCountsFA(String title) {

        super(title);
        CategoryDataset dataset = createDataset();
        JFreeChart chart = createChart(dataset);
        ChartPanel chartPanel = new ChartPanel(chart, false);
        chartPanel.setPreferredSize(new Dimension(800, 600));
        setContentPane(chartPanel);

    }

    /**
     * Returns a sample dataset.
     * 
     * @return The dataset.
     */
    private static CategoryDataset createDataset() {
        
        // row keys...
        String inttime1 = "1s";
        String inttime2 = "3s";
        String inttime3 = "10s";
        String inttime4 = "10000s";

        // column keys...
        String frequency1 = "30MHz";
        String frequency2 = "75MHz";
        String frequency3 = "120MHz";
        String frequency4 = "200MHz";

        // create the dataset...
        DefaultCategoryDataset dataset = new DefaultCategoryDataset();

        dataset.addValue(Math.log10(410.), inttime1, frequency1);
        dataset.addValue(Math.log10(46.), inttime1, frequency2);
        dataset.addValue(Math.log10(159.), inttime1, frequency3);
        dataset.addValue(Math.log10(45.), inttime1, frequency4);

        dataset.addValue(Math.log10(673.), inttime2, frequency1);
        dataset.addValue(Math.log10(77.), inttime2, frequency2);
        dataset.addValue(Math.log10(236.), inttime2, frequency3);
        dataset.addValue(Math.log10(68.), inttime2, frequency4);
        
        dataset.addValue(Math.log10(2643.), inttime3, frequency1);
        dataset.addValue(Math.log10(315.), inttime3, frequency2);
        dataset.addValue(Math.log10(923.), inttime3, frequency3);
        dataset.addValue(Math.log10(252.), inttime3, frequency4);

        dataset.addValue(Math.log10(15475.), inttime4, frequency1);
        dataset.addValue(Math.log10(1728.), inttime4, frequency2);
        dataset.addValue(Math.log10(12710.), inttime4, frequency3);
        dataset.addValue(Math.log10(3355.), inttime4, frequency4);

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
            "LOFAR Full Array",         // chart title
            "Frequency",               // domain axis label
            "Log number of sources",                  // range axis label
            dataset,                  // data
            PlotOrientation.VERTICAL, // orientation
            true,                     // include legend
            true,                     // tooltips?
            false                     // URLs?
        );

        // NOW DO SOME OPTIONAL CUSTOMISATION OF THE CHART...

        // set the background color for the chart...
        chart.setBackgroundPaint(Color.white);

        // get a reference to the plot for further customisation...
        CategoryPlot plot = chart.getCategoryPlot();
        plot.setBackgroundPaint(Color.lightGray);
        plot.setDomainGridlinePaint(Color.white);
        plot.setDomainGridlinesVisible(true);
        plot.setRangeGridlinePaint(Color.white);

        // set the range axis to display integers only...
        final NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
        //NumberAxis y_axis = new LogarithmicAxis("Number of Extragalactic sources");

        rangeAxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());

        // disable bar outlines...
        BarRenderer renderer = (BarRenderer) plot.getRenderer();
        renderer.setDrawBarOutline(false);
        
        // set up gradient paints for inttime...
        GradientPaint gp0 = new GradientPaint(
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
        renderer.setSeriesPaint(2, gp2);

        CategoryAxis domainAxis = plot.getDomainAxis();
        domainAxis.setCategoryLabelPositions(CategoryLabelPositions.createUpRotationLabelPositions(Math.PI / 6.0));
        // OPTIONAL CUSTOMISATION COMPLETED.
        //plot.setRangeAxis(y_axis);
	rangeAxis.setRange(1, 5);
        return chart;
        
    }
    
    /**
     * Starting point for the demonstration application.
     *
     * @param args  ignored.
     */
    public static void main(String[] args) {

        DBCountsFA demo = new DBCountsFA("LOFAR Full Array");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}
