package org.lofar.data;

import org.lofar.util.Observer;
import org.lofar.util.Subject;

public class FileSystem extends StorageSystem implements Observer {

	private Source source;
	private Subject lofarData;

	public FileSystem(Subject lofarData) {
		// The constructor is passed the lofarData object (the Subject)
		// and we use it to register the DatabaseSystem as an observer
		this.lofarData = lofarData;
		lofarData.registerObserver(this);
		// The DatabaseSystem uses the StoreInDatabase class 
		// as its StoreBehavior type
		storeBehavior = new StoreInFile();
	}

	public void update(Source src) {
		this.source = src;
		performStore();
	}

	public void display() {
		System.out.println("In de DB System");
	}

}
