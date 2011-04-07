package org.lofar.data;

public class StoreSimulator {

	public static void main(String[] args) {
		StorageSystem s = new DatabaseSystem();
		s.performStore();
		StorageSystem model = new ModelSystem();
		model.setStoreBehavior(new StoreInFile());
		model.performStore();
	}

}
