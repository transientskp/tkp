package org.lofar.services;

import edu.jhu.htm.core.*;
import edu.jhu.htm.geometry.*;
import java.util.*;

public class Conversion {

	/**
	 * ra in units hms but separated by spaces
	 */
        public static double fromRAToDegrees(String ra) {
                String inputStr = ra;
	        String patternStr = " ";
        	String[] fields = inputStr.split(patternStr);
	        return (((((Double.parseDouble(fields[2]) / 60) + Double.parseDouble(fields[1])) / 60) + Double.parseDouble(fields[0])) / 24) * 360;
        }

	/**
	 * ra in units hms but separated by spaces
	 */
        public static double fromRAToRadians(String ra) {
                String inputStr = ra;
	        String patternStr = " ";
        	String[] fields = inputStr.split(patternStr);
	        return (((((Double.parseDouble(fields[2]) / 60) + Double.parseDouble(fields[1])) / 60) + Double.parseDouble(fields[0])) / 24) 
				* 2 * Math.PI;
        }

	/**
	 * dec in units deg amin asec but separated by spaces
	 */
        public static double fromDECToDegrees(String dec) {
                String inputStr = dec;
	        String patternStr = " ";
        	String[] fields = inputStr.split(patternStr);
		if ("-".equals(fields[0].substring(0, 1))) {
               	  return (-1 * (((Math.abs(Double.parseDouble(fields[2])) / 60) + Double.parseDouble(fields[1])) / 60) + Double.parseDouble(fields[0]));
        	} else {
                  return (((Double.parseDouble(fields[2]) / 60) + Double.parseDouble(fields[1])) / 60) + Double.parseDouble(fields[0]);
        	}
        }

	/**
	 * dec in units deg amin asec but separated by spaces
	 */
        public static double fromDECToRadians(String ra) {
                String inputStr = ra;
	        String patternStr = " ";
        	String[] fields = inputStr.split(patternStr);
		if (ra.substring(0, 1).equals("-")) {
	        	return ((((Double.parseDouble(fields[2]) / 60) + Double.parseDouble(fields[1])) / 60) + Double.parseDouble(fields[0])) 
				* -1 * Math.PI / 180;
		} else {
	        	return ((((Double.parseDouble(fields[2]) / 60) + Double.parseDouble(fields[1])) / 60) + Double.parseDouble(fields[0])) 
				* Math.PI / 180;
		}
        }

}
