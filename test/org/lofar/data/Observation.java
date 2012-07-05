package org.lofar.data;

public class Observation {
	private int obsId;
	private long timeStart;
	private long timeEnd;

	public int getObsId() {
		return obsId;
	}

	public long getTimeStart() {
		return timeStart;
	}

	public long getTimeEnd() {
		return timeEnd;
	}

	public void setObsId(int obsId) {
		this.obsId = obsId;
	}

	public void setTimeStart(long timeStart) {
		this.timeStart = timeStart;
	}

	public void setTimeEnd(long timeEnd) {
		this.timeEnd = timeEnd;
	}

}
