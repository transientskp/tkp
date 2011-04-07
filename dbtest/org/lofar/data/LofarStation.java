package org.lofar.data;

import java.util.*;

import org.lofar.util.*;
import org.lofar.services.*;

public class LofarStation {

	public static void main(String[] args) {

		long start = System.currentTimeMillis();

		LofarData lofarData = new LofarData();

		//DatabaseStorage dbStorage = new DatabaseStorage(lofarData);
		//FileSystemStorage fsStorage = new FileSystemStorage(lofarData);

		StorageSystem db = new ModelSystem(lofarData);
		db.setStoreBehavior(new StoreInDatabase());
		StorageSystem fs = new ModelSystem(lofarData);
		fs.setStoreBehavior(new StoreInFile());

		SExtractorService sextr = new SExtractorService();
		//List sources = sextr.getSourcesFromFile("files/sources/sourcesextracted.xml");
		Source[] sources = sextr.getSourcesFromFile("files/sources/sourcesextracted.xml");

		//int i = 0;
		//for (Iterator iter = sources.iterator(); iter.hasNext();) {
			//Source src = (Source) iter.next();
			//System.out.println("Source[" + i++ + "]: htmid = " + src.getHtmId() + "; ra = " + src.getRA());
		//	lofarData.setMeasurements((Source)iter.next());
		//}

		for (int i = 0; i < sources.length; i++) {
			lofarData.setMeasurements(sources[i]);
		}
		
		float elapsed = (System.currentTimeMillis() - start) / 1000f;
                System.out.println("LofarStation Elapsed time: " + elapsed + " s");
	}

}
