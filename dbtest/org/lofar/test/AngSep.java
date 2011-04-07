package org.lofar.test;

import java.io.*;

import org.lofar.services.Conversion;

public class AngSep {

	public static void main(String[] args) {
		double a1 = Double.parseDouble(args[0]);
		double d1 = Double.parseDouble(args[1]);
		double a2 = Double.parseDouble(args[2]);
		double d2 = Double.parseDouble(args[3]);

		double arg = Math.sin(d1) * Math.sin(d2) + Math.cos(d1) * Math.cos(d2) * Math.cos(a1 - a2);
		double angsep = Math.acos(arg);
		System.out.println("a1 = " + a1 + "d1 = " + d1 + "a2 = " + a2 + "d2 = " + d2 + "angsep = " + angsep);

	}
}
