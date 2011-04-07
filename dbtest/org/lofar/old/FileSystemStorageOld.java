package org.lofar.data;

import java.io.*;
import java.util.Observable;
import java.util.Observer;

public class FileSystemStorage implements Observer, StorageSystem {
	Observable observable;
	private Source source;

	public FileSystemStorage(Observable observable) {
		this.observable = observable;
		observable.addObserver(this);
	}

	/*
	 * TODO: Use the MVC pattern in order to make a better design 
	 * for calling store()
	 */
	public void update(Observable obs, Object arg) {
		if (obs instanceof LofarData) {
			long startFS = System.currentTimeMillis();
			LofarData lofarData = (LofarData) obs;
			this.source = lofarData.getSource();
			store();
			float elapsedFS = (System.currentTimeMillis() - startFS) / 1000f;
                        System.out.println("\tDatabase elapsed time: " + elapsedFS + " s");
		}
	}

	public void store() {
		try {
                        final String dir = "files/sources/lofar_rs3flux/";
			String fileName = "LFR" + source.getHtmId() + ".lfr";
                        String file = dir + fileName;
                        BufferedWriter out = new BufferedWriter(new FileWriter(file, true));
                        out.write(source.getObsTime() + ":" + source.getFlux() + ";");
                        out.close();
			System.out.println("+---------------------------");
			System.out.println("| File written: " + file);
                        System.out.println("| Flux added for source:");
                        System.out.println("| htmid = " + source.getHtmId() + "; ra = " + source.getRA() +
                                        "; dec = " + source.getDec() + "; obsTime = " + source.getObsTime() + 
					"; flux = " + source.getFlux());
                        System.out.println("+---------------------------");
                } catch (IOException e) {
                        System.err.println("-------------------------------------------------------");
                        System.err.println("- IOException @ FileSystemStorage.store()");
			System.out.println("Source to be stored on fs: " + 
						source.getHtmId() + ", " + 
						source.getRA() + ", " +
						source.getDec() + ", " + 
						source.getFlux() + ", " + 
						source.getObsTime() + ";");
                        System.err.println("- IOException Message: " + e.getMessage());
                        System.err.println("-------------------------------------------------------");
			System.exit(1);
                }

	}
}
