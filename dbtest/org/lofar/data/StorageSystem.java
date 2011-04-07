package org.lofar.data;

public abstract class StorageSystem {
	
	StoreBehavior storeBehavior;
	//RetrieveBehavior retrieveBehavior;

	public abstract void display();

	public void performStore(Source src) {
		storeBehavior.store(src);
	}

	//public void performRetrieve() {
	//	retrieveBehavior.retrieve();
	//}

	public void setStoreBehavior(StoreBehavior sb) {
		storeBehavior = sb;
	}

	//public void setRetrieveBehavior(RetrieveBehavior rb) {
	//	retrieveBehavior = rb;
	//}

	public void getInfo() {
		System.out.println("Info");
	}
}
