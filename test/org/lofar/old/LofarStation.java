package org.lofar.data;

import java.util.*;

import org.lofar.util.*;
import org.lofar.services.*;

public class LofarStation {

	public static void main(String[] args) {

		long start = System.currentTimeMillis();

		LofarData lofarData = new LofarData();

		DatabaseStorage dbStorage = new DatabaseStorage(lofarData);
		// TODO Maybe move the FileSystemStorage part to the DatabaseStorage part 
		// where the store() is handled...
		FileSystemStorage fsStorage = new FileSystemStorage(lofarData);

		// TODO Every next image (UV or image data?) should be added to previous
		// in this way we will get the logarithmic timeseries
		// 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000 seconds
		
		// each image that is built up in this way 
		// has to go to SExtractor

		SExtractorService sextr = new SExtractorService();
		List sources = sextr.getSourcesFromFile("files/sources/radec_corners.xml");

		//int i = 0;
		for (Iterator iter = sources.iterator(); iter.hasNext();) {
			//Source src = (Source) iter.next();
			//System.out.println("Source[" + i++ + "]: htmid = " + src.getHtmId() + "; ra = " + src.getRA());
			lofarData.setMeasurements((Source)iter.next());
		}
		
		float elapsed = (System.currentTimeMillis() - start) / 1000f;
                System.out.println("LofarStation Elapsed time: " + elapsed + " s");
	}

}
