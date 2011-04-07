package org.lofar.data;

import java.util.ArrayList;

public class LofarData implements Subject {

	private ArrayList observers;
	private Source source;
	private Source[] sources;
	
	public LofarData() {
		observers = new ArrayList();
	}
	
	// Subject interface method is implemented
	public void registerObserver(Observer o) {
		observers.add(o);
	}

	// Subject interface method is implemented
	public void removeObserver(Observer o) {
		int i = observers.indexOf(o);
		if (i >= 0) observers.remove(i);
	}

	// Subject interface method is implemented
	public void notifyObservers() {
		for (int i = 0; i < observers.size(); i++) {
			Observer observer = (Observer) observers.get(i);
			observer.update(source);
		}
	}
	
	public void measurementsChanged() {
		// We notify the observers when we get data from a LofarStation
		notifyObservers();
	}
	
	// Here LofarData reads the data off a device
	// TODO: make better description because here is an essential part
	public void setMeasurements(Source source) {
		this.source = source;
		measurementsChanged();
	}
	
	public Source getSource() {
		return source;
	}
	/*
	public void setSources(Source[] sources) {
		this.sources = sources;
	}*/
}
