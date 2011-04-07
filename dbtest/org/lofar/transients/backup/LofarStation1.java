package org.lofar.data;

public class LofarStation {

	public static void main(String[] args) {
		LofarData lofarData = new LofarData();

		DatabaseStorage dbStorage = new DatabaseStorage(lofarData);
		FileSystemStorage fsStorage = new FileSystemStorage(lofarData);

		Source src = new Source();
		src.setHtmId(1234567890);
		src.setRA(123.4567890);
		src.setDec(12.34567890);
		src.setFlux(1234.567890);
		lofarData.setMeasurements(src);		
	}
}
