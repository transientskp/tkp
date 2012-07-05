package org.lofar.data;

import java.util.ArrayList;

import org.lofar.util.Observer;
import org.lofar.util.Subject;

public class LofarData implements Subject {

	private ArrayList<Observer> observers;
	private Source source;
	private Source[] sources;
	
	public LofarData() {
		observers = new ArrayList<Observer>();
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
	// What that device is, is not yet clear. But for now
	// we read the source that is coming in.
	// TODO: make better description because here is an essential part
	public void setMeasurements(Source source) {
		this.source = source;
		measurementsChanged();
	}

	//public void setMeasurements(Source[] sources) {
	//	this.sources = sources;
	//	measurementsChanged();
	//}
	
	public Source getSource() {
		return source;
	}
	
	public Source[] getSources() {
		return sources;
	}
}
