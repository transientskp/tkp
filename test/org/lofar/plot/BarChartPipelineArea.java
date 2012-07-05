package org.lofar.plot;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.GradientPaint;
import java.io.*;
import java.util.*;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.CategoryAxis;
import org.jfree.chart.axis.CategoryLabelPositions;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.CategoryPlot;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.renderer.category.BarRenderer;
import org.jfree.chart.title.LegendTitle;
import org.jfree.data.category.CategoryDataset;
import org.jfree.data.category.DefaultCategoryDataset;
import org.jfree.ui.ApplicationFrame;
import org.jfree.ui.RectangleEdge;
import org.jfree.ui.RefineryUtilities;

public class BarChartPipelineArea extends ApplicationFrame {

    public BarChartPipelineArea(String title) {

        super(title);
        CategoryDataset dataset = createDataset();
        JFreeChart chart = createChart(dataset);
        ChartPanel chartPanel = new ChartPanel(chart, false);
        chartPanel.setPreferredSize(new Dimension(750, 270+135));
        setContentPane(chartPanel);

    }

    private static CategoryDataset createDataset() {
        
        String[] series = {"MySQL: LOAD DATA INFILE", "MonetDB: LOAD DATA INFILE", "MonetDB64: LOAD DATA INFILE", "MonetDB BeoWulf: LOAD DATA INFILE"};

        DefaultCategoryDataset dataset = new DefaultCategoryDataset();

	// Collect log files w/ data
	String logMySQLDir = "files/dbtests/pipeline/mysql-32bit/infile/";
	String logMonetDBDir = "files/dbtests/pipeline/monetdb-32bit/infile/";
	String logMonetDB64Dir = "files/dbtests/pipeline/monetdb64/infile/";
	String logBeoMonetDBDir = "files/dbtests/pipeline/beowulf/monetdb/infile/";
	File mysqldir = new File(logMySQLDir);
	File monetdbdir = new File(logMonetDBDir);
	File monetdb64dir = new File(logMonetDB64Dir);
	File beomonetdbdir = new File(logBeoMonetDBDir);
	File[] dirs = {mysqldir, monetdbdir, monetdb64dir, beomonetdbdir};
    
	FileFilter fileFilter = new FileFilter() {
       		public boolean accept(File file) {
       			return file.getName().endsWith(".log");
        	}
	};	

	for (int j = 0; j < dirs.length; j++) {
		try {
    			File[] files = dirs[j].listFiles(fileFilter);
			//System.out.println("dirs[" + j + "] = " + dirs[j].getName());
			//System.out.println("|");
			int Nimg = 0, Nbands = 10, Nbeams = 10, Nsrc = 0, Nrows = 0;
			double millisecs = 0, secs = 0;
			BufferedReader logFile;
			String[] fileNames = new String[files.length];
			for (int i = 0; i < files.length; i++) {
	        	        System.out.println("unsorted file names [" + i + "] = " + files[i].getName());
				fileNames[i] = files[i].getName();
			}
			Arrays.sort(fileNames);
			for (int i = 0; i < fileNames.length; i++) {
	        	        System.out.println("sorted file names [" + i + "] = " + fileNames[i]);
			}

			for (int i = 0; i < fileNames.length; i++) {
	        	        //System.out.println("+-- files[" + i + "] = " + files[i].getName());
			
				//int index = Arrays.binarySearch(sortedFileNames);
				//logFile = new BufferedReader(new FileReader(files[i]));
				logFile = new BufferedReader(new FileReader("" + dirs[j] + "/" + fileNames[i]));
	                        String str;
				String patternStr = "\t";
				String[] fields;
				Nrows = 0;
				String category = null;
				Nimg = 0;
				Nsrc = 0;
				secs = 0;
	                        while ((str = logFile.readLine()) != null) {
					Nrows++;
                	                fields = str.split(patternStr);
					//for (int k = 0; k < fields.length; k++) {
					//	System.out.println("    |  ");
					//	System.out.println("    +--fields[" + k + "] = " + fields[k]);
					//}
					Nimg = Integer.parseInt(fields[0]);
					//System.out.println("Nimg = " + Nimg);
					Nsrc = Integer.parseInt(fields[3]);
					secs = secs + Double.parseDouble(fields[4]);
	                        }
				//category = "Nimg=" + Nimg + ",Nsrc=" + Nsrc;
				category = Nimg + ", " + Nsrc;
				millisecs = 1000 * secs / Nrows;
				//System.out.println("secavg = " + secs);
				//System.out.println("category = " + category);
        			dataset.addValue(Math.log10(millisecs), series[j], category);
                	        logFile.close();
			}

	        } catch (IOException e) {
        	        System.err.println("IOException @ createDataset: " + e.getMessage());
                	System.exit(1);
	        }
	}
		
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
            "Pipeline Area Insert Times by loading from file, DBs compared",
            "Number of seconds & number of sources per image (Every image: 10 beams, 10 frequencies)",
            "log milliseconds",   // range axis label
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

	LegendTitle legend = chart.getLegend();
        legend.setItemFont(new java.awt.Font("Lucinda", java.awt.Font.PLAIN, 12));
        //legend.setPosition(RectangleEdge.RIGHT);

        // get a reference to the plot for further customisation...
        CategoryPlot plot = chart.getCategoryPlot();
        //plot.setBackgroundPaint(Color.lightGray);
        plot.setBackgroundPaint(Color.white);
        //plot.setDomainGridlinePaint(Color.white);
        plot.setDomainGridlinePaint(Color.lightGray);
        plot.setDomainGridlinesVisible(true);
        //plot.setRangeGridlinePaint(Color.white);
        plot.setRangeGridlinePaint(Color.lightGray);

	//LegendTitle legend = chart.getLegend();
	//legend.

        // set the range axis to display integers only...
        final NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
        rangeAxis.setStandardTickUnits(NumberAxis.createIntegerTickUnits());
	rangeAxis.setLowerBound(0.9);
        rangeAxis.setUpperBound(7);
        rangeAxis.setLabelFont(fontje);
        rangeAxis.setTickLabelFont(fontje);

        // disable bar outlines...
        BarRenderer renderer = (BarRenderer) plot.getRenderer();
        renderer.setDrawBarOutline(false);
        
        // set up gradient paints for series...
        /*GradientPaint gp0 = new GradientPaint(0.0f, 0.0f, Color.blue, 0.0f, 0.0f, new Color(0, 0, 64));
        GradientPaint gp1 = new GradientPaint(0.0f, 0.0f, Color.green, 0.0f, 0.0f, new Color(0, 64, 0));
        GradientPaint gp2 = new GradientPaint(0.0f, 0.0f, Color.red, 0.0f, 0.0f, new Color(64, 0, 0));
        renderer.setSeriesPaint(0, gp0);
        renderer.setSeriesPaint(1, gp1);
        renderer.setSeriesPaint(2, gp2);*/

	//NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
	//rangeAxis.setLowerBound(-1);
	//rangeAxis.setUpperBound(5);
        CategoryAxis domainAxis = plot.getDomainAxis();
	//domainAxis.setCategoryLabelPositionOffset(10);
        //domainAxis.setCategoryLabelPositions(CategoryLabelPositions.createUpRotationLabelPositions(0));
        domainAxis.setCategoryLabelPositions(CategoryLabelPositions.createUpRotationLabelPositions(Math.PI/6));
	//domainAxis.setCategoryLabelPositions(CategoryLabelPositions.createUpRotationLabelPositions(0));
        java.awt.Font fontje2 = new java.awt.Font("Lucinda", java.awt.Font.BOLD, 10);
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

        BarChartPipelineArea demo = new BarChartPipelineArea("Pipeline Area Insert Times");
        demo.pack();
        RefineryUtilities.centerFrameOnScreen(demo);
        demo.setVisible(true);

    }

}
