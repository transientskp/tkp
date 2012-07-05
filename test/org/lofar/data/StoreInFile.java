package org.lofar.data;

public class StoreInFile implements StoreBehavior {

	public void store(Source src) {
		System.out.println("Source: " + src.getHtmId() + " observed at: " + src.getObsTime() + " stored on FS!");
	}
}
