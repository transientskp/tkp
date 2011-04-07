package org.lofar.util;

public interface Storage {

	public void store();

	public boolean sourceIsNew();

	public boolean sourceIsKnown();

	public boolean fluxHasChanged();

}
	
