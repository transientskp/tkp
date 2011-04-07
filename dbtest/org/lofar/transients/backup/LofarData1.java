package org.lofar.data;

import java.util.*;

public class LofarData implements Subject {

	private ArrayList observers;
	private Source source;
	
	public LofarData() {
		observers = new ArrayList();
	}

	public void registerObserver(Observer o) {
		observers.add(o);
	}
	
	public void removeObserver(Observer o) {
		int i = observers.indexOf(o);
		if (i >= 0) observers.remove(i);
	}
	
	public void notifyObservers() {
		for (int i = 0; i < observers.size(); i++) {
			Observer observer = (Observer) observers.get(i);
			observer.update(source);
		}
	}
	
	/*
	 * Returns the most recent data coming from lofar;
	 * whether it is from a station, core station or the
	 * full array is not specified in this method
	 */
	public void getData() {}
	public void getUVData() {}
	public void getImage() {}
	public ArrayList getSourceList() {
		return new ArrayList();
	}

	/*
	 * This method gets called whenever the lofar measurements
	 * have been updated.
	 */
	public void measurementsChanged() {
		notifyObservers();
	}

	public void setMeasurements(Source source){
		this.source = source;
		measurementsChanged();
	}

}
