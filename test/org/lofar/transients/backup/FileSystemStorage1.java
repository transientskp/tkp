package org.lofar.data;

public class FileSystemStorage implements Observer, StorageSystem {
	private Source source;
	private Subject lofarData;

	// Register the storage as an observer to 
	// the lofarData object (Subject)
	public FileSystemStorage(Subject lofarData) {
		this.lofarData = lofarData;
		lofarData.registerObserver(this);
	}

	/*
	 * TODO: Use the MVC pattern in order to make a better design 
	 * for calling store()
	 */
	public void update(Source source) {
		this.source = source;
		store();
	}

	public void store() {
		System.out.println("Source to be stored: " + 
					source.getHtmId() + ", " + 
					source.getRA() + ", " +
					source.getDec() + ", " + 
					source.getFlux() + ";");
	}
}
