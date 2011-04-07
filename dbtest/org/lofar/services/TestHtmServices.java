package org.lofar.services;

import edu.jhu.htm.core.*;
import edu.jhu.htm.geometry.*;
import edu.jhu.skiplist.*;

public class TestHtmServices {

	public static void main(String[] args) {
		long startHTM = 0, endHTM = 0, elapsedHTM = 0, totalHTM = 0;
		float elapsedHTMs = 0, totalHTMs = 0;
		for (int i = 0; i < 1; i++) {
			//try {
				startHTM = System.currentTimeMillis();
				//HTMrange range20 = HtmServices.getHtmCover(20, 284.5051751, -0.6095379, 284.5051751, -0.6095379);
				//HTMrange range20 = HtmServices.getHtmCover(20, 284.5051751, 0.6095379, 284.5051751, 0.6095379);
				HTMrange range20 = HtmServices.getHtmCover(20, 4.5051751, 0.6095379, 4.5151751, 0.6195379);
				System.out.println(range20);
				endHTM = System.currentTimeMillis();
				elapsedHTM = endHTM - startHTM;
				totalHTM = totalHTM + elapsedHTM;
			/*} catch (HTMException e) {
        	                System.err.println(e.getMessage());
                	        System.exit(1);
			} finally {*/
				elapsedHTMs = elapsedHTM / 1000f;
				System.out.println("Elapsed: " + elapsedHTMs + " s");
			//}
		}
		totalHTMs = totalHTM / 1000f;
		System.out.println("Total: " + totalHTMs + " s");
	}
}
