package org.lofar.transients;

import edu.jhu.htm.core.*;
import edu.jhu.htm.geometry.*;
import java.util.*;

public class HtmServices {

	public static long getHtmId(int level, double ra, double dec) throws HTMException {
		long htmId = -1;
		try {
			HTMindex si = new HTMindexImp(level);
			htmId = si.lookupId(ra, dec);
		} catch (HTMException e) {
			throw new HTMException(75, "Could not lookup htmId for level = " + level + ", ra = " + ra + ", dec = " + dec);
		}
		return htmId;
	}

	public static HTMrange getHtmCover(int level, double tlRA, double tlDEC, double brRA, double brDEC) throws HTMException {
		HTMrange range = null;
		try {
			HTMindex si = new HTMindexImp(level);
        	        Rect rec = new Rect(tlRA, tlDEC, brRA, brDEC);
                	Domain dom = rec.getDomain();
	                dom.setOlevel(level);
        	        range = new HTMrange();
                	dom.intersect((HTMindexImp) si, range, false);
		} catch (Exception e) {
			String message = "Could not retrieve htmIds for level = " + level + ", tlRA = " + tlRA + ", tlDEC = " + tlDEC + 
						", brRA = " + brRA + ", brDEC = " + brDEC;
			throw new HTMException(76, message);
		}
		return range;

	}

	public static void systemOutPrintln(boolean out, String message) {
		if (out) System.out.println(message);
	}
	
}
